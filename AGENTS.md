# Agent Instructions for designmonkey

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

designmonkey follows a **Playful Vibrant Academy** design aesthetic — a joyful, creative, and approachable design language inspired by a "sticker-book" aesthetic with high-energy colors, organic shapes, and whimsical details. All generated UI components should adhere to this design language.

### Design Principles
- **Curated Play**: A digital playground that blends structured learning with the organic, messy joy of a child's scrapbook
- **Warmth & Human Touch**: Communicates trust through warmth, not sterility — like a friendly teacher who sits on the floor with students
- **High-Energy Color**: Vibrant, high-contrast, candy-like palette with Electric Violet and Marigold Yellow as the primary power pair
- **Soft & Rounded**: No sharp corners — everything is softened with large border radii (24px+), pill-shaped buttons, and organic photo masks
- **Bouncy Motion**: Hover states should feel like pressing a physical button or lifting a sticker; elastic, bouncy transitions

### Material & Lighting
- Surfaces feel like **matte paper and soft plastics** — flat, clean color blocks with a "cut-out" paper feel
- Uniform, high-key lighting; shadows are very soft and diffuse (sticker-lift effect)
- Depth is achieved through **overlap and layering** (2.5D collage approach), not heavy shadows

### CSS Variables Reference

Apply these CSS custom properties in your components to maintain visual consistency. These are defined in `frontend/src/index.css`:

```css
:root {
  /* =========================================================
   * Brand Colors
   * ========================================================= */
  --brand-primary: #6B52E1;    /* Electric Violet */
  --brand-secondary: #FFD560;  /* Marigold Yellow */

  /* =========================================================
   * Neutral Colors
   * ========================================================= */
  --bg-canvas: #FFFFFF;        /* Main background (white paper) */
  --bg-surface: #F5F0FF;       /* Secondary surface (pale lilac) */
  
  --border-subtle: #E8DFF5;    /* Light violet borders/dividers */
  --border-default: #D4C8F0;   /* Default violet borders */
  
  --text-primary: #2D1B69;     /* Main text (deep indigo, never pure black) */
  --text-secondary: #6B5B8A;   /* Secondary text (medium violet-gray) */
  --text-tertiary: #9B8FBB;    /* Tertiary text (light violet-gray) */
  --text-on-dark: #FFFFFF;     /* Text on dark backgrounds */

  /* =========================================================
   * Accent Colors (High Saturation, Candy-like)
   * ========================================================= */
  --accent-violet: #6B52E1;    /* Electric Violet for primary accents */
  --accent-yellow: #FFD560;    /* Marigold Yellow for highlights */
  --accent-pink: #FF6B9D;      /* Playful pink for illustrations */
  --accent-blue: #6B52E1;      /* Alias to primary for backward compat */

  /* =========================================================
   * Functional Colors
   * ========================================================= */
  --color-success: #22C55E;    /* Success states */
  --color-warning: #FFD560;    /* Warning states (marigold) */
  --color-error: #FF6B6B;      /* Error states (soft playful red) */
  --color-info: #6B52E1;       /* Info states (primary violet) */

  /* =========================================================
   * Typography
   * ========================================================= */
  --font-sans: "Nunito", "Quicksand", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --font-accent: "Caveat", cursive;  /* Handwritten brush script for emotional words */
  
  --font-weight-heading: 800;  /* Extra-bold for headings */
  --font-weight-subheading: 700;
  --font-weight-body: 400;     /* Regular for body text */
  
  --text-h1-size: 3.5rem;      /* ~56px for hero headings */
  --text-h1-line: 1.1;
  --text-body-size: 1rem;      /* 16px base font size */
  --text-body-line: 1.6;

  /* =========================================================
   * Spacing & Radius
   * ========================================================= */
  --radius-md: 24px;           /* Large border radius for cards/buttons */
  --radius-pill: 9999px;       /* Fully rounded pill shapes */

  /* =========================================================
   * Elevation (Shadows - Soft, Diffuse, Violet-tinted)
   * ========================================================= */
  --shadow-none: none;
  --shadow-sm: 0 2px 8px rgba(107, 82, 225, 0.08);      /* Subtle sticker-lift */
  --shadow-md: 0 8px 24px rgba(107, 82, 225, 0.12);     /* Floating cards */
  --shadow-lg: 0 16px 48px rgba(107, 82, 225, 0.16);    /* Modals (use sparingly) */

  /* =========================================================
   * Component Semantics
   * ========================================================= */
  --btn-primary-bg: #6B52E1;   /* Primary button background (Electric Violet) */
  --btn-primary-fg: #FFFFFF;   /* Primary button text */
  --link-default: #6B52E1;     /* Default link color */

  /* =========================================================
   * Shadcn/ui Compatibility Layer (HSL format)
   * ========================================================= */
  --background: 0 0% 100%;
  --foreground: 259 58% 26%;
  --primary: 252 69% 60%;
  --primary-foreground: 0 0% 100%;
  --secondary: 44 100% 69%;
  --secondary-foreground: 259 58% 26%;
  --muted: 260 100% 97%;
  --muted-foreground: 262 20% 45%;
  --accent: 260 100% 97%;
  --accent-foreground: 259 58% 26%;
  --destructive: 0 100% 71%;
  --destructive-foreground: 0 0% 100%;
  --border: 260 52% 92%;
  --input: 260 52% 92%;
  --ring: 252 69% 60%;
  --radius: 24px;
}
```

