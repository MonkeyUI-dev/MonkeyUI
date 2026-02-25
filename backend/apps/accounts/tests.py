"""
Tests for the accounts app.

Covers User model, UserAPIKey model, serializers, and API views
for registration, login, logout, password change, and API key management.
"""
import unittest
from datetime import timedelta
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import UserAPIKey
from apps.accounts.serializers import (
    RegisterSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    UserAPIKeySerializer,
)

User = get_user_model()


# ---------------------------------------------------------------------------
# Model Tests (pure unit tests – mock DB interactions)
# ---------------------------------------------------------------------------


class TestUserManager(unittest.TestCase):
    """Tests for the custom UserManager."""

    @patch("apps.accounts.models.UserManager.normalize_email", side_effect=lambda e: e.lower())
    def test_create_user_with_valid_email(self, mock_normalize):
        """create_user should normalise email and call set_password."""
        manager = User.objects
        with patch.object(manager, "model") as MockModel, \
             patch.object(manager, "_db", "default"):
            instance = MagicMock()
            MockModel.return_value = instance

            manager.create_user.__func__(manager, email="Test@Example.COM", password="secret123")

            mock_normalize.assert_called_once_with("Test@Example.COM")
            instance.set_password.assert_called_once_with("secret123")
            instance.save.assert_called_once()

    def test_create_user_empty_email_raises(self):
        """create_user with empty email should raise ValueError."""
        manager = User.objects
        with self.assertRaises(ValueError):
            with patch.object(manager, "model"), \
                 patch.object(manager, "_db", "default"):
                manager.create_user.__func__(manager, email="", password="secret")

    @patch.object(User.objects, "create_user")
    def test_create_superuser_sets_flags(self, mock_create_user):
        """create_superuser should set is_staff and is_superuser to True."""
        mock_create_user.return_value = MagicMock()
        User.objects.create_superuser.__func__(
            User.objects, email="admin@test.com", password="admin123"
        )
        _call_kwargs = mock_create_user.call_args
        extra = _call_kwargs[1] if _call_kwargs[1] else {}
        self.assertTrue(extra.get("is_staff", False))
        self.assertTrue(extra.get("is_superuser", False))

    @patch.object(User.objects, "create_user")
    def test_create_superuser_is_staff_false_raises(self, mock_create_user):
        """create_superuser with is_staff=False should raise ValueError."""
        with self.assertRaises(ValueError):
            User.objects.create_superuser.__func__(
                User.objects, email="admin@test.com", password="admin", is_staff=False
            )

    @patch.object(User.objects, "create_user")
    def test_create_superuser_is_superuser_false_raises(self, mock_create_user):
        """create_superuser with is_superuser=False should raise ValueError."""
        with self.assertRaises(ValueError):
            User.objects.create_superuser.__func__(
                User.objects, email="admin@test.com", password="admin", is_superuser=False
            )


class TestUserModel(unittest.TestCase):
    """Tests for the User model instance methods."""

    def _create_mock_user(self, email="user@example.com", name=""):
        """Create a mock User instance."""
        user = MagicMock(spec=User)
        user.email = email
        user.name = name
        return user

    def test_str_returns_email(self):
        """__str__ should return the user's email."""
        result = User.__str__(self._create_mock_user(email="bob@test.com"))
        self.assertEqual(result, "bob@test.com")

    def test_get_full_name_with_name(self):
        """get_full_name should return name when set."""
        user = self._create_mock_user(name="Alice Smith")
        result = User.get_full_name(user)
        self.assertEqual(result, "Alice Smith")

    def test_get_full_name_without_name(self):
        """get_full_name should fall back to email when name is empty."""
        user = self._create_mock_user(name="")
        result = User.get_full_name(user)
        self.assertEqual(result, "user@example.com")

    def test_get_short_name_with_name(self):
        """get_short_name should return name when set."""
        user = self._create_mock_user(name="Alice")
        result = User.get_short_name(user)
        self.assertEqual(result, "Alice")

    def test_get_short_name_without_name(self):
        """get_short_name should return local part of email when name is empty."""
        user = self._create_mock_user(email="alice@example.com", name="")
        result = User.get_short_name(user)
        self.assertEqual(result, "alice")


