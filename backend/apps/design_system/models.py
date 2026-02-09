"""Django models for design system management.

This module provides the data models for storing design systems,
their analysis results, and source images.
"""
import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


class DesignSystemStatus(models.TextChoices):
    """Status choices for design system analysis."""

    PENDING = 'pending', _('Pending Analysis')
    PROCESSING = 'processing', _('Processing')
    COMPLETED = 'completed', _('Completed')
    FAILED = 'failed', _('Failed')


class DesignSystem(TimeStampedModel):
    """
    Model representing a user's design system.
    
    A design system contains:
    - Basic info (name, description)
    - Source images used for analysis
    - Analysis results (design tokens: colors, typography, spacing, etc.)
    - Status of the analysis process
    - MCP enablement flag (authentication via UserAPIKey)
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique identifier for the design system")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='design_systems',
        verbose_name=_("Owner"),
        help_text=_("User who owns this design system")
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Name"),
        help_text=_("Name of the design system")
    )
    description = models.TextField(
        blank=True,
        default='',
        verbose_name=_("Description"),
        help_text=_("Description of the design system")
    )
    status = models.CharField(
        max_length=20,
        choices=DesignSystemStatus.choices,
        default=DesignSystemStatus.PENDING,
        verbose_name=_("Status"),
        help_text=_("Current status of the design system analysis")
    )
    
    # Analysis result - stored as JSON
    design_tokens = models.JSONField(
        null=True,
        blank=True,
        default=dict,
        verbose_name=_("Design Tokens"),
        help_text=_("Generated design tokens: colors, typography, spacing, shadows, etc.")
    )
    aesthetic_analysis = models.TextField(
        blank=True,
        default='',
        verbose_name=_("Aesthetic Analysis"),
        help_text=_("LLM-generated aesthetic analysis in Markdown format: design soul invariants, variation knobs, and anti-patterns")
    )
    
    # Task tracking
    task_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Task ID"),
        help_text=_("Celery task ID for tracking analysis progress")
    )
    analysis_error = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Analysis Error"),
        help_text=_("Error message if analysis failed")
    )
    analyzed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Analyzed At"),
        help_text=_("Timestamp when analysis was completed")
    )

    class Meta:
        verbose_name = _("Design System")
        verbose_name_plural = _("Design Systems")
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.name} ({self.user.email})"

    def get_primary_color(self):
        """Get the primary color from design tokens."""
        if self.design_tokens and 'colors' in self.design_tokens:
            return self.design_tokens['colors'].get('primary', '#2A99D3')
        return '#2A99D3'

    def get_initial(self):
        """Get the first character of the name for avatar."""
        return self.name[0].upper() if self.name else 'D'


def design_system_image_path(instance, filename):
    """
    Generate upload path for design system images.
    
    Structure: design_systems/<user_id>/<design_system_id>/<filename>
    This groups images by user and design system for easier management.
    """
    return f"design_systems/{instance.design_system.user_id}/{instance.design_system_id}/{filename}"


class DesignSystemImage(TimeStampedModel):
    """
    Model representing the source image for a design system.
    
    One-to-one relationship: Each design system has exactly one reference image.
    This image is used as input for LLM analysis to extract design tokens.
    
    Storage backend is configured via Django's DEFAULT_FILE_STORAGE setting:
    - Local: django.core.files.storage.FileSystemStorage
    - S3: storages.backends.s3boto3.S3Boto3Storage (django-storages)
    
    To use S3, install django-storages[s3] and configure in settings:
        DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
        AWS_ACCESS_KEY_ID = 'your-key'
        AWS_SECRET_ACCESS_KEY = 'your-secret'
        AWS_STORAGE_BUCKET_NAME = 'your-bucket'
        AWS_S3_REGION_NAME = 'us-east-1'
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    design_system = models.OneToOneField(
        DesignSystem,
        on_delete=models.CASCADE,
        related_name='image',
        verbose_name=_("Design System"),
        help_text=_("Design system this image belongs to")
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name=_("Filename"),
        help_text=_("Original filename of the image")
    )
    image = models.ImageField(
        upload_to=design_system_image_path,
        verbose_name=_("Image"),
        help_text=_("Uploaded image file (supports local storage or S3)")
    )
    mime_type = models.CharField(
        max_length=50,
        default='image/png',
        verbose_name=_("MIME Type"),
        help_text=_("MIME type of the image")
    )
    file_size = models.PositiveIntegerField(
        default=0,
        verbose_name=_("File Size"),
        help_text=_("File size in bytes")
    )

    class Meta:
        verbose_name = _("Design System Image")
        verbose_name_plural = _("Design System Images")
        ordering = ['created_at']

    def __str__(self):
        return f"{self.name} - {self.design_system.name}"

    def save(self, *args, **kwargs):
        """Auto-populate file metadata on save."""
        if self.image and hasattr(self.image, 'size'):
            self.file_size = self.image.size
        super().save(*args, **kwargs)
