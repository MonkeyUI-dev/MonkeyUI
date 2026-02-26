import secrets
import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


class UserManager(BaseUserManager):
    """
    Custom user manager where email is the unique identifier
    for authentication instead of username.
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """
    Custom user model that uses email as the unique identifier
    instead of username.
    """
    email = models.EmailField(
        _('Email address'),
        unique=True,
        error_messages={
            'unique': _('A user with that email already exists.'),
        },
    )
    name = models.CharField(
        _('Name'),
        max_length=150,
        blank=True,
    )
    is_staff = models.BooleanField(
        _('Staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('Active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """
        Return the name for the user.
        """
        return self.name or self.email
    
    def get_short_name(self):
        """
        Return the short name for the user.
        """
        return self.name or self.email.split('@')[0]


class UserAPIKey(TimeStampedModel):
    """
    User-level API key for MCP and external integrations.

    Each user can have multiple API keys for different purposes
    (e.g., different projects, different tools like Cursor, Claude Desktop).

    Usage:
        - MCP authentication: Use API key in Authorization header
        - External integrations: Third-party tools can use this key
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='api_keys',
        verbose_name=_('User'),
        help_text=_('User who owns this API key')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('Name'),
        help_text=_("Friendly name for this API key (e.g., 'Cursor MCP', 'Claude Desktop')")
    )
    key = models.CharField(
        max_length=64,
        unique=True,
        verbose_name=_('API Key'),
        help_text=_('The actual API key value')
    )
    # Store prefix for display (e.g., "mk_abc...xyz")
    key_prefix = models.CharField(
        max_length=12,
        blank=True,
        verbose_name=_('Key Prefix'),
        help_text=_('First few characters of the key for identification')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is Active'),
        help_text=_('Whether this API key is currently active')
    )
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Last Used At'),
        help_text=_('Timestamp when this key was last used')
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Expires At'),
        help_text=_('Optional expiration date for the key')
    )

    class Meta:
        verbose_name = _('User API Key')
        verbose_name_plural = _('User API Keys')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['key']),
            models.Index(fields=['user', 'is_active']),
        ]

    def __str__(self):
        return f'{self.name} ({self.key_prefix}...)'

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        if not self.key_prefix:
            self.key_prefix = self.key[:8]
        super().save(*args, **kwargs)

    @staticmethod
    def generate_key():
        """Generate a secure random API key with 'mk_' prefix."""
        return f'sk_{secrets.token_urlsafe(32)}'

    def is_valid(self):
        """Check if the API key is valid (active and not expired)."""
        from django.utils import timezone

        if not self.is_active:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True

    def update_last_used(self):
        """Update the last_used_at timestamp."""
        from django.utils import timezone

        self.last_used_at = timezone.now()
        self.save(update_fields=['last_used_at'])


class UserLLMConfig(TimeStampedModel):
    """
    Per-user LLM provider configuration.

    Each user can configure one entry per provider with their own API key.
    API keys are encrypted at rest using Fernet symmetric encryption.
    """

    PROVIDER_CHOICES = [
        ('gemini', _('Gemini')),
        ('openrouter', _('OpenRouter')),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='llm_configs',
        verbose_name=_('User'),
        help_text=_('User who owns this LLM configuration')
    )
    provider = models.CharField(
        max_length=20,
        choices=PROVIDER_CHOICES,
        verbose_name=_('Provider'),
        help_text=_('LLM provider name')
    )
    api_key_encrypted = models.TextField(
        verbose_name=_('Encrypted API key'),
        help_text=_('Fernet-encrypted API key')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is Active'),
        help_text=_('Whether this provider configuration is active')
    )

    class Meta:
        verbose_name = _('User LLM configuration')
        verbose_name_plural = _('User LLM configurations')
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'provider'],
                name='unique_user_provider'
            )
        ]

    def __str__(self):
        return f'{self.user.email} - {self.get_provider_display()}'

    def set_api_key(self, plaintext_key: str):
        """Encrypt and store the API key."""
        from .encryption import encrypt_value
        self.api_key_encrypted = encrypt_value(plaintext_key)

    def get_api_key(self) -> str:
        """Decrypt and return the API key."""
        from .encryption import decrypt_value
        return decrypt_value(self.api_key_encrypted)