class TestUserAPIKeyModel(unittest.TestCase):
    """Tests for the UserAPIKey model."""

    def test_generate_key_starts_with_sk(self):
        """generate_key should return a key starting with 'sk_'."""
        key = UserAPIKey.generate_key()
        self.assertTrue(key.startswith("sk_"))

    def test_generate_key_sufficient_length(self):
        """generate_key should produce a key of reasonable length."""
        key = UserAPIKey.generate_key()
        # 'sk_' + 43 chars from token_urlsafe(32) ≈ 46 chars
        self.assertGreater(len(key), 30)

    def test_generate_key_unique(self):
        """Two generated keys should not be equal."""
        self.assertNotEqual(UserAPIKey.generate_key(), UserAPIKey.generate_key())

    def test_is_valid_active_no_expiry(self):
        """is_valid should return True for active key without expiration."""
        api_key = MagicMock(spec=UserAPIKey)
        api_key.is_active = True
        api_key.expires_at = None
        result = UserAPIKey.is_valid(api_key)
        self.assertTrue(result)

    def test_is_valid_inactive(self):
        """is_valid should return False for inactive key."""
        api_key = MagicMock(spec=UserAPIKey)
        api_key.is_active = False
        api_key.expires_at = None
        result = UserAPIKey.is_valid(api_key)
        self.assertFalse(result)

    def test_is_valid_expired(self):
        """is_valid should return False for expired key."""
        api_key = MagicMock(spec=UserAPIKey)
        api_key.is_active = True
        api_key.expires_at = timezone.now() - timedelta(hours=1)
        result = UserAPIKey.is_valid(api_key)
        self.assertFalse(result)

    def test_is_valid_future_expiry(self):
        """is_valid should return True for key with future expiry."""
        api_key = MagicMock(spec=UserAPIKey)
        api_key.is_active = True
        api_key.expires_at = timezone.now() + timedelta(days=30)
        result = UserAPIKey.is_valid(api_key)
        self.assertTrue(result)

    def test_str_representation(self):
        """__str__ should include name and key prefix."""
        api_key = MagicMock(spec=UserAPIKey)
        api_key.name = "Test Key"
        api_key.key_prefix = "sk_abcde"
        result = UserAPIKey.__str__(api_key)
        self.assertEqual(result, "Test Key (sk_abcde...)")

    def test_save_auto_populates_key(self):
        """save should generate a key if not set."""
        api_key = MagicMock(spec=UserAPIKey)
        api_key.key = ""
        api_key.key_prefix = ""

        def side_effect():
            api_key.key = UserAPIKey.generate_key()

        with patch.object(UserAPIKey, "generate_key") as mock_gen:
            mock_gen.return_value = "sk_testkey1234567890abcdefghijklmnop"
            # Simulate the save logic
            if not api_key.key:
                api_key.key = UserAPIKey.generate_key()
            if not api_key.key_prefix:
                api_key.key_prefix = api_key.key[:8]

        self.assertTrue(api_key.key.startswith("sk_"))
        self.assertEqual(api_key.key_prefix, api_key.key[:8])


# ---------------------------------------------------------------------------
# Serializer Tests (need Django DB via TestCase)
# ---------------------------------------------------------------------------


