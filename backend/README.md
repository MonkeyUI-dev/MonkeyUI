# Backend

Django + DRF backend API for designmonkey.

## Setup

### Prerequisites
- Python 3.14+
- PostgreSQL 15+ with pgvector extension
- uv (Python package manager)

### Installation

1. Install uv (if not installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Install dependencies:
```bash
uv sync
```

3. Create `.env` file from example:
```bash
cp .env.example .env
```

4. Update `.env` with your database credentials.

5. Setup PostgreSQL database:
```bash
# Create database
createdb designmonkey_dev

# Enable pgvector extension
psql designmonkey_dev -c 'CREATE EXTENSION vector;'
```

6. Run migrations:
```bash
uv run python manage.py migrate
```

7. Create superuser:
```bash
uv run python manage.py createsuperuser
```

8. Run development server:
```bash
uv run python manage.py runserver
```

The API will be available at `http://localhost:8000`

## Project Structure

```
backend/
├── config/                 # Django project configuration
│   ├── settings.py        # Main settings
│   ├── urls.py            # Root URL configuration
│   ├── wsgi.py
│   └── asgi.py
├── apps/                   # Django applications
│   └── core/              # Core app
│       ├── models.py
│       ├── views.py
│       ├── serializers.py
│       ├── urls.py
│       └── admin.py
├── locale/                 # i18n translation files
├── manage.py
├── pyproject.toml         # Python dependencies (uv)
└── .env
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/api/docs/
- OpenAPI Schema: http://localhost:8000/api/schema/

## Internationalization

### Marking strings for translation

In Python code:
```python
from django.utils.translation import gettext_lazy as _

message = _("Hello, world!")
```

### Generating translation files

```bash
# Create/update message files
uv run python manage.py makemessages -l zh_Hans

# Compile translations
uv run python manage.py compilemessages
```

## Database with pgvector

To use pgvector in your models:

```python
from pgvector.django import VectorField

class Document(models.Model):
    embedding = VectorField(dimensions=1536)
```

## Running Tests

```bash
uv run pytest
```

## Code Style

Format code with Black:
```bash
uv run black .
```

Check code style with flake8:
```bash
uv run flake8
```

## Environment Variables

See `.env.example` for all available environment variables.
