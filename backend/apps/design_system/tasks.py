"""
Celery tasks for async design system generation.

This module provides Celery tasks for generating design systems from images
using LLM providers with progress tracking and structured JSON output.

Single-Step Workflow:
1. Initialization - Set up LLM provider and validate inputs (10%)
2. Single-Step Analysis - Comprehensive analysis with JSON output (50%)
3. Finalization - Validate JSON, add metadata and save to database (100%)
"""
import json
import logging
import time
import uuid
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional, Any
from celery import shared_task, current_task
from django.core.cache import cache
from django.utils.translation import gettext as _
from json_repair import repair_json

from .llm import create_llm_provider
from .llm.config import get_default_provider
from .llm.providers import LLMConfig
from .prompts import get_json_analysis_prompt, get_aesthetic_analysis_prompt
from .schema import (
    get_gemini_response_schema,
    validate_design_system_output,
    convert_to_frontend_format
)

logger = logging.getLogger(__name__)


# =============================================================================
# Workflow Step Constants (Single-Step)
# =============================================================================

WORKFLOW_STEPS = {
    "initialization": {"name": "Initialization", "weight": 10},
    "analysis": {"name": "Single-Step Analysis", "weight": 80},
    "finalization": {"name": "Finalization", "weight": 10},
}


class TaskStatus(str, Enum):
    """Status of an async task."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TaskProgress:
    """Progress information for an async task."""
    task_id: str
    status: TaskStatus
    progress: int  # 0-100
    current_step: str
    total_steps: int
    current_step_number: int
    message: str
    result: Optional[dict] = None
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        return asdict(self)


def get_task_cache_key(task_id: str) -> str:
    """Get the cache key for a task's progress."""
    return f"design_system_task:{task_id}"


def update_task_progress(
    task_id: str,
    status: TaskStatus,
    progress: int,
    current_step: str,
    current_step_number: int,
    total_steps: int,
    message: str,
    result: Optional[dict] = None,
    error: Optional[str] = None,
    timeout: int = 3600  # 1 hour cache
):
    """
    Update task progress in cache for frontend polling.
    
    Args:
        task_id: Unique task identifier
        status: Current task status
        progress: Progress percentage (0-100)
        current_step: Description of current step
        current_step_number: Current step number
        total_steps: Total number of steps
        message: User-friendly message
        result: Optional result data when completed
        error: Optional error message if failed
        timeout: Cache timeout in seconds
    """
    progress_data = TaskProgress(
        task_id=task_id,
        status=status,
        progress=progress,
        current_step=current_step,
        current_step_number=current_step_number,
        total_steps=total_steps,
        message=message,
        result=result,
        error=error
    )
    
    cache_key = get_task_cache_key(task_id)
    cache.set(cache_key, progress_data.to_dict(), timeout)
    
    # Enhanced logging with step details
    logger.info(f"[Task {task_id[:8]}...] [{current_step}] {progress}% - {message}")


def get_task_progress(task_id: str) -> Optional[dict]:
    """
    Get task progress from cache.
    
    Args:
        task_id: Unique task identifier
        
    Returns:
        TaskProgress dict or None if not found
    """
    cache_key = get_task_cache_key(task_id)
    return cache.get(cache_key)


