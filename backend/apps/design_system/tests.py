"""
Tests for the design_system app.

Covers DesignSystem/DesignSystemImage models, schema validation,
services (CSS/Tailwind generation), task helpers, serializers,
and API views (CRUD + image upload/delete).
"""
import base64
import json
import unittest
import uuid
from dataclasses import asdict
from unittest.mock import patch, MagicMock, PropertyMock

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.test import TestCase
from pydantic import ValidationError
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework_simplejwt.tokens import RefreshToken

from apps.design_system.models import (
    DesignSystem,
    DesignSystemImage,
    DesignSystemStatus,
    design_system_image_path,
)
from apps.design_system.schema import (
    get_design_system_json_schema,
    get_gemini_response_schema,
    get_openrouter_response_format,
    validate_design_system_output,
    convert_to_frontend_format,
)
from apps.design_system.services import (
    generate_css_variables,
    generate_tailwind_config,
    DesignSystemResult,
    DesignSystemService,
)
from apps.design_system.tasks import (
    TaskProgress,
    TaskStatus,
    get_task_cache_key,
    _parse_llm_json,
    _extract_style_from_text,
    merge_design_systems,
    merge_color_dicts,
)
from apps.design_system.serializers import (
    DesignSystemCreateSerializer,
    DesignSystemUpdateSerializer,
    ImageUploadSerializer,
    StartAnalysisSerializer,
    GenerateDesignSystemRequestSerializer,
)

User = get_user_model()

# 1×1 white pixel PNG (valid minimal PNG for image tests)
TINY_PNG = base64.b64encode(
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
    b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00'
    b'\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00'
    b'\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
).decode('utf-8')


# =============================================================================
# Model Tests
# =============================================================================


class TestDesignSystemStatus(TestCase):
    """Tests for DesignSystemStatus choices."""

    def test_status_values(self):
        """Status choices should have the expected string values."""
        self.assertEqual(DesignSystemStatus.PENDING, 'pending')
        self.assertEqual(DesignSystemStatus.PROCESSING, 'processing')
        self.assertEqual(DesignSystemStatus.COMPLETED, 'completed')
        self.assertEqual(DesignSystemStatus.FAILED, 'failed')


