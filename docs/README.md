# MonkeyUI Documentation

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL 15+ with pgvector
- Pipenv

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd monkeyui
   ```

2. **Setup Frontend:**
   ```bash
   cd frontend
   npm install
   cp .env.example .env  # if exists
   npm run dev
   ```

3. **Setup Backend:**
   ```bash
   cd backend
   pipenv install
   pipenv shell
   cp .env.example .env
   # Update .env with your database credentials
   
   # Setup database
   createdb monkeyui_dev
   psql monkeyui_dev -c 'CREATE EXTENSION vector;'
   
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

## Architecture

### Frontend (React + Vite)
- Modern React with Hooks
- Vite for fast development
- TailwindCSS for styling
- Shadcn/ui component library
- i18next for internationalization
- Axios for API calls

### Backend (Django + DRF)
- Django 5.0
- Django REST Framework
- PostgreSQL with pgvector
- Pipenv for dependency management
- drf-spectacular for API documentation

## Features

### Internationalization (i18n)

The project supports English and Chinese. All user-facing text uses translation keys.

**Frontend Example:**
```jsx
import { useTranslation } from 'react-i18next';

function MyComponent() {
  const { t } = useTranslation();
  return <h1>{t('welcome.title')}</h1>;
}
```

**Backend Example:**
```python
from django.utils.translation import gettext_lazy as _

class MyView(APIView):
    def get(self, request):
        return Response({'message': _('Success')})
```

### API Documentation

Visit http://localhost:8000/api/docs/ for interactive API documentation.

### Vector Search (pgvector)

The backend is configured to use pgvector for vector similarity search:

```python
from pgvector.django import VectorField

class Document(models.Model):
    embedding = VectorField(dimensions=1536)
```

## Development Workflow

### Frontend Development

```bash
cd frontend
npm run dev       # Start dev server
npm run build     # Build for production
npm run preview   # Preview production build
npm run lint      # Run ESLint
```

### Backend Development

```bash
cd backend
pipenv shell
python manage.py runserver          # Start dev server
python manage.py makemigrations     # Create migrations
python manage.py migrate            # Apply migrations
python manage.py createsuperuser    # Create admin user
python manage.py test               # Run tests
```

### i18n Workflow

**Frontend:**
1. Add translation keys to `frontend/public/locales/en/translation.json`
2. Add Chinese translations to `frontend/public/locales/zh/translation.json`
3. Use `t('key')` in components

**Backend:**
1. Mark strings with `_()` or `gettext_lazy()`
2. Generate message files: `python manage.py makemessages -l zh_Hans`
3. Edit translations in `backend/locale/zh_Hans/LC_MESSAGES/django.po`
4. Compile: `python manage.py compilemessages`

## Testing

### Frontend
```bash
cd frontend
npm test
```

### Backend
```bash
cd backend
pipenv shell
pytest
```

## Deployment

See deployment documentation for production setup instructions.

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running
- Verify credentials in `.env`
- Check if pgvector extension is installed

### Frontend Build Issues
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node.js version: `node --version` (should be 18+)

### Backend Import Errors
- Activate pipenv: `pipenv shell`
- Reinstall dependencies: `pipenv install`

## Additional Documentation

- [MCP Tools Reference](MCP_TOOLS.md) - Complete reference for MCP (Model Context Protocol) tools and AI coding assistant integration

## Further Reading

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [TailwindCSS Documentation](https://tailwindcss.com/)
- [Shadcn/ui Documentation](https://ui.shadcn.com/)