@shared_task(bind=True)
def generate_design_system_task(
    self,
    task_id: str,
    design_system_id: str
) -> dict:
    """
    Celery task to generate a design system from uploaded images.
    
    Single-Step Workflow:
    1. Initialization - Load design system from DB, set up LLM provider
    2. Single-Step Analysis - Comprehensive analysis using the single-step prompt
    3. Finalization - Add metadata and save to database
    
    All information (images, name, description) is loaded from the database
    using the design_system_id. This keeps the Celery message small and
    works with any storage backend (local or S3).
    
    Args:
        task_id: Unique task identifier for progress tracking
        design_system_id: UUID of the DesignSystem model to analyze
        
    Returns:
        Dict containing the generated design system or error information
    """
    import asyncio
    from .models import DesignSystem
    
    total_steps = 3  # Simplified to 3 steps
    
    try:
        # =================================================================
        # STEP 1: Initialization
        # =================================================================
        update_task_progress(
            task_id=task_id,
            status=TaskStatus.PROCESSING,
            progress=10,
            current_step="initialization",
            current_step_number=1,
            total_steps=total_steps,
            message=_("Setting up AI vision model...")
        )
        
        # Load design system from database
        logger.info(f"[Task {task_id[:8]}] Loading design system from database...")
        design_system = DesignSystem.objects.select_related('image').get(id=design_system_id)
        vibe_name = design_system.name
        vibe_description = design_system.description
        
        logger.info(f"=" * 60)
        logger.info(f"[Task {task_id[:8]}] Starting Design System Analysis")
        logger.info(f"[Task {task_id[:8]}] Vibe: {vibe_name or 'Untitled'}")
        logger.info(f"=" * 60)
        
        # Get LLM provider configuration (from environment variables)
        logger.info(f"[Task {task_id[:8]}] Configuring LLM provider with structured output...")
        base_config = get_default_provider(for_vision=True)
        logger.info(f"[Task {task_id[:8]}] Using default provider: {base_config.provider_type.value if base_config else 'None'}")
        
        if not base_config:
            raise ValueError(_("No LLM provider configured. Please set up at least one provider."))
        
        # Create new config with structured output enabled
        config = LLMConfig(
            provider_type=base_config.provider_type,
            api_key=base_config.api_key,
            model=base_config.model,
            base_url=base_config.base_url,
            timeout=base_config.timeout,
            enable_reasoning=base_config.enable_reasoning,
            structured_output=True,
            response_schema=get_gemini_response_schema()
        )
        
        provider = create_llm_provider(config)
        logger.info(f"[Task {task_id[:8]}] LLM Provider initialized with structured output: {config.provider_type.value} / {config.model}")
        
        # Load image from storage (works with both local filesystem and S3)
        if not hasattr(design_system, 'image'):
            raise ValueError(_("No image found for this design system."))
        
        img = design_system.image
        with img.image.open('rb') as f:
            image_bytes = f.read()
        mime_type = img.mime_type
        image_name = img.name
        logger.info(f"[Task {task_id[:8]}] Image loaded from storage: {image_name} ({mime_type}, {len(image_bytes)} bytes)")
        
        # =================================================================
        # STEP 2: Parallel Analysis (Design Tokens + Aesthetic Analysis)
        # =================================================================
        logger.info(f"-" * 60)
        logger.info(f"[Task {task_id[:8]}] STEP 2: Parallel Analysis (Design Tokens + Aesthetic)")
        logger.info(f"-" * 60)
        
        update_task_progress(
            task_id=task_id,
            status=TaskStatus.PROCESSING,
            progress=50,
            current_step="analysis",
            current_step_number=2,
            total_steps=total_steps,
            message=_("AI is extracting design tokens and aesthetic analysis...")
        )
        
        # Get prompts for both analyses
        design_token_prompt = get_json_analysis_prompt()
        aesthetic_prompt = get_aesthetic_analysis_prompt()
        
        # Add context from vibe name/description to both prompts
        if vibe_name or vibe_description:
            context = f"\n\n# Additional Context\n"
            if vibe_name:
                context += f"- Design System Name: {vibe_name}\n"
            if vibe_description:
                context += f"- Style Description: {vibe_description}\n"
            design_token_prompt = design_token_prompt + context
            aesthetic_prompt = aesthetic_prompt + context
        
        logger.info(f"[Task {task_id[:8]}] Sending image for parallel analysis (design tokens + aesthetic)...")
        
        # Use threading to run both LLM calls concurrently
        import threading
        
        design_token_result = {"response": None, "error": None}
        aesthetic_result = {"response": None, "error": None}
        
        def run_design_token_analysis():
            """Thread target for design token extraction."""
            try:
                design_token_result["response"] = asyncio.run(
                    provider.generate_with_image(
                        prompt=design_token_prompt,
                        image_data=image_bytes,
                        image_mime_type=mime_type
                    )
                )
            except Exception as e:
                design_token_result["error"] = e
                logger.error(f"[Task {task_id[:8]}] Design token analysis failed: {e}")
        
        def run_aesthetic_analysis():
            """Thread target for aesthetic analysis extraction."""
            try:
                # Create a separate provider instance for the aesthetic analysis thread
                # to avoid sharing async state across threads
                aesthetic_config = LLMConfig(
                    provider_type=base_config.provider_type,
                    api_key=base_config.api_key,
                    model=base_config.model,
                    base_url=base_config.base_url,
                    timeout=base_config.timeout,
                    enable_reasoning=base_config.enable_reasoning,
                    structured_output=False,  # Aesthetic analysis uses free-form JSON
                    response_schema=None
                )
                aesthetic_provider = create_llm_provider(aesthetic_config)
                aesthetic_result["response"] = asyncio.run(
                    aesthetic_provider.generate_with_image(
                        prompt=aesthetic_prompt,
                        image_data=image_bytes,
                        image_mime_type=mime_type
                    )
                )
            except Exception as e:
                aesthetic_result["error"] = e
                logger.error(f"[Task {task_id[:8]}] Aesthetic analysis failed: {e}")
        
        analysis_start_time = time.time()
        
        # Start both threads
        design_token_thread = threading.Thread(target=run_design_token_analysis, name="design-token-analysis")
        aesthetic_thread = threading.Thread(target=run_aesthetic_analysis, name="aesthetic-analysis")
        
        design_token_thread.start()
        aesthetic_thread.start()
        
        # Wait for both to complete
        design_token_thread.join()
        aesthetic_thread.join()
        
        analysis_elapsed = time.time() - analysis_start_time
        logger.info(f"[Task {task_id[:8]}] Parallel analysis completed in {analysis_elapsed:.2f}s")
        
        # Check design token result (required)
        if design_token_result["error"]:
            raise design_token_result["error"]
        
        analysis_response = design_token_result["response"]
        logger.info(f"[Task {task_id[:8]}] Design token response length: {len(analysis_response.content)} chars")
        
        # Process aesthetic result (optional — non-fatal if it fails)
        # Aesthetic analysis is now Markdown text, no JSON parsing needed
        aesthetic_analysis_data = None
        if aesthetic_result["response"]:
            aesthetic_analysis_data = aesthetic_result["response"].content.strip()
            logger.info(f"[Task {task_id[:8]}] ✓ Aesthetic analysis extracted ({len(aesthetic_analysis_data)} chars)")
        elif aesthetic_result["error"]:
            logger.warning(f"[Task {task_id[:8]}] Aesthetic analysis failed (non-fatal): {aesthetic_result['error']}")
        
        # Update progress after LLM completes
        update_task_progress(
            task_id=task_id,
            status=TaskStatus.PROCESSING,
            progress=85,
            current_step="analysis",
            current_step_number=2,
            total_steps=total_steps,
            message=_("Validating and processing design tokens...")
        )
        
        # Parse and validate JSON response
        try:
            # Try direct JSON parse first (structured output should return clean JSON)
            raw_json = json.loads(analysis_response.content)
        except json.JSONDecodeError:
            # Fallback to json_repair for non-compliant responses
            logger.warning(f"[Task {task_id[:8]}] Direct JSON parse failed, attempting repair...")
            repaired = repair_json(analysis_response.content)
            if isinstance(repaired, str):
                raw_json = json.loads(repaired)
            else:
                raw_json = repaired
        
        # Validate against schema
        try:
            validated = validate_design_system_output(raw_json)
            logger.info(f"[Task {task_id[:8]}] ✓ JSON validated successfully")
        except Exception as validation_error:
            logger.error(f"[Task {task_id[:8]}] JSON validation failed: {validation_error}")
            logger.debug(f"[Task {task_id[:8]}] Raw JSON: {raw_json}")
            raise ValueError(_("Failed to extract design system from image. Please try again with a clearer design image."))
        
        # Convert to frontend format
        analysis_result = convert_to_frontend_format(raw_json)
        logger.info(f"[Task {task_id[:8]}] ✓ Design tokens extracted: confidence={analysis_result.get('confidence')}")
        
        # =================================================================
        # STEP 3: Finalization
        # =================================================================
        logger.info(f"-" * 60)
        logger.info(f"[Task {task_id[:8]}] STEP 3: Finalization")
        logger.info(f"-" * 60)
        
        update_task_progress(
            task_id=task_id,
            status=TaskStatus.PROCESSING,
            progress=90,
            current_step="finalizing",
            current_step_number=3,
            total_steps=total_steps,
            message=_("Saving design system to database...")
        )
        
        # Add metadata
        final_result = {
            **analysis_result,
            "metadata": {
                "name": vibe_name or "Untitled Design System",
                "description": vibe_description or "",
                "provider": config.provider_type.value,
                "model": config.model,
                "images_analyzed": 1,
                "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "workflow_version": "5.0"  # Version 5.0 = parallel design tokens + aesthetic analysis
            }
        }
        
        logger.info(f"[Task {task_id[:8]}] Metadata added to result")
        
        # Save to database (design tokens + aesthetic analysis)
        logger.info(f"[Task {task_id[:8]}] Saving to database (ID: {design_system_id[:8]}...)")
        save_design_system_result(
            design_system_id=design_system_id,
            style_data=final_result,
            aesthetic_analysis=aesthetic_analysis_data,
            provider=config.provider_type.value,
            model=config.model
        )
        logger.info(f"[Task {task_id[:8]}] ✓ Saved to database successfully")
        
        # Mark completed
        logger.info(f"=" * 60)
        logger.info(f"[Task {task_id[:8]}] ✅ ANALYSIS COMPLETED SUCCESSFULLY")
        logger.info(f"[Task {task_id[:8]}] Total Time: {analysis_elapsed:.2f}s")
        logger.info(f"=" * 60)
        
        update_task_progress(
            task_id=task_id,
            status=TaskStatus.COMPLETED,
            progress=100,
            current_step="completed",
            current_step_number=total_steps,
            total_steps=total_steps,
            message=_("Analysis complete! Your design system is ready."),
            result=final_result
        )
        
        return final_result
        
    except Exception as e:
        logger.error(f"=" * 60)
        logger.error(f"[Task {task_id[:8]}] ❌ ANALYSIS FAILED")
        logger.error(f"[Task {task_id[:8]}] Error: {str(e)}")
        logger.error(f"=" * 60)
        logger.exception(f"Task {task_id} failed with exception:")
        
        # Save error to database
        save_design_system_error(design_system_id, str(e))
        
        update_task_progress(
            task_id=task_id,
            status=TaskStatus.FAILED,
            progress=0,
            current_step="error",
            current_step_number=0,
            total_steps=total_steps,
            message=_("Analysis failed. Please check the error details."),
            error=str(e)
        )
        
        raise