class TestDesignSystemModel(TestCase):
    """Tests for the DesignSystem model."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='ds@test.com', password='StrongP@ss123!'
        )

    def test_get_primary_color_with_tokens(self):
        """get_primary_color returns the primary color from design_tokens."""
        ds = DesignSystem.objects.create(
            user=self.user, name='Test',
            design_tokens={'colors': {'primary': '#FF0000'}},
        )
        self.assertEqual(ds.get_primary_color(), '#FF0000')

    def test_get_primary_color_without_tokens(self):
        """get_primary_color returns default when design_tokens is None."""
        ds = DesignSystem.objects.create(
            user=self.user, name='Test', design_tokens=None,
        )
        self.assertEqual(ds.get_primary_color(), '#2A99D3')

    def test_get_primary_color_empty_tokens(self):
        """get_primary_color returns default when design_tokens is empty dict."""
        ds = DesignSystem.objects.create(
            user=self.user, name='Test', design_tokens={},
        )
        self.assertEqual(ds.get_primary_color(), '#2A99D3')

    def test_get_primary_color_no_primary_key(self):
        """get_primary_color returns default when colors dict has no primary."""
        ds = DesignSystem.objects.create(
            user=self.user, name='Test',
            design_tokens={'colors': {'secondary': '#00FF00'}},
        )
        self.assertEqual(ds.get_primary_color(), '#2A99D3')

    def test_get_initial_with_name(self):
        """get_initial returns first uppercase character of name."""
        ds = DesignSystem.objects.create(user=self.user, name='alpha')
        self.assertEqual(ds.get_initial(), 'A')

    def test_get_initial_empty_name(self):
        """get_initial returns 'D' when name is empty."""
        ds = DesignSystem.objects.create(user=self.user, name='')
        self.assertEqual(ds.get_initial(), 'D')

    def test_str_representation(self):
        """__str__ returns 'name (user.email)'."""
        ds = DesignSystem.objects.create(user=self.user, name='My Vibe')
        self.assertEqual(str(ds), f'My Vibe ({self.user.email})')

    def test_default_ordering(self):
        """Default ordering should be -updated_at."""
        self.assertEqual(DesignSystem._meta.ordering, ['-updated_at'])

    def test_default_status_is_pending(self):
        """Default status should be PENDING."""
        ds = DesignSystem.objects.create(user=self.user, name='New')
        self.assertEqual(ds.status, DesignSystemStatus.PENDING)

    def test_design_tokens_defaults_to_empty_dict(self):
        """design_tokens should default to empty dict."""
        ds = DesignSystem.objects.create(user=self.user, name='Def')
        self.assertEqual(ds.design_tokens, {})


class TestDesignSystemImageModel(TestCase):
    """Tests for the DesignSystemImage model and helpers."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='img@test.com', password='StrongP@ss123!'
        )
        self.ds = DesignSystem.objects.create(user=self.user, name='ImgDS')

    def test_design_system_image_path(self):
        """design_system_image_path returns correct upload path."""
        mock_instance = MagicMock()
        mock_instance.design_system.user_id = self.user.id
        mock_instance.design_system_id = self.ds.id
        path = design_system_image_path(mock_instance, 'test.png')
        self.assertEqual(
            path,
            f'design_systems/{self.user.id}/{self.ds.id}/test.png',
        )

    def test_str_representation(self):
        """__str__ returns 'name - design_system.name'."""
        img_data = base64.b64decode(TINY_PNG)
        img = DesignSystemImage.objects.create(
            design_system=self.ds,
            name='photo.png',
            image=ContentFile(img_data, name='photo.png'),
            mime_type='image/png',
        )
        self.assertEqual(str(img), f'photo.png - {self.ds.name}')

    def test_save_auto_populates_file_size(self):
        """save() should auto-populate file_size from image."""
        img_data = base64.b64decode(TINY_PNG)
        img = DesignSystemImage.objects.create(
            design_system=self.ds,
            name='auto.png',
            image=ContentFile(img_data, name='auto.png'),
            mime_type='image/png',
        )
        self.assertGreater(img.file_size, 0)


# =============================================================================
# Schema Tests
# =============================================================================


