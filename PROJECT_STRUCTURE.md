# MonkeyUI Project Structure

```
monkeyui/
├── .github/
│   ├── agent.md                    # AI agent instructions & project conventions
│   └── workflows/
│       └── fly-deploy.yml          # Fly.io deployment workflow
│
├── frontend/                       # React frontend application
│   ├── public/
│   │   └── locales/               # i18n translation files (loaded at runtime)
│   │       ├── en/
│   │       │   └── translation.json
│   │       └── zh/
│   │           └── translation.json
│   ├── src/
│   │   ├── components/
│   │   │   ├── auth/              # Auth components (ProtectedRoute)
│   │   │   ├── layout/            # Layout components (ConsoleLayout)
│   │   │   ├── ui/                # Shadcn/ui base components (Button, Alert, Pagination)
│   │   │   └── vibe/              # Vibe/design-system feature components
│   │   ├── contexts/              # React context providers (AuthContext)
│   │   ├── pages/                 # Page components (Login, Register, VibeStudio, DesignWorkshop)
│   │   ├── services/              # API service layer (auth, designSystem, apiKeys)
│   │   ├── lib/                   # Utility functions (api, utils)
│   │   ├── App.jsx                # Main app component with routing
│   │   ├── main.jsx               # Entry point
│   │   ├── i18n.js                # i18n configuration
│   │   └── index.css              # Global styles + design system CSS variables
│   ├── index.html
│   ├── vite.config.js             # Vite configuration with API proxy
│   ├── tailwind.config.js         # TailwindCSS configuration with Shadcn theme
│   ├── postcss.config.js
│   ├── eslint.config.js           # ESLint flat config
│   ├── components.json            # Shadcn/ui configuration
│   ├── package.json
│   └── README.md
│
├── backend/                        # Django backend application
│   ├── config/                    # Project configuration
│   │   ├── settings.py            # Django settings (DB, cache, LLM, storage, etc.)
│   │   ├── urls.py                # Root URL configuration
│   │   ├── celery.py              # Celery app configuration
│   │   ├── wsgi.py
│   │   ├── asgi.py
│   │   └── __init__.py
│   ├── apps/                      # Django apps
│   │   ├── __init__.py
│   │   ├── accounts/              # User authentication & management
│   │   │   ├── models.py          # Custom User model
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   └── urls.py
│   │   ├── core/                  # Core functionality
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   └── tests.py
│   │   └── design_system/         # Design system features (main business logic)
│   │       ├── models.py
│   │       ├── serializers.py
│   │       ├── services.py
│   │       ├── tasks.py           # Celery async tasks
│   │       ├── views.py
│   │       ├── urls.py
│   │       ├── schema.py          # DRF Spectacular schema customizations
│   │       ├── llm/               # LLM provider integration
│   │       │   ├── config.py
│   │       │   └── providers.py
│   │       ├── mcp/               # Model Context Protocol
│   │       │   ├── server.py
│   │       │   ├── mcp_server.py
│   │       │   ├── views.py
│   │       │   └── tests.py
│   │       └── prompts/           # Prompt templates for LLM
│   ├── manage.py
│   ├── pyproject.toml             # Python dependencies (managed by uv)
│   ├── uv.lock                    # Lock file for uv
│   ├── .env.example               # Environment variables example
│   ├── .flake8                    # Flake8 configuration
│   ├── start-dev.sh               # Dev startup script (Django + Celery)
│   └── README.md
│
├── docs/                          # Documentation
│   └── README.md
│
├── docker-compose.yml             # Docker Compose (DB, Redis, Backend, Celery, Frontend)
├── Dockerfile                     # Production Dockerfile
├── fly.toml                       # Fly.io deployment config
├── .gitignore
├── README.md                      # Main project README
├── CONTRIBUTING.md                # Contribution guidelines
├── PROJECT_STRUCTURE.md           # This file
├── QUICKSTART.md                  # Quick start guide
├── LICENSE
├── package.json                   # Root package.json (npm workspaces)
├── monkeyui.code-workspace        # VS Code workspace config
├── setup.sh                       # Setup script
└── setup-auth.sh                  # Auth setup script
```

## Key Components

### Frontend Structure
- **public/locales/**: Translation files for i18n (loaded via HTTP backend)
- **src/components/ui/**: Reusable Shadcn/ui base components
- **src/components/vibe/**: Feature-specific components for vibe/design-system
- **src/contexts/**: React context providers (e.g., AuthContext)
- **src/pages/**: Page-level components
- **src/services/**: API service layer for backend communication
- **src/lib/**: Utility functions and helpers
- **vite.config.js**: Vite configuration with API proxy to backend
- **tailwind.config.js**: TailwindCSS with Shadcn theme and CSS variable integration

### Backend Structure
- **config/**: Django project settings, Celery config, and URL routing
- **apps/accounts/**: Custom user model and JWT authentication
- **apps/core/**: Core functionality and base models
- **apps/design_system/**: Main business logic — design system creation, LLM integration, MCP server
- **apps/design_system/llm/**: Multi-provider LLM integration (Gemini, OpenRouter)
- **apps/design_system/mcp/**: Model Context Protocol server
- **pyproject.toml**: Python dependencies managed by uv

## Technology Stack

### Frontend
- React 19.0.0
- Vite 6.0.0
- TailwindCSS 3.4
- Shadcn/ui + Headless UI + Heroicons + Lucide React
- react-i18next 15.2 + i18next 24.2
- react-router-dom 7.1
- Axios 1.7

### Backend
- Django 6.0.1
- Django REST Framework 3.14
- djangorestframework-simplejwt 5.3 (JWT auth)
- PostgreSQL 16 with pgvector
- Redis 7 + Celery (async task queue)
- Python >=3.14 (managed by uv)
- drf-spectacular (API docs)
- OpenAI + Google Generative AI + MCP (LLM integration)
- django-storages + boto3 (S3-compatible file storage)

### Infrastructure
- Docker Compose for local development
- Fly.io for production deployment
- WhiteNoise for static file serving

## Development Ports
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/api/docs/
- PostgreSQL: localhost:5432
- Redis: localhost:6379
