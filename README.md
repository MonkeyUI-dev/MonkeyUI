# MonkeyUI

[中文文档](README.zh-CN.md)

A modern full-stack application built with **React 19** and **Django 6**, featuring AI/LLM integrations, vector search with pgvector, and async task processing with Celery.

---

## Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 19 · Vite 6 · TailwindCSS · Shadcn/ui · react-i18next |
| **Backend** | Django 6 · Django REST Framework · Celery · drf-spectacular |
| **Database** | PostgreSQL 16 · pgvector |
| **Infra** | Docker Compose · Redis · uv · Fly.io |

## Project Structure

```
monkeyui/
├── frontend/           # React + Vite frontend application
│   ├── src/
│   │   ├── components/ # React components (incl. Shadcn/ui)
│   │   ├── locales/    # i18n translation files (en/zh)
│   │   └── lib/        # Utility functions
│   └── public/
├── backend/            # Django + DRF backend API
│   ├── config/         # Django project settings
│   ├── apps/           # Django applications
│   └── locale/         # Backend i18n files
├── docs/               # Documentation
├── docker-compose.yml  # Full-stack Docker setup
├── Dockerfile          # Multi-stage production build
├── setup.sh            # Automated setup script
└── setup-auth.sh       # Auth system setup script
```

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for a detailed breakdown.

## Getting Started

### Prerequisites

| Tool | Version | Installation |
|---|---|---|
| Node.js | 18+ | https://nodejs.org |
| Python | 3.14+ | https://www.python.org |
| PostgreSQL | 15+ (with pgvector) | `brew install postgresql pgvector` (macOS) |
| uv | latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Redis | 7+ | `brew install redis` (macOS) or via Docker |

### Option A: Docker Compose (Recommended)

The fastest way to get up and running — no need to install PostgreSQL, Redis, or Python locally:

```bash
# Start all services (PostgreSQL, Redis, Backend, Celery Worker, Frontend)
docker compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/api/docs/ |

### Option B: Automated Local Setup

```bash
# Run the setup script (checks prerequisites, installs dependencies)
./setup.sh
```

Then follow the printed "Next Steps" to create the database, run migrations, and start the servers.

### Option C: Manual Local Setup

#### 1. Database

```bash
# macOS
brew install postgresql pgvector
brew services start postgresql

# Create database and enable pgvector
createdb monkeyui_dev
psql monkeyui_dev -c 'CREATE EXTENSION vector;'
```

#### 2. Backend

```bash
cd backend

# Install dependencies with uv
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Run migrations and create admin user
uv run python manage.py migrate
uv run python manage.py createsuperuser

# Start the development server
uv run python manage.py runserver
```

The backend API will be available at http://localhost:8000

#### 3. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

The frontend will be available at http://localhost:5173

#### 4. Celery Worker (Optional — for async tasks)

```bash
# Make sure Redis is running first
cd backend
uv run celery -A config worker --loglevel=info
```

## Development

### Running Both Services

```bash
# Terminal 1 — Frontend
cd frontend && npm run dev

# Terminal 2 — Backend
cd backend && uv run python manage.py runserver

# Terminal 3 — Celery Worker (optional)
cd backend && uv run celery -A config worker --loglevel=info
```

### Useful Commands

#### Frontend

```bash
npm run dev        # Start dev server
npm run build      # Production build
npm run preview    # Preview production build
npm run lint       # Run ESLint
```

#### Backend

```bash
uv run python manage.py runserver          # Start dev server
uv run python manage.py makemigrations     # Create migrations
uv run python manage.py migrate            # Apply migrations
uv run python manage.py createsuperuser    # Create admin user
uv run pytest                              # Run tests
uv run black .                             # Format code
uv run flake8                              # Check code style
```

### API Documentation

Once the backend is running:

- **Swagger UI**: http://localhost:8000/api/docs/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## Environment Variables

### Backend (`backend/.env`)

Copy from the example and edit as needed:

```bash
cp backend/.env.example backend/.env
```

Key variables:

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Django secret key | *(change in production)* |
| `DEBUG` | Debug mode | `True` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/monkeyui_dev` |
| `CELERY_BROKER_URL` | Redis URL for Celery | `redis://localhost:6379/0` |
| `DEFAULT_LLM_PROVIDER` | LLM provider (`gemini`, `openrouter`, `qwen`) | — |
| `FILE_STORAGE_BACKEND` | Storage backend (`local` or `s3`) | `local` |

See [`backend/.env.example`](backend/.env.example) for the full list of variables including LLM and S3 configuration.

### Frontend (`frontend/.env`)

```
VITE_API_URL=http://localhost:8000/api
```

## Internationalization (i18n)

The project supports **English** (default) and **Chinese**.

### Frontend

- Translation files: `frontend/public/locales/{en,zh}/translation.json`
- Use the `t()` function from `react-i18next` — never hardcode user-facing text.

```jsx
import { useTranslation } from 'react-i18next';

function MyComponent() {
  const { t } = useTranslation();
  return <h1>{t('welcome.title')}</h1>;
}
```

### Backend

- Mark strings with `gettext_lazy()`:

```python
from django.utils.translation import gettext_lazy as _
message = _("Hello, world!")
```

- Generate and compile translations:

```bash
uv run python manage.py makemessages -l zh_Hans
uv run python manage.py compilemessages
```

## Deployment

The project includes a multi-stage `Dockerfile` and a `fly.toml` for deployment to [Fly.io](https://fly.io).

```bash
# Deploy to Fly.io
fly deploy
```

## Troubleshooting

| Problem | Solution |
|---|---|
| Database connection error | Ensure PostgreSQL is running (`brew services start postgresql` on macOS). Verify credentials in `backend/.env`. |
| Frontend build error | Clear cache: `rm -rf node_modules && npm install`. Check Node.js version (`node --version`, need 18+). |
| Backend import error | Ensure dependencies are installed: `cd backend && uv sync`. |
| Celery tasks not executing | Ensure Redis is running and `CELERY_BROKER_URL` is correct in `backend/.env`. |

## Contributing

Please read our [Contributing Guide](CONTRIBUTING.md) before submitting pull requests.

## Documentation

- [Quick Start Guide](QUICKSTART.md)
- [Project Structure](PROJECT_STRUCTURE.md)
- [Frontend README](frontend/README.md)
- [Backend README](backend/README.md)
- [Documentation](docs/README.md)

## License

[MIT](LICENSE)
