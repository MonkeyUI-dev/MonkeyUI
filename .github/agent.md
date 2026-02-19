# Agent Instructions for MonkeyUI

## Project Overview
This is a monorepo full-stack application with a React frontend and Django backend, focused on design system creation powered by AI/LLM.

### Tech Stack Summary
| Component       | Version / Tool         |
|-----------------|------------------------|
| React           | 19.0.0                 |
| Vite            | 6.0.0                  |
| TailwindCSS     | 3.4                    |
| Django          | 6.0.1                  |
| DRF             | 3.14                   |
| Python          | >=3.14                 |
| Node            | >=18.0.0               |
| Package Manager | uv (backend), npm (frontend) |
| Database        | PostgreSQL 16 + pgvector |
| Cache / Queue   | Redis 7 + Celery       |
| Auth            | JWT (SimpleJWT)        |
| AI / LLM        | OpenAI, Gemini, OpenRouter |
| Deployment      | Fly.io, Docker Compose |

## Code Standards

### General Guidelines
- **Primary Language**: English for all code, comments, documentation, and user-facing text
- **Internationalization**: Support i18n for English and Chinese languages
  - Always use i18n keys instead of hardcoded strings in UI components
  - Frontend: Use `react-i18next` with translation keys
  - Backend: Use Django's translation utilities (`gettext_lazy`)
- **Code Style**: Follow industry best practices for React and Django
- **Comments**: Write clear, concise comments in English

### Frontend (React 19 + Vite 6 + TailwindCSS 3.4)
- Use functional components with React Hooks
- All files use **JavaScript (JSX)** — no TypeScript in this project
- Use Shadcn/ui components when possible
- Additional UI libraries: Headless UI, Heroicons, Lucide React
- Routing: react-router-dom v7
- HTTP client: Axios
- Follow Tailwind utility-first approach
- Keep components small and focused
- Use proper semantic HTML
- Organize imports: React → Third-party → Local components → Utilities → Styles

**Frontend directory structure:**
```
frontend/src/
├── components/
│   ├── auth/           # Authentication components (ProtectedRoute)
│   ├── layout/         # Layout components (ConsoleLayout)
│   ├── ui/             # Shadcn/ui base components (Button, Alert, Pagination)
│   └── vibe/           # Vibe/design-system feature components
├── contexts/           # React context providers (AuthContext)
├── pages/              # Page components (Login, Register, VibeStudio, DesignWorkshop)
├── services/           # API service layer (auth, designSystem, apiKeys)
├── lib/                # Utility functions (api, utils)
├── i18n.js             # i18n configuration
├── App.jsx             # Main app component with routing
├── main.jsx            # Entry point
└── index.css           # Global styles + design system CSS variables
```

**Component Example:**
```jsx
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';

export function WelcomeButton() {
  const { t } = useTranslation();
  
  return (
    <Button className="bg-primary">
      {t('welcome.button')}
    </Button>
  );
}
```

### Backend (Django 6 + DRF 3.14)
- Package manager: **uv** (not pip/pipenv) — use `uv sync` to install deps, `uv run` to execute commands
- Follow Django project structure best practices
- Use class-based views or ViewSets for DRF
- Implement proper serializers for API endpoints
- Use environment variables for sensitive configuration
- Keep models focused and normalized
- Write comprehensive docstrings for views and serializers
- Use Django's translation utilities for all user-facing strings
- Custom user model: `AUTH_USER_MODEL = 'accounts.User'`
- Authentication: JWT via `djangorestframework-simplejwt`