# =============================================================================
# Helper Functions
# =============================================================================

def _parse_llm_json(content: str) -> dict:
    """
    Parse LLM response into JSON, with automatic repair for common issues.
    
    Uses json_repair to handle:
    - Markdown code blocks (```json, ```)
    - Missing quotes, commas, brackets
    - Trailing commas
    - Single quotes instead of double quotes
    - JavaScript-style comments
    - Invalid values (NaN, Infinity)
    
    Args:
        content: Raw LLM response content
        
    Returns:
        Parsed dict
        
    Raises:
        ValueError: If JSON cannot be parsed/repaired
    """
    try:
        result = repair_json(content)
        
        # repair_json might return a string if content is already valid JSON string
        # We need to ensure we get a dict
        if isinstance(result, str):
            result = json.loads(result)
        
        if not isinstance(result, dict):
            raise ValueError(f"Expected dict, got {type(result).__name__}")
            
        return result
    except Exception as e:
        logger.error(f"Failed to parse/repair JSON: {e}")
        logger.debug(f"Raw content preview: {content[:500]}...")
        raise ValueError(f"Unable to parse LLM response as JSON: {e}") from e




def _extract_style_from_text(analysis_text: str) -> str:
    """
    Extract visual style from analysis text when JSON parsing fails.
    Uses keyword matching as a fallback.
    
    Args:
        analysis_text: Raw LLM response text
        
    Returns:
        Detected style identifier
    """
    text_lower = analysis_text.lower()
    
    # Check for style keywords in priority order
    style_keywords = {
        "neumorphism": ["neumorphism", "soft ui", "新拟物", "neumorph"],
        "glassmorphism": ["glassmorphism", "frosted glass", "玻璃态", "毛玻璃", "backdrop blur"],
        "material": ["material design", "elevation", "投影", "shadow-based", "google material"],
        "gradient": ["gradient", "渐变", "vibrant", "colorful gradient"],
        "playful": ["playful", "organic", "bubble", "inflated", "doughy", "rounded corners"],
        "flat": ["flat design", "minimal", "扁平", "极简", "clean lines"],
    }
    
    for style, keywords in style_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            return style
    
    return "general"