### Using Design Tokens with Tailwind

When Tailwind classes align with our design system, prefer them. Otherwise, use CSS variables:

```jsx
// ✅ Good: Using CSS variables for custom colors
<div className="bg-white" style={{ borderColor: 'var(--border-subtle)' }}>
  <h1 style={{ color: 'var(--text-primary)', fontWeight: 'var(--font-weight-heading)' }}>
    {t('hero.title')}
  </h1>
</div>

// ✅ Good: Pill-shaped button with primary violet
<Button className="rounded-full bg-primary text-white px-6 py-3">
  {t('common.getStarted')}
</Button>

// ✅ Good: Using font-accent for handwritten words
<span className="font-accent text-2xl" style={{ color: 'var(--accent-yellow)' }}>
  {t('hero.playful')}
</span>

// ❌ Avoid: Hardcoding colors
<div className="bg-[#F8F8F8]">...</div>

// ❌ Avoid: Sharp corners (use rounded-2xl or rounded-full)
<div className="rounded-sm">...</div>
```

### Component Design Guidelines

1. **Buttons**: Pill-shaped (`rounded-full`) with `--btn-primary-bg` (Electric Violet); include bouncy `active:scale-[0.97]` effect
2. **Cards**: Massive border radii (24px+), use solid color backgrounds (`--bg-surface` pale lilac) rather than outlines; treat as "islands"
3. **Text Hierarchy**: Headings use `--font-weight-heading` (800) with Nunito; for emotional/marketing words, use `--font-accent` (Caveat handwritten)
4. **Spacing**: Asymmetric and breathing — elements float in open space with generous padding
5. **Color Usage**: Use violet and yellow in large solid blocks (card backgrounds, highlighter strokes); never use Corporate Blue/Grey palettes
6. **Photos**: Never use raw rectangular photos — mask into circles, arches, or organic blobs
7. **Decorative Elements**: Use hand-drawn doodles (arrows, spirals, dots, sparkles) sparingly to add motion and whimsy
8. **Navigation**: Minimal and pill-shaped; active states use rounded capsules
9. **No Sharp Corners**: No 90-degree angles on buttons, cards, or images
10. **No Dark Mode**: This aesthetic relies on the "white paper" brightness
11. **No Serif Fonts**: Do not use traditional serifs — they feel too academic for this vibe

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
8. **Visual Consistency**: Generated UI should reflect the Playful Vibrant Academy aesthetic — joyful, rounded, high-energy, and whimsical
9. **No Sharp Corners**: All buttons use `rounded-full`, cards use `rounded-3xl` or `--radius-md` (24px)
10. **Color Palette**: Electric Violet (#6B52E1) + Marigold Yellow (#FFD560) — never use corporate blue/grey palettes
11. **Typography**: Use Nunito/Quicksand for UI, Caveat (handwritten) for playful accents
12. **Anti-Patterns**: No pure black text, no rectangular photos, no serif fonts, no dark mode