class TestSchemaFunctions(unittest.TestCase):
    """Tests for schema.py helper functions."""

    def test_get_design_system_json_schema(self):
        """get_design_system_json_schema returns a dict with required fields."""
        schema = get_design_system_json_schema()
        self.assertIsInstance(schema, dict)
        self.assertIn('properties', schema)
        self.assertIn('required', schema)

    def test_get_gemini_response_schema_structure(self):
        """Gemini schema should have colors, typography, shadow_depth properties."""
        schema = get_gemini_response_schema()
        props = schema['properties']
        self.assertIn('colors', props)
        self.assertIn('typography', props)
        self.assertIn('shadow_depth', props)

    def test_get_gemini_response_schema_required(self):
        """All three top-level fields should be required."""
        schema = get_gemini_response_schema()
        required = schema['required']
        self.assertIn('colors', required)
        self.assertIn('typography', required)
        self.assertIn('shadow_depth', required)

    def test_get_openrouter_response_format(self):
        """OpenRouter format wraps schema in json_schema format."""
        fmt = get_openrouter_response_format()
        self.assertEqual(fmt['type'], 'json_schema')
        self.assertIn('json_schema', fmt)
        self.assertEqual(fmt['json_schema']['name'], 'design_system')
        self.assertTrue(fmt['json_schema']['strict'])
        self.assertIn('schema', fmt['json_schema'])

    def test_validate_design_system_output_valid(self):
        """Valid data should pass validation."""
        data = {
            'colors': {
                'primary': '#FF0000',
                'secondary': '#00FF00',
                'background': '#FFFFFF',
                'surface': '#F0F0F0',
            },
            'typography': {
                'font_family': 'Inter',
                'font_weight': '400, 700',
                'base_font_size': '16px',
            },
            'shadow_depth': 3,
        }
        result = validate_design_system_output(data)
        self.assertEqual(result.shadow_depth, 3)

    def test_validate_design_system_output_missing_fields(self):
        """Missing required fields should raise ValidationError."""
        with self.assertRaises(ValidationError):
            validate_design_system_output({'colors': {}})

    def test_validate_design_system_output_wrong_types(self):
        """Wrong types should raise ValidationError."""
        with self.assertRaises(ValidationError):
            validate_design_system_output({
                'colors': {
                    'primary': 123,
                    'secondary': '#00FF00',
                    'background': '#FFFFFF',
                    'surface': '#F0F0F0',
                },
                'typography': {
                    'font_family': 'Inter',
                    'font_weight': '400',
                    'base_font_size': '16px',
                },
                'shadow_depth': 'high',
            })

    def test_validate_design_system_output_shadow_depth_out_of_range(self):
        """shadow_depth outside 0-5 should raise ValidationError."""
        with self.assertRaises(ValidationError):
            validate_design_system_output({
                'colors': {
                    'primary': '#FF0000',
                    'secondary': '#00FF00',
                    'background': '#FFFFFF',
                    'surface': '#F0F0F0',
                },
                'typography': {
                    'font_family': 'Inter',
                    'font_weight': '400',
                    'base_font_size': '16px',
                },
                'shadow_depth': 10,
            })

    def test_convert_to_frontend_format_camel_case(self):
        """convert_to_frontend_format should convert snake_case to camelCase."""
        data = {
            'colors': {
                'primary': '#FF0000',
                'secondary': '#00FF00',
                'background': '#FFFFFF',
                'surface': '#F0F0F0',
            },
            'typography': {
                'font_family': 'Inter',
                'font_weight': '400, 700',
                'base_font_size': '16px',
            },
            'shadow_depth': 3,
        }
        result = convert_to_frontend_format(data)
        self.assertEqual(result['typography']['fontFamily'], 'Inter')
        self.assertEqual(result['typography']['fontWeight'], '400, 700')
        self.assertEqual(result['typography']['baseFontSize'], '16px')
        self.assertEqual(result['shadowDepth'], 3)
        self.assertEqual(result['colors']['primary'], '#FF0000')

    def test_convert_to_frontend_format_handles_missing_fields(self):
        """convert_to_frontend_format should handle missing fields gracefully."""
        result = convert_to_frontend_format({})
        self.assertEqual(result['colors']['primary'], None)
        self.assertEqual(result['typography']['fontFamily'], None)
        self.assertIsNone(result['shadowDepth'])


# =============================================================================
# Service Tests
# =============================================================================


class TestGenerateCSSVariables(unittest.TestCase):
    """Tests for generate_css_variables()."""

    def test_full_design_system(self):
        """Full design system should produce correct CSS custom properties."""
        ds = {
            'colors': {
                'primary': '#FF0000',
                'secondary': '#00FF00',
                'background': '#FFFFFF',
                'surface': '#F0F0F0',
            },
            'typography': {
                'fontFamily': 'Inter, sans-serif',
                'baseFontSize': '16px',
            },
        }
        css = generate_css_variables(ds)
        self.assertIn('--color-primary: #FF0000;', css)
        self.assertIn('--color-secondary: #00FF00;', css)
        self.assertIn('--bg-canvas: #FFFFFF;', css)
        self.assertIn('--bg-surface: #F0F0F0;', css)
        self.assertIn('--font-sans: Inter, sans-serif;', css)
        self.assertIn('--text-body-size: 16px;', css)
        self.assertIn(':root {', css)
        self.assertIn('}', css)

    def test_empty_design_system(self):
        """Empty design system should produce just :root {}."""
        css = generate_css_variables({})
        self.assertEqual(css, ':root {\n}')

    def test_partial_colors(self):
        """Only present colors should be included."""
        ds = {'colors': {'primary': '#FF0000'}}
        css = generate_css_variables(ds)
        self.assertIn('--color-primary: #FF0000;', css)
        self.assertNotIn('--color-secondary', css)


