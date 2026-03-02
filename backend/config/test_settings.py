"""
Test settings for MonkeyUI backend.
Uses SQLite in-memory for fast test execution without requiring PostgreSQL.
"""
from config.settings import *  # noqa: F401,F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Use faster password hasher for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable password validators for tests
AUTH_PASSWORD_VALIDATORS = []

# Use locmem cache for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Use in-memory file storage
DEFAULT_FILE_STORAGE = 'django.core.files.storage.InMemoryStorage'