**Backend directory structure:**
```
backend/
├── config/                     # Project configuration
│   ├── settings.py             # Django settings (DB, cache, LLM, storage, etc.)
│   ├── urls.py                 # Root URL configuration
│   ├── celery.py               # Celery app configuration
│   ├── wsgi.py / asgi.py
│   └── __init__.py
├── apps/
│   ├── accounts/               # User authentication & management
│   │   ├── models.py           # Custom User model
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── core/                   # Core functionality
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests.py
│   └── design_system/          # Design system features (main business logic)
│       ├── models.py
│       ├── serializers.py
│       ├── services.py         # Business logic
│       ├── tasks.py            # Celery async tasks
│       ├── views.py
│       ├── urls.py
│       ├── schema.py           # DRF Spectacular schema customizations
│       ├── llm/                # LLM provider integration
│       │   ├── config.py       # Provider configuration
│       │   └── providers.py    # LLM provider implementations
│       ├── mcp/                # Model Context Protocol integration
│       │   ├── server.py
│       │   ├── mcp_server.py
│       │   ├── views.py
│       │   └── tests.py
│       └── prompts/            # Prompt templates for LLM
├── manage.py
├── pyproject.toml              # Python dependencies (managed by uv)
└── uv.lock
```

**API View Example:**
```python
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users.
    Supports i18n for all response messages.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response({
            'message': _('User retrieved successfully'),
            'data': serializer.data
        })
```

### Database (PostgreSQL 16 + pgvector)
- Use meaningful table and column names in snake_case
- Always include created_at and updated_at timestamps
- Add appropriate indexes for query optimization
- Use pgvector for vector similarity search when needed
- Docker image: `pgvector/pgvector:pg16`

**Model Example:**
```python
from django.db import models
from django.utils.translation import gettext_lazy as _
from pgvector.django import VectorField

class Document(models.Model):
    title = models.CharField(max_length=255, help_text=_("Document title"))
    content = models.TextField(help_text=_("Document content"))
    embedding = VectorField(dimensions=1536)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Document")
        verbose_name_plural = _("Documents")
        ordering = ['-created_at']
```

### Async Tasks (Celery + Redis)
- Celery is configured in `backend/config/celery.py`
- Task modules are auto-discovered from installed apps
- Define tasks in each app's `tasks.py`
- Redis serves as both message broker and result backend
- Task time limit: 30 minutes

### LLM / AI Integration
- Supported providers: Gemini, OpenRouter (with OpenAI-compatible API)
- Provider config in `backend/config/settings.py` → `LLM_PROVIDERS`
- LLM logic in `backend/apps/design_system/llm/`
- MCP (Model Context Protocol) server in `backend/apps/design_system/mcp/`
- Provider selection via `DEFAULT_LLM_PROVIDER` env var

### File Storage
- Supports local file storage (default for development) and S3-compatible storage (CloudFlare R2, MinIO, AWS S3)
- Configured via `FILE_STORAGE_BACKEND` env var (`local` or `s3`)
- Uses `django-storages[s3]` + `boto3` for cloud storage

## Design System

MonkeyUI follows a **minimalist black-and-white design aesthetic** inspired by Notion, with carefully chosen accent colors for emphasis. All generated UI components should adhere to this design language.

### Design Principles
- **Minimalism First**: Clean, uncluttered interfaces with generous whitespace
- **High Contrast**: Strong black-on-white contrast for readability
- **Selective Accent**: Use vibrant accent colors (red, yellow, blue) sparingly for emphasis and CTAs
- **Subtle Depth**: Prefer borders over heavy shadows; use subtle shadows only when needed
- **Modern Typography**: Sans-serif fonts with clear hierarchy (extra-bold headings, regular body text)

### CSS Variables Reference

Apply these CSS custom properties in your components to maintain visual consistency. These are defined in `frontend/src/index.css`:

```css
:root {
  /* =========================================================
   * Brand Colors
   * ========================================================= */
  --brand-primary: #000000;    /* Pure black for primary brand */
  --brand-secondary: #2A99D3;  /* Blue accent for secondary elements */

  /* =========================================================
   * Neutral Colors
   * ========================================================= */
  --bg-canvas: #FFFFFF;        /* Main background (pure white) */
  --bg-surface: #F8F8F8;       /* Secondary surface (subtle gray) */
  
  --border-subtle: #E8E8E8;    /* Light borders/dividers */
  --border-default: #E0E0E0;   /* Default borders */
  
  --text-primary: #101010;     /* Main text (near-black) */
  --text-secondary: #525252;   /* Secondary text (medium gray) */
  --text-tertiary: #737373;    /* Tertiary text (light gray) */
  --text-on-dark: #FFFFFF;     /* Text on dark backgrounds */

  /* =========================================================
   * Accent Colors (Use Sparingly)
   * ========================================================= */
  --accent-red: #F8534E;       /* Red for highlights/illustrations */
  --accent-yellow: #FBC113;    /* Yellow for warnings/highlights */
  --accent-blue: #2A99D3;      /* Blue for icons/interactive elements */

  /* =========================================================
   * Functional Colors
   * ========================================================= */
  --color-success: #22C55E;    /* Success states */
  --color-warning: #F59E0B;    /* Warning states */
  --color-error: #EF4444;      /* Error states */
  --color-info: #3B82F6;       /* Info states */

  /* =========================================================
   * Typography
   * ========================================================= */
  --font-sans: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans";
  
  --font-weight-heading: 800;  /* Extra-bold for headings */
  --font-weight-body: 400;     /* Regular for body text */
  
  --text-h1-size: 4rem;        /* ~64px for hero headings */
  --text-h1-line: 1.05;
  --text-body-size: 1.125rem;  /* ~18px for body text */
  --text-body-line: 1.6;

  /* =========================================================
   * Spacing & Radius
   * ========================================================= */
  --radius-md: 10px;           /* Medium border radius for buttons/cards */

  /* =========================================================
   * Elevation (Shadows)
   * ========================================================= */
  --shadow-none: none;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.06);      /* Subtle hover states */
  --shadow-md: 0 8px 24px rgba(0, 0, 0, 0.12);     /* Dropdowns/popovers */
  --shadow-lg: 0 16px 48px rgba(0, 0, 0, 0.16);    /* Modals (use sparingly) */

  /* =========================================================
   * Component Semantics
   * ========================================================= */
  --btn-primary-bg: #101010;   /* Primary button background */
  --btn-primary-fg: #FFFFFF;   /* Primary button text */
  --link-default: #2A99D3;     /* Default link color */

  /* =========================================================
   * Shadcn/ui Compatibility Layer (HSL format)
   * ========================================================= */
  --background: 0 0% 100%;
  --foreground: 0 0% 6%;
  --primary: 0 0% 6%;
  --primary-foreground: 0 0% 100%;
  --secondary: 0 0% 97%;
  --secondary-foreground: 0 0% 32%;
  --muted: 0 0% 97%;
  --muted-foreground: 0 0% 32%;
  --accent: 0 0% 97%;
  --accent-foreground: 0 0% 6%;
  --destructive: 0 85% 60%;
  --destructive-foreground: 0 0% 100%;
  --border: 0 0% 91%;
  --input: 0 0% 91%;
  --ring: 0 0% 6%;
  --radius: 10px;
}
```

### Using Design Tokens with Tailwind

When Tailwind classes align with our design system, prefer them. Otherwise, use CSS variables:

```jsx
// ✅ Good: Using CSS variables for custom colors
<div className="bg-white border" style={{ borderColor: 'var(--border-subtle)' }}>
  <h1 style={{ color: 'var(--text-primary)', fontWeight: 'var(--font-weight-heading)' }}>
    {t('hero.title')}
  </h1>
</div>

// ✅ Good: Using Tailwind for standard utilities
<Button className="rounded-xl bg-black text-white px-6 py-3">
  {t('common.getStarted')}
</Button>

// ❌ Avoid: Hardcoding colors
<div className="bg-[#F8F8F8]">...</div>
```

### Component Design Guidelines

1. **Buttons**: Use `--btn-primary-bg` with `--radius-md` for primary CTAs
2. **Text Hierarchy**: H1 should use `--font-weight-heading` (800), body uses `--font-weight-body` (400)
3. **Spacing**: Embrace whitespace; use generous padding around key sections
4. **Borders Over Shadows**: Prefer subtle borders (`--border-subtle`) to separate sections
5. **Accent Colors**: Reserve for interactive elements, icons, and key highlights only

## i18n Implementation