class TestGenerateTailwindConfig(unittest.TestCase):
    """Tests for generate_tailwind_config()."""

    def test_full_design_system(self):
        """Full design system should produce correct Tailwind config."""
        ds = {
            'colors': {
                'primary': '#FF0000',
                'secondary': '#00FF00',
                'background': '#FFFFFF',
            },
            'typography': {'fontFamily': 'Inter'},
        }
        config = generate_tailwind_config(ds)
        self.assertEqual(config['colors']['primary'], '#FF0000')
        self.assertEqual(config['fontFamily']['sans'], ['Inter'])

    def test_empty_design_system(self):
        """Empty design system should produce empty config sections."""
        config = generate_tailwind_config({})
        self.assertEqual(config['colors'], {})
        self.assertEqual(config['fontFamily'], {})
        self.assertEqual(config['borderRadius'], {})
        self.assertEqual(config['boxShadow'], {})

    def test_none_values_filtered_from_colors(self):
        """None values should be filtered out from colors."""
        ds = {'colors': {'primary': '#FF0000', 'secondary': None}}
        config = generate_tailwind_config(ds)
        self.assertIn('primary', config['colors'])
        self.assertNotIn('secondary', config['colors'])


class TestDesignSystemResult(unittest.TestCase):
    """Tests for DesignSystemResult dataclass."""

    def test_success_state(self):
        """Success result should have success=True and data."""
        r = DesignSystemResult(success=True, data={'colors': {}})
        self.assertTrue(r.success)
        self.assertIsNotNone(r.data)
        self.assertIsNone(r.error)

    def test_failure_state(self):
        """Failure result should have success=False and error message."""
        r = DesignSystemResult(success=False, error='Something went wrong')
        self.assertFalse(r.success)
        self.assertIsNone(r.data)
        self.assertEqual(r.error, 'Something went wrong')


class TestMergeResults(unittest.TestCase):
    """Tests for DesignSystemService._merge_results()."""

    def setUp(self):
        self.service = DesignSystemService.__new__(DesignSystemService)

    def test_empty_list(self):
        """Empty list should return empty dict."""
        self.assertEqual(self.service._merge_results([]), {})

    def test_single_item(self):
        """Single item should be returned as-is."""
        item = {'colors': {'primary': '#FF0000'}}
        self.assertEqual(self.service._merge_results([item]), item)

    def test_multiple_items_merge_colors(self):
        """Multiple items should merge colors (first non-empty wins)."""
        r1 = {'colors': {'primary': '#FF0000', 'secondary': ''}}
        r2 = {'colors': {'primary': '#00FF00', 'secondary': '#0000FF'}}
        merged = self.service._merge_results([r1, r2])
        self.assertEqual(merged['colors']['primary'], '#FF0000')
        self.assertEqual(merged['colors']['secondary'], '#0000FF')

    def test_multiple_items_merge_style_rules(self):
        """Multiple items should merge styleRules as union."""
        r1 = {'styleRules': ['rule1', 'rule2']}
        r2 = {'styleRules': ['rule2', 'rule3']}
        merged = self.service._merge_results([r1, r2])
        self.assertEqual(set(merged['styleRules']), {'rule1', 'rule2', 'rule3'})


# =============================================================================
# Task Helper Tests
# =============================================================================


class TestTaskProgress(unittest.TestCase):
    """Tests for TaskProgress dataclass."""

    def test_to_dict(self):
        """to_dict should serialize all fields."""
        tp = TaskProgress(
            task_id='abc',
            status=TaskStatus.PROCESSING,
            progress=50,
            current_step='analysis',
            total_steps=3,
            current_step_number=2,
            message='Analyzing...',
            result=None,
            error=None,
        )
        d = tp.to_dict()
        self.assertEqual(d['task_id'], 'abc')
        self.assertEqual(d['status'], TaskStatus.PROCESSING)
        self.assertEqual(d['progress'], 50)
        self.assertEqual(d['current_step'], 'analysis')
        self.assertEqual(d['total_steps'], 3)
        self.assertEqual(d['current_step_number'], 2)
        self.assertEqual(d['message'], 'Analyzing...')
        self.assertIsNone(d['result'])
        self.assertIsNone(d['error'])


class TestGetTaskCacheKey(unittest.TestCase):
    """Tests for get_task_cache_key()."""

    def test_correct_format(self):
        """Cache key should follow the expected format."""
        key = get_task_cache_key('my-task-id')
        self.assertEqual(key, 'design_system_task:my-task-id')


