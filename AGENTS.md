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
| Deployment      | Docker Compose         |

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

MonkeyUI follows a **NOCTURNAL NEBULA FINANCE** design aesthetic — an ethereal, precise, sophisticated, futuristic, and serene design language inspired by deep space exploration and constellations. All generated UI components should adhere to this design language.

### Design Principles
- **Illuminated Clarity in the Void**: A visual language that feels like navigating a high-tech interface in deep space.
- **Technological Mastery**: Communicates trust through precision and high-fidelity rendering, suggesting a platform that is powerful, silent, and incredibly fast.
- **Monochromatic Dark Mode**: Strictly controlled palette favoring void blacks with desaturated spectral accents (muted mint/sage green and pale ethereal silver).
- **Ambient & Volumetric Lighting**: Soft "aurora" glows and diffuse fogs drift behind elements. Light seems to emanate from the data itself.
- **Cinematic Center-Stage**: Layouts feature a central visual anchor with supporting details orbiting around it, feeling more like a HUD.

### Material & Lighting
- Surfaces feel like **smoked glass and matte darkness** — deep, matte charcoal surfaces that recede into true black.
- Overlays are treated as "smoked glass" — translucent panels that blur the background slightly.
- Depth is achieved through **atmospheric perspective** — elements further "back" are dimmer and covered by a subtle haze.

### CSS Variables Reference

Apply these CSS custom properties in your components to maintain visual consistency. These are defined in `frontend/src/index.css`:

```css
:root {
  /* =========================================================
   * Brand Colors
   * ========================================================= */
  --brand-primary: #FFFFFF;    /* White */
  --brand-secondary: #A8C0AF;  /* Muted mint/sage green */

  /* =========================================================
   * Neutral Colors
   * ========================================================= */
  --bg-canvas: #050505;        /* Main background (Void Black) */
  --bg-surface: #171717;       /* Secondary surface (Deep matte charcoal) */
  
  --border-subtle: rgba(255, 255, 255, 0.1);    /* Light borders/dividers */
  --border-default: rgba(255, 255, 255, 0.2);   /* Default borders */
  
  --text-primary: #FFFFFF;     /* Main text (White) */
  --text-secondary: #A3A3A3;   /* Secondary text (Mid-grey) */
  --text-tertiary: #737373;    /* Tertiary text (Dark-grey) */
  --text-on-dark: #FFFFFF;     /* Text on dark backgrounds */

  /* =========================================================
   * Accent Colors (Desaturated spectral accents)
   * ========================================================= */
  --accent-mint: #A8C0AF;      /* Muted mint/sage green for primary accents */
  --accent-silver: #E5E7EB;    /* Pale ethereal silver for highlights */

  /* =========================================================
   * Functional Colors
   * ========================================================= */
  --color-success: #A8C0AF;    /* Success states */
  --color-warning: #FCD34D;    /* Warning states */
  --color-error: #FCA5A5;      /* Error states */
  --color-info: #93C5FD;       /* Info states */

  /* =========================================================
   * Typography
   * ========================================================= */
  --font-sans: "Inter", "SF Pro Display", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --font-accent: "Inter", "SF Pro Display", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  
  --font-weight-heading: 500;  /* Moderate weight for headings */
  --font-weight-subheading: 500;
  --font-weight-body: 300;     /* Light for body text */
  
  --text-h1-size: 3.5rem;      /* ~56px for hero headings */
  --text-h1-line: 1.1;
  --text-body-size: 1rem;      /* 16px base font size */
  --text-body-line: 1.6;

  /* =========================================================
   * Spacing & Radius
   * ========================================================= */
  --radius-md: 12px;           /* Standard rounded corners */
  --radius-pill: 9999px;       /* Fully rounded pill shapes */

  /* =========================================================
   * Elevation (Shadows - Ambient and volumetric glows)
   * ========================================================= */
  --shadow-none: none;
  --shadow-sm: 0 0 10px rgba(168, 192, 175, 0.1);      /* Soft aurora glow */
  --shadow-md: 0 0 20px rgba(168, 192, 175, 0.15);     /* Floating islands */
  --shadow-lg: 0 0 40px rgba(168, 192, 175, 0.2);      /* Modals */

  /* =========================================================
   * Component Semantics
   * ========================================================= */
  --btn-primary-bg: #FFFFFF;   /* Primary button background */
  --btn-primary-fg: #050505;   /* Primary button text */
  --link-default: #A8C0AF;     /* Default link color */

  /* =========================================================
   * Shadcn/ui Compatibility Layer (HSL format)
   * ========================================================= */
  --background: 0 0% 2%;
  --foreground: 0 0% 100%;
  --primary: 0 0% 100%;
  --primary-foreground: 0 0% 2%;
  --secondary: 138 15% 71%;
  --secondary-foreground: 0 0% 2%;
  --muted: 0 0% 15%;
  --muted-foreground: 0 0% 64%;
  --accent: 138 15% 71%;
  --accent-foreground: 0 0% 2%;
  --destructive: 0 84% 60%;
  --destructive-foreground: 0 0% 100%;
  --border: 0 0% 20%;
  --input: 0 0% 20%;
  --ring: 138 15% 71%;
  --radius: 12px;
}
```

