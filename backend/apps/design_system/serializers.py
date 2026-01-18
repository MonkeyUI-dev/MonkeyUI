"""
Serializers for design system generation API.
"""
import base64
import uuid
from django.core.files.base import ContentFile
from rest_framework import serializers

from .models import DesignSystem, DesignSystemImage, DesignSystemStatus


# =============================================================================
# Design System CRUD Serializers
# =============================================================================

class DesignSystemImageSerializer(serializers.ModelSerializer):
    """Serializer for design system images."""
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = DesignSystemImage
        fields = ['id', 'name', 'url', 'mime_type', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_url(self, obj):
        """Get the full URL for the image."""
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class DesignSystemListSerializer(serializers.ModelSerializer):
    """Serializer for listing design systems (minimal fields)."""
    initial = serializers.SerializerMethodField()
    primary_color = serializers.SerializerMethodField()
    has_image = serializers.SerializerMethodField()
    
    class Meta:
        model = DesignSystem
        fields = [
            'id', 'name', 'description', 'status', 
            'initial', 'primary_color', 'has_image',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_initial(self, obj):
        return obj.get_initial()
    
    def get_primary_color(self, obj):
        return obj.get_primary_color()
    
    def get_has_image(self, obj):
        return hasattr(obj, 'image')


class DesignSystemDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed design system view."""
    image = DesignSystemImageSerializer(read_only=True)
    initial = serializers.SerializerMethodField()
    primary_color = serializers.SerializerMethodField()
    
    class Meta:
        model = DesignSystem
        fields = [
            'id', 'name', 'description', 'status',
            'design_tokens', 'task_id', 'analysis_error', 'analyzed_at',
            'image', 'initial', 'primary_color',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'design_tokens', 'task_id', 'analysis_error', 'analyzed_at',
            'created_at', 'updated_at'
        ]
    
    def get_initial(self, obj):
        return obj.get_initial()
    
    def get_primary_color(self, obj):
        return obj.get_primary_color()


class DesignSystemCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a design system."""
    
    class Meta:
        model = DesignSystem
        fields = ['name', 'description']
    
    def create(self, validated_data):
        user = self.context['request'].user
        return DesignSystem.objects.create(user=user, **validated_data)


class DesignSystemUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a design system."""
    
    class Meta:
        model = DesignSystem
        fields = ['name', 'description', 'design_tokens']


class ImageUploadSerializer(serializers.Serializer):
    """Serializer for uploading base64 images."""
    data = serializers.CharField(help_text="Base64 encoded image data")
    mime_type = serializers.CharField(
        default="image/png",
        help_text="MIME type of the image"
    )
    name = serializers.CharField(
        required=False,
        allow_blank=True,
        default='',
        help_text="Original filename"
    )
    
    def create_image(self, design_system):
        """Create a DesignSystemImage from base64 data (one-to-one relationship)."""
        data = self.validated_data['data']
        mime_type = self.validated_data['mime_type']
        name = self.validated_data.get('name', '')
        
        # Decode base64
        try:
            # Remove data URL prefix if present
            if ',' in data:
                data = data.split(',')[1]
            image_data = base64.b64decode(data)
        except Exception as e:
            raise serializers.ValidationError(f"Invalid base64 data: {str(e)}")
        
        # Create file
        ext = mime_type.split('/')[-1] if '/' in mime_type else 'png'
        filename = name or f"image_{uuid.uuid4().hex[:8]}.{ext}"
        
        image_file = ContentFile(image_data, name=filename)
        
        return DesignSystemImage.objects.create(
            design_system=design_system,
            name=filename,
            image=image_file,
            mime_type=mime_type
        )


class StartAnalysisSerializer(serializers.Serializer):
    """Serializer for starting design system analysis."""
    provider = serializers.ChoiceField(
        choices=['openai', 'gemini', 'openrouter', 'qwen', 'kimi'],
        required=False,
        allow_null=True,
        help_text="LLM provider to use. If not specified, uses default provider."
    )
    images = ImageUploadSerializer(
        many=True,
        required=False,
        help_text="Optional new image to add before analysis (replaces existing image)"
    )
    
    def validate_images(self, value):
        if value and len(value) > 1:
            raise serializers.ValidationError("Only one image allowed per design system.")
        return value


# =============================================================================
# Legacy Serializers (for existing API compatibility)
# =============================================================================

class ImageDataSerializer(serializers.Serializer):
    """Serializer for image data in design system generation request."""
    data = serializers.CharField(
        help_text="Base64 encoded image data"
    )
    mime_type = serializers.CharField(
        default="image/png",
        help_text="MIME type of the image (e.g., image/png, image/jpeg)"
    )
    name = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Original filename"
    )


class GenerateDesignSystemRequestSerializer(serializers.Serializer):
    """Serializer for design system generation request."""
    images = ImageDataSerializer(
        many=True,
        help_text="List of images to analyze"
    )
    provider = serializers.ChoiceField(
        choices=['openai', 'gemini', 'openrouter', 'qwen', 'kimi'],
        required=False,
        allow_null=True,
        help_text="LLM provider to use. If not specified, uses default provider."
    )
    vibe_name = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        help_text="Name of the vibe/design system"
    )
    vibe_description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Description of the desired style"
    )

    def validate_images(self, value):
        """Validate that at least one image is provided."""
        if not value:
            raise serializers.ValidationError("At least one image is required.")
        if len(value) > 10:
            raise serializers.ValidationError("Maximum 10 images allowed per request.")
        return value


class TaskStatusResponseSerializer(serializers.Serializer):
    """Serializer for task status response."""
    task_id = serializers.CharField(help_text="Unique task identifier")
    status = serializers.ChoiceField(
        choices=['pending', 'processing', 'completed', 'failed'],
        help_text="Current task status"
    )
    progress = serializers.IntegerField(
        min_value=0,
        max_value=100,
        help_text="Progress percentage (0-100)"
    )
    current_step = serializers.CharField(help_text="Current processing step")
    current_step_number = serializers.IntegerField(help_text="Current step number")
    total_steps = serializers.IntegerField(help_text="Total number of steps")
    message = serializers.CharField(help_text="User-friendly status message")
    result = serializers.JSONField(
        required=False,
        allow_null=True,
        help_text="Result data when completed"
    )
    error = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Error message if failed"
    )


class CreateTaskResponseSerializer(serializers.Serializer):
    """Serializer for create task response."""
    task_id = serializers.CharField(help_text="Unique task identifier for tracking")
    message = serializers.CharField(help_text="Status message")


class DesignSystemColorsSerializer(serializers.Serializer):
    """Serializer for design system colors."""
    primary = serializers.CharField(required=False, help_text="Primary brand color")
    secondary = serializers.CharField(required=False, help_text="Secondary accent color")
    background = serializers.CharField(required=False, help_text="Page background color")
    surface = serializers.CharField(required=False, help_text="Card/container surface color")
    textPrimary = serializers.CharField(required=False, help_text="Main text color")
    textSecondary = serializers.CharField(required=False, help_text="Secondary text color")
    textTertiary = serializers.CharField(required=False, help_text="Tertiary text color")
    border = serializers.CharField(required=False, help_text="Border/divider color")
    success = serializers.CharField(required=False, help_text="Success state color")
    warning = serializers.CharField(required=False, help_text="Warning state color")
    error = serializers.CharField(required=False, help_text="Error state color")


class DesignSystemTypographySerializer(serializers.Serializer):
    """Serializer for design system typography."""
    fontFamily = serializers.CharField(required=False, help_text="Primary font family")
    fontFamilyHeading = serializers.CharField(required=False, help_text="Heading font family")
    baseFontSize = serializers.CharField(required=False, help_text="Base font size")
    fontWeightRegular = serializers.IntegerField(required=False, help_text="Regular font weight")
    fontWeightMedium = serializers.IntegerField(required=False, help_text="Medium font weight")
    fontWeightBold = serializers.IntegerField(required=False, help_text="Bold font weight")
    lineHeightBase = serializers.FloatField(required=False, help_text="Base line height")
    lineHeightHeading = serializers.FloatField(required=False, help_text="Heading line height")


class DesignSystemSpacingSerializer(serializers.Serializer):
    """Serializer for design system spacing."""
    unit = serializers.IntegerField(required=False, help_text="Base spacing unit in pixels")
    scale = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="Spacing scale values"
    )


class DesignSystemBorderRadiusSerializer(serializers.Serializer):
    """Serializer for design system border radius."""
    small = serializers.CharField(required=False, help_text="Small border radius")
    medium = serializers.CharField(required=False, help_text="Medium border radius")
    large = serializers.CharField(required=False, help_text="Large border radius")
    full = serializers.CharField(required=False, help_text="Full/pill border radius")


class DesignSystemShadowsSerializer(serializers.Serializer):
    """Serializer for design system shadows."""
    level1 = serializers.CharField(required=False, help_text="Level 1 shadow")
    level2 = serializers.CharField(required=False, help_text="Level 2 shadow")
    level3 = serializers.CharField(required=False, help_text="Level 3 shadow")


class DesignSystemVisualEffectsSerializer(serializers.Serializer):
    """Serializer for design system visual effects."""
    hasGlassmorphism = serializers.BooleanField(required=False)
    hasGradients = serializers.BooleanField(required=False)
    gradientStyle = serializers.CharField(required=False, allow_blank=True)
    hasAnimations = serializers.BooleanField(required=False)
    backdropBlur = serializers.CharField(required=False, allow_blank=True)


class DesignSystemMetadataSerializer(serializers.Serializer):
    """Serializer for design system metadata."""
    name = serializers.CharField(help_text="Design system name")
    description = serializers.CharField(required=False, allow_blank=True)
    provider = serializers.CharField(required=False, help_text="LLM provider used")
    model = serializers.CharField(required=False, help_text="LLM model used")
    images_analyzed = serializers.IntegerField(required=False)
    generated_at = serializers.CharField(required=False)


class DesignSystemResponseSerializer(serializers.Serializer):
    """Serializer for complete design system response."""
    styleName = serializers.CharField(required=False, help_text="Style name")
    styleDescription = serializers.CharField(required=False, help_text="Style description")
    colors = DesignSystemColorsSerializer(required=False)
    typography = DesignSystemTypographySerializer(required=False)
    spacing = DesignSystemSpacingSerializer(required=False)
    borderRadius = DesignSystemBorderRadiusSerializer(required=False)
    shadows = DesignSystemShadowsSerializer(required=False)
    visualEffects = DesignSystemVisualEffectsSerializer(required=False)
    styleRules = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Style-specific rules"
    )
    metadata = DesignSystemMetadataSerializer(required=False)


class LLMProviderInfoSerializer(serializers.Serializer):
    """Serializer for LLM provider information."""
    type = serializers.CharField(help_text="Provider type identifier")
    model = serializers.CharField(help_text="Default model name")
    has_vision = serializers.BooleanField(help_text="Whether the provider supports vision")


class AvailableProvidersResponseSerializer(serializers.Serializer):
    """Serializer for available providers response."""
    providers = LLMProviderInfoSerializer(many=True)
    default_provider = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Default provider type"
    )