class TestParseLLMJson(unittest.TestCase):
    """Tests for _parse_llm_json()."""

    def test_valid_json(self):
        """Valid JSON string should be parsed correctly."""
        result = _parse_llm_json('{"key": "value"}')
        self.assertEqual(result, {'key': 'value'})

    def test_invalid_json_raises(self):
        """Completely unparseable content should raise ValueError."""
        with self.assertRaises(ValueError):
            _parse_llm_json('this is not json at all []')

    def test_repairs_common_issues(self):
        """json_repair should fix trailing commas and similar issues."""
        result = _parse_llm_json('{"key": "value",}')
        self.assertEqual(result, {'key': 'value'})


class TestExtractStyleFromText(unittest.TestCase):
    """Tests for _extract_style_from_text()."""

    def test_detects_neumorphism(self):
        """Should detect neumorphism keywords."""
        self.assertEqual(_extract_style_from_text('This uses neumorphism style'), 'neumorphism')

    def test_detects_glassmorphism(self):
        """Should detect glassmorphism keywords."""
        self.assertEqual(_extract_style_from_text('Frosted glass effect'), 'glassmorphism')

    def test_detects_material(self):
        """Should detect material design keywords."""
        self.assertEqual(_extract_style_from_text('Uses Material Design elevation'), 'material')

    def test_detects_gradient(self):
        """Should detect gradient keywords."""
        self.assertEqual(_extract_style_from_text('Beautiful gradient backgrounds'), 'gradient')

    def test_detects_playful(self):
        """Should detect playful keywords."""
        self.assertEqual(_extract_style_from_text('Organic bubble shapes'), 'playful')

    def test_detects_flat(self):
        """Should detect flat design keywords."""
        self.assertEqual(_extract_style_from_text('Clean flat design minimal'), 'flat')

    def test_unknown_returns_general(self):
        """Unknown style should return 'general'."""
        self.assertEqual(_extract_style_from_text('Some random text'), 'general')


class TestMergeDesignSystems(unittest.TestCase):
    """Tests for merge_design_systems()."""

    def test_empty_returns_empty(self):
        """Empty list should return empty dict."""
        self.assertEqual(merge_design_systems([]), {})

    def test_single_returns_same(self):
        """Single item should be returned as-is."""
        item = {'colors': {'primary': '#FF0000'}}
        self.assertEqual(merge_design_systems([item]), item)

    def test_multiple_merges(self):
        """Multiple items should merge correctly."""
        r1 = {'colors': {'primary': '#FF0000', 'secondary': ''}}
        r2 = {'colors': {'primary': '', 'secondary': '#0000FF'}}
        merged = merge_design_systems([r1, r2])
        self.assertEqual(merged['colors']['primary'], '#FF0000')
        self.assertEqual(merged['colors']['secondary'], '#0000FF')

    def test_filters_out_raw_response(self):
        """Results with raw_response should be filtered out."""
        r1 = {'raw_response': 'invalid'}
        r2 = {'colors': {'primary': '#FF0000'}}
        merged = merge_design_systems([r1, r2])
        self.assertEqual(merged['colors']['primary'], '#FF0000')


class TestMergeColorDicts(unittest.TestCase):
    """Tests for merge_color_dicts()."""

    def test_empty_returns_empty(self):
        """Empty list should return empty dict."""
        self.assertEqual(merge_color_dicts([]), {})

    def test_single_returns_same(self):
        """Single dict should be returned as-is."""
        d = {'primary': '#FF0000'}
        self.assertEqual(merge_color_dicts([d]), d)

    def test_multiple_first_non_empty_wins(self):
        """First non-empty value should win."""
        d1 = {'primary': '#FF0000', 'secondary': ''}
        d2 = {'primary': '#00FF00', 'secondary': '#0000FF'}
        merged = merge_color_dicts([d1, d2])
        self.assertEqual(merged['primary'], '#FF0000')
        self.assertEqual(merged['secondary'], '#0000FF')


# =============================================================================
# Serializer Tests
# =============================================================================