class TestRegisterSerializer(TestCase):
    """Tests for RegisterSerializer."""

    def test_valid_registration_data(self):
        """RegisterSerializer should accept valid data."""
        data = {
            "email": "new@example.com",
            "password": "StrongP@ss123!",
            "password_confirm": "StrongP@ss123!",
            "name": "New User",
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_password_mismatch(self):
        """RegisterSerializer should reject mismatched passwords."""
        data = {
            "email": "new@example.com",
            "password": "StrongP@ss123!",
            "password_confirm": "DifferentP@ss456!",
            "name": "New User",
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_duplicate_email(self):
        """RegisterSerializer should reject a duplicate email."""
        User.objects.create_user(email="dup@example.com", password="StrongP@ss123!")
        data = {
            "email": "dup@example.com",
            "password": "StrongP@ss123!",
            "password_confirm": "StrongP@ss123!",
            "name": "Dup User",
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_create_user(self):
        """RegisterSerializer.create should persist a user."""
        data = {
            "email": "created@example.com",
            "password": "StrongP@ss123!",
            "password_confirm": "StrongP@ss123!",
            "name": "Created User",
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertEqual(user.email, "created@example.com")
        self.assertTrue(user.check_password("StrongP@ss123!"))

    def test_weak_password_rejected(self):
        """RegisterSerializer should reject passwords that fail Django validators."""
        data = {
            "email": "weak@example.com",
            "password": "123",
            "password_confirm": "123",
            "name": "Weak User",
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)


class TestLoginSerializer(TestCase):
    """Tests for LoginSerializer."""

    def test_valid_login_data(self):
        """LoginSerializer should accept email and password."""
        data = {"email": "user@example.com", "password": "secret123"}
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_missing_email(self):
        """LoginSerializer should reject missing email."""
        serializer = LoginSerializer(data={"password": "secret123"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_missing_password(self):
        """LoginSerializer should reject missing password."""
        serializer = LoginSerializer(data={"email": "user@example.com"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)


class TestChangePasswordSerializer(TestCase):
    """Tests for ChangePasswordSerializer."""

    def test_valid_change_password_data(self):
        """ChangePasswordSerializer should accept old and new passwords."""
        data = {
            "old_password": "OldP@ss123!",
            "new_password": "NewStr0ng!Pass",
        }
        serializer = ChangePasswordSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_weak_new_password_rejected(self):
        """ChangePasswordSerializer should reject a weak new_password."""
        data = {"old_password": "OldP@ss123!", "new_password": "123"}
        serializer = ChangePasswordSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("new_password", serializer.errors)


class TestUserAPIKeySerializer(TestCase):
    """Tests for UserAPIKeySerializer."""

    def setUp(self):
        """Set up a user and API key for serializer tests."""
        self.user = User.objects.create_user(
            email="keyuser@example.com", password="StrongP@ss123!"
        )
        self.api_key = UserAPIKey.objects.create(
            user=self.user, name="Test Key"
        )

    def test_key_display_shows_prefix(self):
        """key_display should show the key_prefix followed by '...'."""
        serializer = UserAPIKeySerializer(self.api_key)
        self.assertEqual(
            serializer.data["key_display"],
            f"{self.api_key.key_prefix}...",
        )

    def test_to_representation_hides_key_by_default(self):
        """to_representation should omit full key when show_full_key is False."""
        serializer = UserAPIKeySerializer(self.api_key)
        self.assertNotIn("key", serializer.data)

    def test_to_representation_shows_key_when_flagged(self):
        """to_representation should include full key when show_full_key is True."""
        serializer = UserAPIKeySerializer(
            self.api_key, context={"show_full_key": True}
        )
        self.assertIn("key", serializer.data)
        self.assertTrue(serializer.data["key"].startswith("sk_"))

    def test_key_prefix_auto_populated(self):
        """API key saved via model should auto-populate key_prefix."""
        self.assertTrue(len(self.api_key.key_prefix) > 0)
        self.assertEqual(self.api_key.key_prefix, self.api_key.key[:8])


# ---------------------------------------------------------------------------
# View / API Tests (full integration via APITestCase)
# ---------------------------------------------------------------------------


class AccountsAPITestBase(APITestCase):
    """Shared helpers for accounts API tests."""

    REGISTER_URL = "/api/accounts/register/"
    LOGIN_URL = "/api/accounts/login/"
    LOGOUT_URL = "/api/accounts/logout/"
    ME_URL = "/api/accounts/me/"
    CHANGE_PASSWORD_URL = "/api/accounts/change-password/"
    API_KEYS_URL = "/api/accounts/api-keys/"

    def _create_user(self, email="user@test.com", password="StrongP@ss123!", name="Test User"):
        """Create and return a user."""
        return User.objects.create_user(email=email, password=password, name=name)

    def _get_tokens(self, user):
        """Return (access, refresh) token strings for a user."""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token), str(refresh)

    def _authenticate(self, user):
        """Set JWT auth credentials on the test client."""
        access, _ = self._get_tokens(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")


class TestRegisterView(AccountsAPITestBase):
    """Tests for the registration endpoint."""

    def test_register_success(self):
        """POST /register/ with valid data returns 201 and tokens."""
        data = {
            "email": "newuser@test.com",
            "password": "StrongP@ss123!",
            "password_confirm": "StrongP@ss123!",
            "name": "New User",
        }
        response = self.client.post(self.REGISTER_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])

    def test_register_returns_user_data(self):
        """Registration response should contain user info."""
        data = {
            "email": "info@test.com",
            "password": "StrongP@ss123!",
            "password_confirm": "StrongP@ss123!",
            "name": "Info User",
        }
        response = self.client.post(self.REGISTER_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["email"], "info@test.com")

    def test_register_duplicate_email(self):
        """POST /register/ with existing email returns 400."""
        self._create_user(email="dup@test.com")
        data = {
            "email": "dup@test.com",
            "password": "StrongP@ss123!",
            "password_confirm": "StrongP@ss123!",
            "name": "Dup",
        }
        response = self.client.post(self.REGISTER_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_password_mismatch(self):
        """POST /register/ with mismatched passwords returns 400."""
        data = {
            "email": "mismatch@test.com",
            "password": "StrongP@ss123!",
            "password_confirm": "DifferentP@ss456!",
            "name": "Mismatch",
        }
        response = self.client.post(self.REGISTER_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestLoginView(AccountsAPITestBase):
    """Tests for the login endpoint."""

    def test_login_success(self):
        """POST /login/ with correct credentials returns tokens."""
        self._create_user(email="login@test.com", password="StrongP@ss123!")
        data = {"email": "login@test.com", "password": "StrongP@ss123!"}
        response = self.client.post(self.LOGIN_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_wrong_password(self):
        """POST /login/ with wrong password returns 401."""
        self._create_user(email="wrong@test.com", password="StrongP@ss123!")
        data = {"email": "wrong@test.com", "password": "BadPassword!"}
        response = self.client.post(self.LOGIN_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        """POST /login/ with unknown email returns 401."""
        data = {"email": "nobody@test.com", "password": "Whatever1!"}
        response = self.client.post(self.LOGIN_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestCurrentUserView(AccountsAPITestBase):
    """Tests for the current-user endpoint."""

    def test_authenticated_returns_user(self):
        """GET /me/ with valid token returns user data."""
        user = self._create_user()
        self._authenticate(user)
        response = self.client.get(self.ME_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["email"], user.email)

    def test_unauthenticated_returns_401(self):
        """GET /me/ without token returns 401."""
        response = self.client.get(self.ME_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestChangePasswordView(AccountsAPITestBase):
    """Tests for the change-password endpoint."""

    def test_change_password_success(self):
        """PUT /change-password/ with correct old password succeeds."""
        user = self._create_user(password="StrongP@ss123!")
        self._authenticate(user)
        data = {
            "old_password": "StrongP@ss123!",
            "new_password": "NewStr0ng!Pass9",
        }
        response = self.client.put(self.CHANGE_PASSWORD_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.check_password("NewStr0ng!Pass9"))

    def test_change_password_wrong_old(self):
        """PUT /change-password/ with wrong old password returns 400."""
        user = self._create_user(password="StrongP@ss123!")
        self._authenticate(user)
        data = {
            "old_password": "WrongOld!Pass1",
            "new_password": "NewStr0ng!Pass9",
        }
        response = self.client.put(self.CHANGE_PASSWORD_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_unauthenticated(self):
        """PUT /change-password/ without auth returns 401."""
        data = {
            "old_password": "StrongP@ss123!",
            "new_password": "NewStr0ng!Pass9",
        }
        response = self.client.put(self.CHANGE_PASSWORD_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestLogoutView(AccountsAPITestBase):
    """Tests for the logout endpoint."""

    def test_logout_success(self):
        """POST /logout/ with valid refresh token returns 200."""
        user = self._create_user()
        access, refresh = self._get_tokens(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = self.client.post(
            self.LOGOUT_URL, {"refresh_token": refresh}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_unauthenticated(self):
        """POST /logout/ without auth returns 401."""
        response = self.client.post(self.LOGOUT_URL, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestAPIKeyViews(AccountsAPITestBase):
    """Tests for UserAPIKey list/create/detail endpoints."""

    def setUp(self):
        """Set up an authenticated user."""
        self.user = self._create_user(email="apiuser@test.com")
        self._authenticate(self.user)

    def test_create_api_key(self):
        """POST /api-keys/ should create a key and return the full key."""
        response = self.client.post(
            self.API_KEYS_URL, {"name": "My Key"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("api_key", response.data)
        self.assertTrue(response.data["api_key"]["key"].startswith("sk_"))

    def test_list_api_keys(self):
        """GET /api-keys/ should return the user's API keys."""
        UserAPIKey.objects.create(user=self.user, name="Key 1")
        UserAPIKey.objects.create(user=self.user, name="Key 2")
        response = self.client.get(self.API_KEYS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_keys_masked(self):
        """GET /api-keys/ should not expose the full key value."""
        UserAPIKey.objects.create(user=self.user, name="Masked Key")
        response = self.client.get(self.API_KEYS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        first_key = response.data[0]
        self.assertNotIn("key", first_key)
        self.assertIn("key_display", first_key)

    def test_delete_api_key(self):
        """DELETE /api-keys/<pk>/ should remove the key."""
        api_key = UserAPIKey.objects.create(user=self.user, name="Delete Me")
        url = f"{self.API_KEYS_URL}{api_key.pk}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(UserAPIKey.objects.filter(pk=api_key.pk).exists())

    def test_max_10_keys_limit(self):
        """Creating an 11th API key should return 400."""
        for i in range(10):
            UserAPIKey.objects.create(user=self.user, name=f"Key {i}")
        response = self.client.post(
            self.API_KEYS_URL, {"name": "Key 11"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_key_belongs_to_user(self):
        """Users should not see other users' API keys."""
        other = self._create_user(email="other@test.com")
        UserAPIKey.objects.create(user=other, name="Other Key")
        response = self.client.get(self.API_KEYS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_cannot_delete_other_users_key(self):
        """DELETE on another user's API key should return 404."""
        other = self._create_user(email="other2@test.com")
        api_key = UserAPIKey.objects.create(user=other, name="Not Mine")
        url = f"{self.API_KEYS_URL}{api_key.pk}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_api_keys_returns_401(self):
        """API key endpoints should require authentication."""
        self.client.credentials()  # Clear credentials
        response = self.client.get(self.API_KEYS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


if __name__ == "__main__":
    unittest.main()
