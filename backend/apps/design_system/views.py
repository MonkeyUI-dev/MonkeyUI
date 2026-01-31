"""
API views for design system generation and management.
"""
import logging
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.translation import gettext as _
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import DesignSystem, DesignSystemStatus
from .serializers import (
    CreateTaskResponseSerializer,
    TaskStatusResponseSerializer,
    DesignSystemListSerializer,
    DesignSystemDetailSerializer,
    DesignSystemCreateSerializer,
    DesignSystemUpdateSerializer,
    StartAnalysisSerializer,
    ImageUploadSerializer,
)
from .tasks import create_analysis_task, get_task_progress
from .llm.config import get_default_provider

logger = logging.getLogger(__name__)


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
        try:
            logger.info(f"Starting analysis for design system {pk}")
            design_system = self.get_object()
            serializer = StartAnalysisSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Add any new images first
            new_images = serializer.validated_data.get('images', [])
            logger.debug(f"Processing {len(new_images)} new images")
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
                logger.warning(f"No images found for design system {pk}")
                return Response(
                    {"error": _("No images to analyze. Please upload at least one image.")},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check LLM provider is configured
            logger.debug("Checking LLM provider configuration")
            default_config = get_default_provider(for_vision=True)
            if not default_config:
                logger.error("No LLM provider configured")
                return Response(
                    {"error": _("No LLM provider configured. Please configure at least one provider.")},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            logger.info(f"Using LLM provider: {default_config.provider_type.value}")
            
            # Create and queue the task - only pass design_system_id
            # The task will load image and other info from database
            logger.info("Creating analysis task")
            task_id = create_analysis_task(
                design_system_id=str(design_system.id)
            )
            logger.info(f"Task created with ID: {task_id}")
            
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
        except Exception as e:
            logger.exception(f"Error analyzing design system {pk}: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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


