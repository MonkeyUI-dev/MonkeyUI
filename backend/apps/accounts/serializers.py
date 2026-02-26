from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import UserAPIKey, UserLLMConfig

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user model.
    """
    
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)
    name = serializers.CharField(required=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'name']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": _("Password fields didn't match.")
            })
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data.get('name', '')
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password]
    )


class UserAPIKeySerializer(serializers.ModelSerializer):
    """
    Serializer for UserAPIKey model.
    Returns masked key for security (except on creation).
    """
    key = serializers.CharField(read_only=True)
    key_display = serializers.SerializerMethodField()
    
    class Meta:
        model = UserAPIKey
        fields = [
            'id', 'name', 'key', 'key_display', 'key_prefix',
            'is_active', 'last_used_at', 'expires_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'key', 'key_prefix', 'last_used_at',
            'created_at', 'updated_at'
        ]
    
    def get_key_display(self, obj):
        """Return masked key for display."""
        return f"{obj.key_prefix}..." if obj.key_prefix else "***..."
    
    def to_representation(self, instance):
        """Customize representation to show full key only on creation."""
        representation = super().to_representation(instance)
        # Only show full key when it's being created (context from view)
        if not self.context.get('show_full_key', False):
            representation.pop('key', None)
        return representation


class CreateUserAPIKeySerializer(serializers.ModelSerializer):
    """
    Serializer for creating UserAPIKey.
    Returns full key value only once on creation.
    """
    
    class Meta:
        model = UserAPIKey
        fields = ['id', 'name', 'key', 'key_prefix', 'expires_at', 'created_at']
        read_only_fields = ['id', 'key', 'key_prefix', 'created_at']


class UserLLMConfigSerializer(serializers.ModelSerializer):
    """
    Serializer for UserLLMConfig.
    Accepts a plaintext ``api_key`` on write and returns a masked
    version on read.  The actual encrypted blob is never exposed.
    """

    api_key = serializers.CharField(
        write_only=True,
        required=True,
        help_text=_('Plaintext API key (write-only)')
    )
    api_key_display = serializers.SerializerMethodField()
    provider_display = serializers.CharField(
        source='get_provider_display',
        read_only=True
    )

    class Meta:
        model = UserLLMConfig
        fields = [
            'id', 'provider', 'provider_display',
            'api_key', 'api_key_display',
            'is_active', 'is_default', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_api_key_display(self, obj):
        """Return a masked version of the API key."""
        try:
            key = obj.get_api_key()
            if len(key) > 8:
                return f"{key[:4]}{'*' * (len(key) - 8)}{key[-4:]}"
            return '****'
        except Exception:
            return '****'

    def validate(self, attrs):
        # On create, check uniqueness of (user, provider)
        if self.instance is None:
            user = self.context['request'].user
            provider = attrs.get('provider')
            if UserLLMConfig.objects.filter(user=user, provider=provider).exists():
                raise serializers.ValidationError({
                    'provider': _('A configuration for this provider already exists.')
                })
        return attrs

    def create(self, validated_data):
        api_key = validated_data.pop('api_key')
        instance = UserLLMConfig(**validated_data)
        instance.set_api_key(api_key)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        api_key = validated_data.pop('api_key', None)
        if api_key:
            instance.set_api_key(api_key)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