### Using Design Tokens with Tailwind

When Tailwind classes align with our design system, prefer them. Otherwise, use CSS variables:

```jsx
// ✅ Good: Using CSS variables for custom colors
<div className="bg-background" style={{ borderColor: 'var(--border-subtle)' }}>
  <h1 style={{ color: 'var(--text-primary)', fontWeight: 'var(--font-weight-heading)' }}>
    {t('hero.title')}
  </h1>
</div>

// ✅ Good: Pill-shaped button with primary white
<Button className="rounded-full bg-primary text-primary-foreground px-6 py-3">
  {t('common.getStarted')}
</Button>

// ✅ Good: Using accent color for highlights
<span className="text-2xl" style={{ color: 'var(--accent-mint)' }}>
  {t('hero.highlight')}
</span>

// ❌ Avoid: Hardcoding colors
<div className="bg-[#F8F8F8]">...</div>

// ❌ Avoid: Sharp corners (use rounded-xl or rounded-full)
<div className="rounded-sm">...</div>
```

### Component Design Guidelines

1. **Buttons**: Pill-shaped (`rounded-full`) with `--btn-primary-bg` (White) or pale mint. Secondary buttons are glass-style pills with a thin stroke and low-opacity fill.
2. **Cards**: Dark panels with a very faint (1px) top or border highlight to catch the "light". Use `--bg-surface` (Deep matte charcoal).
3. **Text Hierarchy**: Headings use `--font-weight-heading` (500) with Inter/SF Pro. Body text is often small, set in grey, with generous line height.
4. **Spacing**: Expansive and fluid. Massive breathing room around central hero elements.
5. **Color Usage**: Monochromatic dark mode with desaturated spectral accents. Never use neon or highly saturated colors.
6. **Data Display**: Large, crisp numbers. "Stat blocks" that group a label (grey) with a value (white/mint).
7. **Decorative Elements**: Constellation lines. Thin, low-opacity vector lines connecting floating elements. Soft, blurred orbs of color in the background.
8. **Navigation**: Minimalist floating pills. Backgrounds are semi-transparent black with a subtle white border.
9. **No Hard Drop Shadows**: Depth comes from glow and overlay, not shadow.
10. **No Boxy Grids**: Avoid rigid, Excel-like grids with visible heavy borders.
11. **No Serif Fonts**: Do not use traditional serifs — they clash with the engineered, futuristic soul of the interface.

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
8. **Visual Consistency**: Generated UI should reflect the NOCTURNAL NEBULA FINANCE aesthetic — ethereal, precise, sophisticated, futuristic, and serene.
9. **No Sharp Corners**: All buttons use `rounded-full`, cards use `rounded-xl` or `--radius-md` (12px)
10. **Color Palette**: Void Blacks (#050505, #171717) + Muted Mint/Sage Green (#A8C0AF) + White (#FFFFFF) — never use neon or highly saturated colors.
11. **Typography**: Use Inter/SF Pro for UI. No serif fonts.
12. **Anti-Patterns**: No hard drop shadows, no boxy grids, no serif fonts, no neon colors.