### Frontend i18n Setup
- Translation files location: `frontend/public/locales/`
- Structure: `public/locales/en/translation.json` and `public/locales/zh/translation.json`
- Loaded via `i18next-http-backend` at runtime (load path: `/locales/{{lng}}/{{ns}}.json`)
- Language detection: `i18next-browser-languagedetector`
- Always add both English and Chinese translations when creating new keys
- Use nested keys for better organization: `{ "common": { "button": { "save": "Save" } } }`
- **Text Casing**: Use Sentence case for all system-level titles and headings in English (capitalize only the first word and proper nouns). Examples: "Design workshop", "Create new vibe", "Color palette"

### Backend i18n Setup
- Use Django's internationalization framework
- Mark all user-facing strings with `gettext_lazy` or `gettext`
- Generate translation files: `uv run python manage.py makemessages -l zh_Hans`
- Compile translations: `uv run python manage.py compilemessages`

## Development

### Prerequisites
- Node.js >=18.0.0, npm >=9.0.0
- Python >=3.14 with [uv](https://docs.astral.sh/uv/) package manager
- Docker & Docker Compose (for PostgreSQL + Redis)

### Quick Start with Docker
```bash
# Start all services (DB, Redis, Backend, Celery, Frontend)
docker compose up --build

# Or start only infrastructure services
docker compose up db redis
```

### Local Development Commands
```bash
# Frontend
npm run dev:frontend          # Start Vite dev server (port 5173)
npm run build:frontend        # Production build
npm run lint                  # ESLint

# Backend
npm run dev:backend           # Start Django + Celery (via start-dev.sh)
npm run dev:backend:django    # Start Django dev server only (port 8000)
npm run dev:backend:celery    # Start Celery worker only

# Backend (direct commands)
cd backend
uv sync                       # Install Python dependencies
uv run python manage.py runserver            # Django dev server
uv run python manage.py migrate              # Run migrations
uv run python manage.py makemigrations       # Create migrations
uv run celery -A config worker --loglevel=info  # Celery worker
```

### Development Ports
- Frontend: http://localhost:5173 (Vite dev server with API proxy to backend)
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/api/docs/ (Swagger UI via drf-spectacular)

### API Endpoints
- `api/accounts/` — User authentication & management (JWT)
- `api/` — Core API endpoints
- `api/design-system/` — Design system features
- `api/v1/design-systems/` — Design system v1 endpoints
- `api/schema/` — OpenAPI schema
- `api/docs/` — Swagger UI
- `api/health/` — Health check

## Testing

### Backend Tests
```bash
cd backend
uv run python -m pytest -v                              # Run all tests
uv run python -m pytest apps/core/tests.py -v            # Run specific app tests
uv run python -m pytest apps/design_system/mcp/tests.py -v  # Run MCP tests
```

- pytest config is in `pyproject.toml` (`[tool.pytest.ini_options]`)
- DJANGO_SETTINGS_MODULE defaults to `config.settings`
- Test files: `tests.py`, `test_*.py`, `*_tests.py`

### Frontend Tests
- Linting: `cd frontend && npm run lint`
- No test runner configured yet (Vitest recommended for future setup)

## Security
- Never commit sensitive credentials or API keys
- Always validate and sanitize user input
- Use Django's built-in security features (CSRF, XSS protection)
- JWT authentication with token rotation and blacklisting
- CORS configured for specific allowed origins

## Git Commit Messages
- Use conventional commits format: `type(scope): message`
- Types: feat, fix, docs, style, refactor, test, chore
- Keep messages concise and descriptive
- Example: `feat(auth): add user login with JWT authentication`

## When Generating Code
1. **Design System First**: Always use CSS variables from the Design System section for colors, typography, and spacing
2. **i18n Requirements**: Use translation keys, not hardcoded strings
3. Follow the project's established patterns and structure
4. Include proper error handling and validation
5. Write self-documenting code with clear variable names
6. Add comments for complex logic only
7. Ensure code is production-ready and follows best practices
8. **Visual Consistency**: Generated UI should reflect the minimalist Notion-inspired aesthetic