def merge_design_systems(results: list[dict]) -> dict:
    """
    Merge multiple design system analysis results into a single coherent system.
    
    This function takes the most common values and creates a unified design system.
    
    Args:
        results: List of design system dicts from individual image analysis
        
    Returns:
        Merged design system dict
    """
    if not results:
        return {}
    
    if len(results) == 1:
        return results[0]
    
    # Filter out invalid results
    valid_results = [r for r in results if isinstance(r, dict) and 'raw_response' not in r]
    
    if not valid_results:
        # Return first result if no valid parsed results
        return results[0] if results else {}
    
    if len(valid_results) == 1:
        return valid_results[0]
    
    # Use the first valid result as base and merge others
    merged = valid_results[0].copy()
    
    # For colors, take the most saturated/prominent
    if 'colors' in merged:
        all_colors = [r.get('colors', {}) for r in valid_results]
        merged['colors'] = merge_color_dicts(all_colors)
    
    # For typography, prefer the first valid one
    if 'typography' in merged:
        for r in valid_results[1:]:
            if 'typography' in r:
                for key, value in r['typography'].items():
                    if key not in merged['typography'] or not merged['typography'][key]:
                        merged['typography'][key] = value
    
    # Merge style rules
    if 'styleRules' in merged:
        all_rules = set(merged.get('styleRules', []))
        for r in valid_results[1:]:
            all_rules.update(r.get('styleRules', []))
        merged['styleRules'] = list(all_rules)
    
    return merged


