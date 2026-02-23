"""
LLM Provider abstraction layer.

This module provides a unified interface for interacting with LLM providers.
Currently supports:
- Gemini (direct Google API)
- OpenRouter (with Gemini 3 Pro support and reasoning capabilities)
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Any
import base64
import logging

logger = logging.getLogger(__name__)


class LLMProviderType(str, Enum):
    """Supported LLM provider types."""
    GEMINI = "gemini"
    OPENROUTER = "openrouter"


@dataclass
class LLMConfig:
    """Configuration for an LLM provider."""
    provider_type: LLMProviderType
    api_key: str
    model: str
    base_url: Optional[str] = None
    timeout: int = 300  # seconds - increased for reasoning models
    enable_reasoning: bool = True  # Enable reasoning for supported models
    structured_output: bool = False  # Enable structured output mode
    response_schema: Optional[dict] = None  # JSON schema for structured output


@dataclass
class LLMResponse:
    """Response from an LLM provider."""
    content: str
    model: str
    provider: str
    usage: dict[str, int]
    raw_response: Optional[Any] = None
    reasoning: Optional[str] = None  # Reasoning tokens if available


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self._client = None
    
    @abstractmethod
    def _initialize_client(self):
        """Initialize the provider-specific client."""
        pass
    
    @property
    def client(self):
        """Lazy initialization of the client."""
        if self._client is None:
            self._initialize_client()
        return self._client
    
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """
        Generate a completion from the LLM.
        
        Args:
            prompt: The user prompt/message
            system_prompt: Optional system prompt to set context
            
        Returns:
            LLMResponse with the generated content
        """
        pass
    
    @abstractmethod
    async def generate_with_image(
        self, 
        prompt: str, 
        image_data: bytes,
        image_mime_type: str = "image/png",
        system_prompt: Optional[str] = None
    ) -> LLMResponse:
        """
        Generate a completion with image input (for vision models).
        
        Args:
            prompt: The user prompt/message
            image_data: Raw image bytes
            image_mime_type: MIME type of the image
            system_prompt: Optional system prompt
            
        Returns:
            LLMResponse with the generated content
        """
        pass

    def _encode_image_base64(self, image_data: bytes) -> str:
        """Encode image data to base64 string."""
        return base64.b64encode(image_data).decode('utf-8')


class GeminiProvider(BaseLLMProvider):
    """Google Gemini API provider (direct API access) with thinking mode and structured output support."""
    
    def _initialize_client(self):
        import google.generativeai as genai
        genai.configure(api_key=self.config.api_key)
        self._client = genai.GenerativeModel(self.config.model)
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        generation_config = {"temperature": 0.1}
        
        # Enable thinking mode for supported models (Gemini 2.0 Flash Thinking)
        if self.config.enable_reasoning:
            generation_config["thought"] = True
        
        # Add structured output config if enabled
        if self.config.structured_output and self.config.response_schema:
            generation_config["response_mime_type"] = "application/json"
            generation_config["response_schema"] = self.config.response_schema
        
        response = await self.client.generate_content_async(
            full_prompt,
            generation_config=generation_config
        )
        
        return LLMResponse(
            content=response.text,
            model=self.config.model,
            provider=LLMProviderType.GEMINI.value,
            usage={
                "prompt_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0,
                "completion_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0,
                "total_tokens": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
            },
            raw_response=response
        )
    
    async def generate_with_image(
        self, 
        prompt: str, 
        image_data: bytes,
        image_mime_type: str = "image/png",
        system_prompt: Optional[str] = None
    ) -> LLMResponse:
        import PIL.Image
        import io
        
        image = PIL.Image.open(io.BytesIO(image_data))
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        generation_config = {"temperature": 0.1}
        
        # Enable thinking mode for supported models (Gemini 2.0 Flash Thinking)
        if self.config.enable_reasoning:
            generation_config["thought"] = True
        
        # Add structured output config if enabled
        if self.config.structured_output and self.config.response_schema:
            generation_config["response_mime_type"] = "application/json"
            generation_config["response_schema"] = self.config.response_schema
        
        response = await self.client.generate_content_async(
            [full_prompt, image],
            generation_config=generation_config
        )
        
        return LLMResponse(
            content=response.text,
            model=self.config.model,
            provider=LLMProviderType.GEMINI.value,
            usage={
                "prompt_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0,
                "completion_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0,
                "total_tokens": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
            },
            raw_response=response
        )


class OpenRouterProvider(BaseLLMProvider):
    """
    OpenRouter API provider with reasoning and structured output support.
    
    Uses OpenAI-compatible API with additional OpenRouter features:
    - Reasoning tokens for Gemini 3 Pro and other reasoning models
    - Structured JSON output via json_schema response format
    - Multi-provider access through a single API
    """
    
    def _initialize_client(self):
        from openai import AsyncOpenAI
        self._client = AsyncOpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url or "https://openrouter.ai/api/v1",
            timeout=self.config.timeout,
            default_headers={
                # TODO: Add any OpenRouter-specific headers if needed (like organization ID, etc)
                # "HTTP-Referer": "https://www.designmonkey.com",
                "X-Title": "designmonkey"
            }
        )
    
    def _build_extra_body(self) -> dict:
        """Build extra_body parameters for OpenRouter requests."""
        extra_body = {}
        
        # Enable reasoning for supported models (like Gemini 3 Pro)
        if self.config.enable_reasoning:
            extra_body["reasoning"] = {
                "enabled": True,
                "effort": "high"  # Use high reasoning effort for better analysis
            }
        
        return extra_body if extra_body else None
    
    def _build_response_format(self) -> Optional[dict]:
        """Build response_format for structured output."""
        if not self.config.structured_output or not self.config.response_schema:
            return None
        
        return {
            "type": "json_schema",
            "json_schema": {
                "name": "design_system",
                "strict": True,
                "schema": self.config.response_schema
            }
        }
    
    def _extract_reasoning(self, response) -> Optional[str]:
        """Extract reasoning from response if available."""
        try:
            message = response.choices[0].message
            
            # Check for reasoning in different possible locations
            if hasattr(message, 'reasoning'):
                return message.reasoning
            
            if hasattr(message, 'reasoning_details') and message.reasoning_details:
                # Extract text from reasoning_details array
                reasoning_texts = []
                for detail in message.reasoning_details:
                    if hasattr(detail, 'text') and detail.text:
                        reasoning_texts.append(detail.text)
                    elif hasattr(detail, 'summary') and detail.summary:
                        reasoning_texts.append(detail.summary)
                return "\n".join(reasoning_texts) if reasoning_texts else None
            
            return None
        except Exception as e:
            logger.debug(f"Could not extract reasoning: {e}")
            return None
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        extra_body = self._build_extra_body()
        response_format = self._build_response_format()
        
        kwargs = {
            "model": self.config.model,
            "messages": messages,
            "temperature": 0.1
        }
        if extra_body:
            kwargs["extra_body"] = extra_body
        if response_format:
            kwargs["response_format"] = response_format
        
        response = await self.client.chat.completions.create(**kwargs)
        
        # Validate response
        if not response.choices or len(response.choices) == 0:
            logger.error(f"OpenRouter returned empty choices. Response: {response}")
            raise ValueError("OpenRouter returned an empty response. The model may be temporarily unavailable.")
        
        reasoning = self._extract_reasoning(response)
        content = response.choices[0].message.content or ""
        
        return LLMResponse(
            content=content,
            model=response.model,
            provider=LLMProviderType.OPENROUTER.value,
            usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0
            },
            raw_response=response,
            reasoning=reasoning
        )
    
    async def generate_with_image(
        self, 
        prompt: str, 
        image_data: bytes,
        image_mime_type: str = "image/png",
        system_prompt: Optional[str] = None
    ) -> LLMResponse:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        base64_image = self._encode_image_base64(image_data)
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{image_mime_type};base64,{base64_image}"
                    }
                }
            ]
        })
        
        extra_body = self._build_extra_body()
        response_format = self._build_response_format()
        
        kwargs = {
            "model": self.config.model,
            "messages": messages,
            "temperature": 0.1
        }
        if extra_body:
            kwargs["extra_body"] = extra_body
        if response_format:
            kwargs["response_format"] = response_format
        
        response = await self.client.chat.completions.create(**kwargs)
        
        # Validate response
        if not response.choices or len(response.choices) == 0:
            logger.error(f"OpenRouter returned empty choices for image request. Response: {response}")
            raise ValueError("OpenRouter returned an empty response. The model may have failed to process the image or is temporarily unavailable.")
        
        reasoning = self._extract_reasoning(response)
        content = response.choices[0].message.content or ""
        
        return LLMResponse(
            content=content,
            model=response.model,
            provider=LLMProviderType.OPENROUTER.value,
            usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0
            },
            raw_response=response,
            reasoning=reasoning
        )


# Provider registry
PROVIDER_CLASSES: dict[LLMProviderType, type[BaseLLMProvider]] = {
    LLMProviderType.GEMINI: GeminiProvider,
    LLMProviderType.OPENROUTER: OpenRouterProvider,
}


def create_llm_provider(config: LLMConfig) -> BaseLLMProvider:
    """
    Factory function to create an LLM provider instance.
    
    Args:
        config: LLMConfig with provider type and credentials
        
    Returns:
        An instance of the appropriate LLM provider
        
    Raises:
        ValueError: If the provider type is not supported
    """
    provider_class = PROVIDER_CLASSES.get(config.provider_type)
    if not provider_class:
        raise ValueError(f"Unsupported LLM provider: {config.provider_type}")
    
    return provider_class(config)
