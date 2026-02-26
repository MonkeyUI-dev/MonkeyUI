"""
LLM Provider configuration management.

This module handles loading and managing LLM provider configurations
from Django settings or environment variables.

Supported providers:
- Gemini (direct Google API)
- OpenRouter (with Gemini 3 Pro and reasoning capabilities)
"""
import os
from django.conf import settings
from typing import Optional
from .providers import LLMConfig, LLMProviderType


# Default model configurations for each provider
DEFAULT_MODELS = {
    LLMProviderType.GEMINI: "gemini-3-pro-preview",
    LLMProviderType.OPENROUTER: "google/gemini-3-pro-preview",
}

# Vision-capable models for each provider
VISION_MODELS = {
    LLMProviderType.GEMINI: "gemini-3-pro-preview",
    LLMProviderType.OPENROUTER: "google/gemini-3-pro-preview",
}


def get_provider_config(
    provider_type: LLMProviderType,
    for_vision: bool = False,
    user=None
) -> Optional[LLMConfig]:
    """
    Get LLM provider configuration from Django settings or environment variables.
    
    Configuration priority:
    1. Per-user configuration (UserLLMConfig) when a user is provided
    2. Django settings (LLM_PROVIDERS dict)
    3. Environment variables (e.g., OPENAI_API_KEY, GEMINI_API_KEY)
    
    Args:
        provider_type: The type of LLM provider
        for_vision: If True, use vision-capable model
        user: Optional user instance to check per-user config first
        
    Returns:
        LLMConfig if configuration is available, None otherwise
    """
    api_key = None

    # 1. Try per-user configuration
    if user is not None:
        try:
            from apps.accounts.models import UserLLMConfig
            user_config = UserLLMConfig.objects.filter(
                user=user,
                provider=provider_type.value,
                is_active=True
            ).first()
            if user_config:
                api_key = user_config.get_api_key()
        except Exception:
            pass

    # 2. Try Django settings / env vars as fallback
    llm_settings = getattr(settings, 'LLM_PROVIDERS', {})
    provider_settings = llm_settings.get(provider_type.value, {})

    env_key_mapping = {
        LLMProviderType.GEMINI: 'GEMINI_API_KEY',
        LLMProviderType.OPENROUTER: 'OPENROUTER_API_KEY',
    }

    if not api_key:
        api_key = provider_settings.get('api_key') or os.getenv(env_key_mapping.get(provider_type, ''))
    
    if not api_key:
        return None
    
    # Select model (vision or default)
    model_dict = VISION_MODELS if for_vision else DEFAULT_MODELS
    model = provider_settings.get('model') or model_dict.get(provider_type)
    
    # Enable reasoning by default for OpenRouter
    enable_reasoning = provider_settings.get('enable_reasoning', True)
    
    return LLMConfig(
        provider_type=provider_type,
        api_key=api_key,
        model=model,
        base_url=provider_settings.get('base_url'),
        timeout=provider_settings.get('timeout', 300),
        enable_reasoning=enable_reasoning
    )


def get_default_provider(for_vision: bool = False, user=None) -> Optional[LLMConfig]:
    """
    Get the default (first available) LLM provider configuration.
    
    Priority order:
    1. OpenRouter (preferred - supports Gemini 3 Pro with reasoning)
    2. Gemini (direct API)
    
    Args:
        for_vision: If True, use vision-capable model
        user: Optional user instance to check per-user config first
        
    Returns:
        LLMConfig for the first available provider, None if none available
    """
    # Check for explicit default provider in settings
    default_provider = getattr(settings, 'DEFAULT_LLM_PROVIDER', None)
    if default_provider:
        try:
            provider_type = LLMProviderType(default_provider)
            config = get_provider_config(provider_type, for_vision, user=user)
            if config:
                return config
        except ValueError:
            pass
    
    # Try providers in priority order (OpenRouter first for Gemini 3 Pro support)
    priority_order = [
        LLMProviderType.OPENROUTER,
        LLMProviderType.GEMINI,
    ]
    
    for provider_type in priority_order:
        config = get_provider_config(provider_type, for_vision, user=user)
        if config:
            return config
    
    return None