def merge_color_dicts(color_dicts: list[dict]) -> dict:
    """
    Merge multiple color dictionaries, taking the first non-empty value for each key.
    
    Args:
        color_dicts: List of color dicts
        
    Returns:
        Merged color dict
    """
    if not color_dicts:
        return {}
    
    merged = {}
    all_keys = set()
    for d in color_dicts:
        all_keys.update(d.keys())
    
    for key in all_keys:
        for d in color_dicts:
            if key in d and d[key]:
                merged[key] = d[key]
                break
    
    return merged


def create_analysis_task(design_system_id: str) -> str:
    """
    Create and queue a design system analysis task.
    
    The Celery task will load all information (image, name, description)
    from the database using the design_system_id. This keeps the Redis
    message small and works with any storage backend.
    
    Args:
        design_system_id: UUID of the DesignSystem model to analyze
        
    Returns:
        Task ID for progress tracking
    """
    task_id = str(uuid.uuid4())
    total_steps = 3  # Single-step workflow: initialization, analysis, finalization
    
    logger.info(f"[Task {task_id[:8]}] Creating analysis task for design system {design_system_id[:8]}...")
    
    # Initialize progress
    update_task_progress(
        task_id=task_id,
        status=TaskStatus.PENDING,
        progress=5,
        current_step="queued",
        current_step_number=0,
        total_steps=total_steps,
        message=_("Task queued, analysis will begin shortly...")
    )
    
    # Queue the task - only pass IDs, task will load data from DB
    generate_design_system_task.delay(
        task_id=task_id,
        design_system_id=design_system_id
    )
    
    return task_id


def save_design_system_result(
    design_system_id: str,
    style_data: dict,
    provider: str,
    model: str,
    aesthetic_analysis: str = None
):
    """
    Save the analysis result to the database.
    
    Args:
        design_system_id: UUID of the DesignSystem model
        style_data: The generated style data (stored as design_tokens)
        provider: LLM provider used
        model: LLM model used
        aesthetic_analysis: Optional aesthetic analysis Markdown text
    """
    from django.utils import timezone
    from .models import DesignSystem, DesignSystemStatus
    
    try:
        design_system = DesignSystem.objects.get(id=design_system_id)
        
        # Add provider/model info to the metadata within design_tokens
        if 'metadata' not in style_data:
            style_data['metadata'] = {}
        style_data['metadata']['llm_provider'] = provider
        style_data['metadata']['llm_model'] = model
        
        design_system.design_tokens = style_data
        design_system.status = DesignSystemStatus.COMPLETED
        design_system.analyzed_at = timezone.now()
        design_system.analysis_error = None
        
        # Save aesthetic analysis if provided
        if aesthetic_analysis is not None:
            design_system.aesthetic_analysis = aesthetic_analysis
        
        update_fields = [
            'design_tokens', 'aesthetic_analysis', 'status', 
            'analyzed_at', 'analysis_error', 'updated_at'
        ]
        design_system.save(update_fields=update_fields)
        logger.info(f"Saved design system result for {design_system_id} (aesthetic_analysis: {'yes' if aesthetic_analysis else 'no'})")
    except DesignSystem.DoesNotExist:
        logger.error(f"DesignSystem {design_system_id} not found when saving result")
    except Exception as e:
        logger.exception(f"Error saving design system result: {e}")


def save_design_system_error(design_system_id: str, error: str):
    """
    Save the analysis error to the database.
    
    Args:
        design_system_id: UUID of the DesignSystem model
        error: Error message
    """
    from .models import DesignSystem, DesignSystemStatus
    
    try:
        design_system = DesignSystem.objects.get(id=design_system_id)
        design_system.status = DesignSystemStatus.FAILED
        design_system.analysis_error = error
        design_system.save(update_fields=['status', 'analysis_error', 'updated_at'])
        logger.info(f"Saved design system error for {design_system_id}")
    except DesignSystem.DoesNotExist:
        logger.error(f"DesignSystem {design_system_id} not found when saving error")
    except Exception as e:
        logger.exception(f"Error saving design system error: {e}")