class TestDesignSystemCreateSerializer(TestCase):
    """Tests for DesignSystemCreateSerializer."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='create@test.com', password='StrongP@ss123!'
        )
        self.factory = APIRequestFactory()

    def test_valid_data_creates_with_user(self):
        """Valid data should create a DesignSystem associated with the user."""
        request = self.factory.post('/fake/')
        request.user = self.user
        data = {'name': 'Test DS', 'description': 'A test design system'}
        serializer = DesignSystemCreateSerializer(
            data=data, context={'request': request}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertEqual(instance.user, self.user)
        self.assertEqual(instance.name, 'Test DS')


class TestDesignSystemUpdateSerializer(TestCase):
    """Tests for DesignSystemUpdateSerializer."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='update@test.com', password='StrongP@ss123!'
        )
        self.ds = DesignSystem.objects.create(
            user=self.user, name='Original', description='Old desc'
        )

    def test_updates_name_and_description(self):
        """Should update name and description fields."""
        serializer = DesignSystemUpdateSerializer(
            self.ds, data={'name': 'New Name', 'description': 'New desc'},
            partial=True,
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        self.ds.refresh_from_db()
        self.assertEqual(self.ds.name, 'New Name')
        self.assertEqual(self.ds.description, 'New desc')


class TestImageUploadSerializer(TestCase):
    """Tests for ImageUploadSerializer."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='imgup@test.com', password='StrongP@ss123!'
        )
        self.ds = DesignSystem.objects.create(user=self.user, name='ImgUp')

    def test_valid_base64(self):
        """Valid base64 image data should pass validation."""
        data = {'data': TINY_PNG, 'mime_type': 'image/png'}
        serializer = ImageUploadSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        img = serializer.create_image(self.ds)
        self.assertIsNotNone(img.id)
        self.assertEqual(img.mime_type, 'image/png')

    def test_valid_base64_with_data_url_prefix(self):
        """Data URL prefix should be stripped before decoding."""
        prefixed = f'data:image/png;base64,{TINY_PNG}'
        data = {'data': prefixed, 'mime_type': 'image/png'}
        serializer = ImageUploadSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        img = serializer.create_image(self.ds)
        self.assertIsNotNone(img.id)

    def test_invalid_base64(self):
        """Invalid base64 data should raise a validation error on create."""
        data = {'data': '!!!not-base64!!!', 'mime_type': 'image/png'}
        serializer = ImageUploadSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        with self.assertRaises(Exception):
            serializer.create_image(self.ds)


class TestStartAnalysisSerializer(unittest.TestCase):
    """Tests for StartAnalysisSerializer."""

    def test_validate_images_rejects_more_than_one(self):
        """Should reject more than 1 image."""
        data = {
            'images': [
                {'data': TINY_PNG, 'mime_type': 'image/png'},
                {'data': TINY_PNG, 'mime_type': 'image/png'},
            ]
        }
        serializer = StartAnalysisSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('images', serializer.errors)


class TestGenerateDesignSystemRequestSerializer(unittest.TestCase):
    """Tests for GenerateDesignSystemRequestSerializer."""

    def test_at_least_one_image_required(self):
        """Should require at least 1 image."""
        data = {'images': []}
        serializer = GenerateDesignSystemRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('images', serializer.errors)

    def test_max_ten_images(self):
        """Should reject more than 10 images."""
        data = {
            'images': [
                {'data': TINY_PNG, 'mime_type': 'image/png'}
                for _ in range(11)
            ]
        }
        serializer = GenerateDesignSystemRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('images', serializer.errors)


# =============================================================================
# View / API Tests
# =============================================================================


class DesignSystemAPITestBase(APITestCase):
    """Shared helpers for design system API tests."""

    SYSTEMS_URL = '/api/design-system/systems/'

    def _create_user(self, email='dsuser@test.com', password='StrongP@ss123!'):
        return User.objects.create_user(email=email, password=password)

    def _authenticate(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}'
        )

    def _create_ds(self, user, name='Test DS', **kwargs):
        return DesignSystem.objects.create(user=user, name=name, **kwargs)


class TestDesignSystemCRUD(DesignSystemAPITestBase):
    """Tests for Design System CRUD operations."""

    def setUp(self):
        self.user = self._create_user()
        self._authenticate(self.user)

    def test_list_own_systems(self):
        """GET should list only the authenticated user's design systems."""
        self._create_ds(self.user, 'DS1')
        self._create_ds(self.user, 'DS2')
        response = self.client.get(self.SYSTEMS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 2)

    def test_create(self):
        """POST should create a new design system."""
        data = {'name': 'New DS', 'description': 'A new design system'}
        response = self.client.post(self.SYSTEMS_URL, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New DS')

    def test_retrieve(self):
        """GET with pk should retrieve a design system."""
        ds = self._create_ds(self.user, 'Retrieve DS')
        url = f'{self.SYSTEMS_URL}{ds.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Retrieve DS')

    def test_update(self):
        """PUT should update a design system."""
        ds = self._create_ds(self.user, 'Old Name')
        url = f'{self.SYSTEMS_URL}{ds.id}/'
        data = {'name': 'New Name', 'description': 'Updated'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'New Name')

    def test_partial_update(self):
        """PATCH should partially update a design system."""
        ds = self._create_ds(self.user, 'Partial')
        url = f'{self.SYSTEMS_URL}{ds.id}/'
        data = {'description': 'Patched'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Patched')

    def test_delete(self):
        """DELETE should remove a design system."""
        ds = self._create_ds(self.user, 'Delete Me')
        url = f'{self.SYSTEMS_URL}{ds.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(DesignSystem.objects.filter(id=ds.id).exists())


class TestDesignSystemIsolation(DesignSystemAPITestBase):
    """Test that users can only see their own design systems."""

    def test_users_cannot_see_others_systems(self):
        """User A should not see User B's design systems."""
        user_a = self._create_user(email='a@test.com')
        user_b = self._create_user(email='b@test.com')
        self._create_ds(user_a, 'A DS')
        self._create_ds(user_b, 'B DS')

        self._authenticate(user_a)
        response = self.client.get(self.SYSTEMS_URL)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'A DS')

    def test_cannot_retrieve_others_system(self):
        """User A should not retrieve User B's design system by ID."""
        user_a = self._create_user(email='a2@test.com')
        user_b = self._create_user(email='b2@test.com')
        ds_b = self._create_ds(user_b, 'B DS')

        self._authenticate(user_a)
        url = f'{self.SYSTEMS_URL}{ds_b.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestUploadImages(DesignSystemAPITestBase):
    """Tests for the upload_images endpoint."""

    def setUp(self):
        self.user = self._create_user()
        self._authenticate(self.user)
        self.ds = self._create_ds(self.user, 'Upload DS')

    def _upload_url(self):
        return f'{self.SYSTEMS_URL}{self.ds.id}/upload_images/'

    def test_upload_success(self):
        """POST with valid image data should upload successfully."""
        data = {
            'images': [{'data': TINY_PNG, 'mime_type': 'image/png'}]
        }
        response = self.client.post(self._upload_url(), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('uploaded', response.data)

    def test_upload_no_images_error(self):
        """POST with no images should return 400."""
        data = {'images': []}
        response = self.client.post(self._upload_url(), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_more_than_one_image_error(self):
        """POST with more than 1 image should return 400."""
        data = {
            'images': [
                {'data': TINY_PNG, 'mime_type': 'image/png'},
                {'data': TINY_PNG, 'mime_type': 'image/png'},
            ]
        }
        response = self.client.post(self._upload_url(), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestDeleteImage(DesignSystemAPITestBase):
    """Tests for the delete_image endpoint."""

    def setUp(self):
        self.user = self._create_user()
        self._authenticate(self.user)
        self.ds = self._create_ds(self.user, 'Del DS')

    def _create_image(self):
        img_data = base64.b64decode(TINY_PNG)
        return DesignSystemImage.objects.create(
            design_system=self.ds,
            name='test.png',
            image=ContentFile(img_data, name='test.png'),
            mime_type='image/png',
        )

    def test_delete_success(self):
        """DELETE with correct image ID should succeed."""
        img = self._create_image()
        url = f'{self.SYSTEMS_URL}{self.ds.id}/images/{img.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(DesignSystemImage.objects.filter(id=img.id).exists())

    def test_delete_wrong_image_id(self):
        """DELETE with wrong image ID should return 400."""
        self._create_image()
        wrong_id = uuid.uuid4()
        url = f'{self.SYSTEMS_URL}{self.ds.id}/images/{wrong_id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_no_image(self):
        """DELETE when no image exists should return 404."""
        fake_id = uuid.uuid4()
        url = f'{self.SYSTEMS_URL}{self.ds.id}/images/{fake_id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


if __name__ == '__main__':
    unittest.main()
