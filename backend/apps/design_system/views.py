"""
API views for design system generation and management.
"""
import base64
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.utils.translation import gettext as _
from django.utils import timezone
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import DesignSystem, DesignSystemImage, DesignSystemStatus
from .serializers import (
    GenerateDesignSystemRequestSerializer,
    CreateTaskResponseSerializer,
    TaskStatusResponseSerializer,
    AvailableProvidersResponseSerializer,
    DesignSystemListSerializer,
    DesignSystemDetailSerializer,
    DesignSystemCreateSerializer,
    DesignSystemUpdateSerializer,
    StartAnalysisSerializer,
    ImageUploadSerializer,
)
from .tasks import create_analysis_task, get_task_progress, TaskStatus
from .llm.config import list_available_providers, get_default_provider


# =============================================================================
# Design System ViewSet (CRUD + Analysis)
# =============================================================================

class DesignSystemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing design systems.
    
    Provides CRUD operations plus:
    - Start analysis on a design system
    - Check analysis status
    - Upload images
    - Enable/disable MCP
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only the current user's design systems."""
        return DesignSystem.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return DesignSystemListSerializer
        elif self.action == 'create':
            return DesignSystemCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return DesignSystemUpdateSerializer
        return DesignSystemDetailSerializer
    
    @extend_schema(
        responses={200: DesignSystemListSerializer(many=True)},
        description="List all design systems for the authenticated user",
        tags=["Design System Management"]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        request=DesignSystemCreateSerializer,
        responses={201: DesignSystemDetailSerializer},
        description="Create a new design system",
        tags=["Design System Management"]
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        
        # Return full details
        detail_serializer = DesignSystemDetailSerializer(
            instance, 
            context={'request': request}
        )
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        responses={200: DesignSystemDetailSerializer},
        description="Get a design system by ID",
        tags=["Design System Management"]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        request=DesignSystemUpdateSerializer,
        responses={200: DesignSystemDetailSerializer},
        description="Update a design system",
        tags=["Design System Management"]
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Return full details
        detail_serializer = DesignSystemDetailSerializer(
            instance, 
            context={'request': request}
        )
        return Response(detail_serializer.data)
    
    @extend_schema(
        request=StartAnalysisSerializer,
        responses={
            202: CreateTaskResponseSerializer,
            400: OpenApiResponse(description="Invalid request or no images"),
            503: OpenApiResponse(description="No LLM provider configured"),
        },
        description="Start AI analysis on a design system",
        tags=["Design System Management"]
    )
    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """
        Start AI analysis on a design system.
        
        This queues a Celery task to analyze the design system's images
        using an LLM to extract design tokens. The analysis runs asynchronously.
        """
        design_system = self.get_object()
        serializer = StartAnalysisSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Add any new images first
        new_images = serializer.validated_data.get('images', [])
        for image_data in new_images:
            img_serializer = ImageUploadSerializer(data=image_data)
            if img_serializer.is_valid():
                # Delete existing image if any (one-to-one relationship)
                if hasattr(design_system, 'image'):
                    design_system.image.delete()
                img_serializer.create_image(design_system)
        
        # Refresh from database to get the newly created image
        design_system.refresh_from_db()
        
        # Check if design system has image
        if not hasattr(design_system, 'image'):
            return Response(
                {"error": _("No images to analyze. Please upload at least one image.")},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check LLM provider
        provider = serializer.validated_data.get('provider')
        if not provider:
            default_config = get_default_provider(for_vision=True)
            if not default_config:
                return Response(
                    {"error": _("No LLM provider configured. Please configure at least one provider.")},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
        
        # Prepare image data for the task
        image_data_list = []
        img = design_system.image
        with img.image.open('rb') as f:
            image_bytes = f.read()
            image_data_list.append({
                'data': base64.b64encode(image_bytes).decode('utf-8'),
                'mime_type': img.mime_type,
                'name': img.name
            })
        
        # Create and queue the task
        task_id = create_analysis_task(
            images=image_data_list,
            provider_type=provider,
            vibe_name=design_system.name,
            vibe_description=design_system.description,
            design_system_id=str(design_system.id)
        )
        
        # Update design system status
        design_system.status = DesignSystemStatus.PENDING
        design_system.task_id = task_id
        design_system.analysis_error = None
        design_system.save(update_fields=['status', 'task_id', 'analysis_error', 'updated_at'])
        
        return Response(
            {
                "task_id": task_id,
                "message": _("Design system analysis started. Use the task_id to track progress.")
            },
            status=status.HTTP_202_ACCEPTED
        )
    
    @extend_schema(
        responses={200: TaskStatusResponseSerializer},
        description="Get the analysis status for a design system",
        tags=["Design System Management"]
    )
    @action(detail=True, methods=['get'])
    def analysis_status(self, request, pk=None):
        """Get the current analysis status for a design system."""
        design_system = self.get_object()
        
        if not design_system.task_id:
            return Response({
                "status": design_system.status,
                "message": _("No analysis has been started for this design system.")
            })
        
        progress = get_task_progress(design_system.task_id)
        
        if not progress:
            # Task expired from cache, use DB status
            return Response({
                "task_id": design_system.task_id,
                "status": design_system.status,
                "progress": 100 if design_system.status == DesignSystemStatus.COMPLETED else 0,
                "current_step": "completed" if design_system.status == DesignSystemStatus.COMPLETED else "unknown",
                "current_step_number": 1,
                "total_steps": 1,
                "message": _("Analysis completed") if design_system.status == DesignSystemStatus.COMPLETED else _("Status unknown"),
                "result": design_system.design_tokens if design_system.status == DesignSystemStatus.COMPLETED else None,
                "error": design_system.analysis_error
            })
        
        return Response(progress)
    
    @extend_schema(
        request=ImageUploadSerializer(many=True),
        responses={201: OpenApiResponse(description="Images uploaded successfully")},
        description="Upload images to a design system",
        tags=["Design System Management"]
    )
    @action(detail=True, methods=['post'])
    def upload_images(self, request, pk=None):
        """Upload image to a design system (replaces existing image if any)."""
        design_system = self.get_object()
        
        images_data = request.data.get('images', [])
        if not images_data:
            return Response(
                {"error": _("No images provided.")},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Only accept one image (one-to-one relationship)
        if len(images_data) > 1:
            return Response(
                {"error": _("Only one image allowed per design system.")},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Delete existing image if any
        if hasattr(design_system, 'image'):
            design_system.image.delete()
        
        image_data = images_data[0]
        serializer = ImageUploadSerializer(data=image_data)
        if serializer.is_valid():
            img = serializer.create_image(design_system)
            return Response({
                "message": _("Image uploaded successfully"),
                "uploaded": {
                    'id': str(img.id),
                    'name': img.name
                }
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @extend_schema(
        responses={200: OpenApiResponse(description="Image deleted successfully")},
        description="Delete an image from a design system",
        tags=["Design System Management"]
    )
    @action(detail=True, methods=['delete'], url_path='images/(?P<image_id>[^/.]+)')
    def delete_image(self, request, pk=None, image_id=None):
        """Delete the image from a design system."""
        design_system = self.get_object()
        
        if not hasattr(design_system, 'image'):
            return Response(
                {"error": _("No image found")},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if str(design_system.image.id) != image_id:
            return Response(
                {"error": _("Image ID does not match")},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        design_system.image.delete()
        return Response({
            "message": _("Image deleted successfully")
        })
    
    # TODO: MCP toggle functionality - requires mcp_enabled and mcp_api_key fields in model
    # @extend_schema(
    #     responses={200: OpenApiResponse(description="MCP configuration updated")},
    #     description="Toggle MCP exposure for a design system",
    #     tags=["Design System Management"]
    # )
    # @action(detail=True, methods=['post'])
    # def toggle_mcp(self, request, pk=None):
    #     """Enable or disable MCP exposure for a design system."""
    #     import secrets
    #     design_system = self.get_object()
    #     
    #     # Toggle MCP status
    #     design_system.mcp_enabled = not design_system.mcp_enabled
    #     
    #     # Generate API key if enabling and none exists
    #     if design_system.mcp_enabled and not design_system.mcp_api_key:
    #         design_system.mcp_api_key = secrets.token_urlsafe(32)
    #     
    #     design_system.save(update_fields=['mcp_enabled', 'mcp_api_key', 'updated_at'])
    #     
    #     return Response({
    #         "mcp_enabled": design_system.mcp_enabled,
    #         "mcp_api_key": design_system.mcp_api_key if design_system.mcp_enabled else None,
    #         "message": _("MCP enabled") if design_system.mcp_enabled else _("MCP disabled")
    #     })


# =============================================================================
# Legacy API Views (for backward compatibility)
# =============================================================================

@extend_schema(
    request=GenerateDesignSystemRequestSerializer,
    responses={
        202: CreateTaskResponseSerializer,
        400: OpenApiResponse(description="Invalid request data"),
        503: OpenApiResponse(description="No LLM provider configured"),
    },
    description="Start async design system generation from uploaded images",
    tags=["Design System"]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def generate_design_system(request):
    """
    Start an async task to generate a design system from uploaded images.
    
    This endpoint queues a Celery task that analyzes the provided images
    using an LLM to extract design system tokens. The frontend can poll
    the task status endpoint to track progress.
    
    Returns a task_id that can be used to track progress and retrieve results.
    """
    serializer = GenerateDesignSystemRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if any LLM provider is available
    provider = serializer.validated_data.get('provider')
    if not provider:
        default_config = get_default_provider(for_vision=True)
        if not default_config:
            return Response(
                {"error": _("No LLM provider configured. Please configure at least one provider.")},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
    
    # Create and queue the task
    task_id = create_analysis_task(
        images=serializer.validated_data['images'],
        provider_type=provider,
        vibe_name=serializer.validated_data.get('vibe_name'),
        vibe_description=serializer.validated_data.get('vibe_description')
    )
    
    return Response(
        {
            "task_id": task_id,
            "message": _("Design system generation started. Use the task_id to track progress.")
        },
        status=status.HTTP_202_ACCEPTED
    )


@extend_schema(
    responses={
        200: TaskStatusResponseSerializer,
        404: OpenApiResponse(description="Task not found"),
    },
    description="Get the status and progress of a design system generation task",
    tags=["Design System"]
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_task_status(request, task_id: str):
    """
    Get the status and progress of a design system generation task.
    
    The frontend can poll this endpoint to track progress and retrieve
    the final result when the task is completed.
    
    Returns:
        - status: pending | processing | completed | failed
        - progress: 0-100 percentage
        - current_step: Description of current processing step
        - message: User-friendly status message
        - result: Design system data (when completed)
        - error: Error message (if failed)
    """
    progress = get_task_progress(task_id)
    
    if not progress:
        return Response(
            {"error": _("Task not found or expired")},
            status=status.HTTP_404_NOT_FOUND
        )
    
    return Response(progress)


@extend_schema(
    responses={
        200: AvailableProvidersResponseSerializer,
    },
    description="List all available (configured) LLM providers",
    tags=["Design System"]
)
@api_view(['GET'])
@permission_classes([AllowAny])
def list_providers(request):
    """
    List all available (configured) LLM providers.
    
    Returns information about which providers are configured and available
    for use in design system generation.
    """
    providers = list_available_providers()
    default_config = get_default_provider(for_vision=True)
    
    return Response({
        "providers": providers,
        "default_provider": default_config.provider_type.value if default_config else None
    })


@extend_schema(
    responses={
        200: OpenApiResponse(description="Task cancelled successfully"),
        404: OpenApiResponse(description="Task not found"),
    },
    description="Cancel a running design system generation task",
    tags=["Design System"]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def cancel_task(request, task_id: str):
    """
    Cancel a running design system generation task.
    
    Note: This only marks the task as cancelled in the cache.
    The actual Celery task may still run to completion.
    """
    from django.core.cache import cache
    from .tasks import get_task_cache_key, update_task_progress
    
    progress = get_task_progress(task_id)
    
    if not progress:
        return Response(
            {"error": _("Task not found or expired")},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Only cancel if not already completed/failed
    if progress['status'] in [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value]:
        return Response(
            {"error": _("Task already finished, cannot cancel")},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Mark as failed/cancelled
    update_task_progress(
        task_id=task_id,
        status=TaskStatus.FAILED,
        progress=0,
        current_step="cancelled",
        current_step_number=0,
        total_steps=progress['total_steps'],
        message=_("Task cancelled by user"),
        error=_("Cancelled")
    )
    
    return Response({
        "message": _("Task cancelled successfully")
    })
