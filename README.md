# MonkeyUI
A UIUX knowledge base empowering vibe coding, helping developers generate professional-grade, high-intent UI through carefully designed reference guidelines, without requiring designer expertise.

## Project Structure

```
monkeyui/
├── frontend/          # React + Vite frontend application
├── backend/           # Django + DRF backend API
└── docs/              # Documentation
```

## Tech Stack

### Frontend
- **React** - UI framework
- **Vite** - Build tool and dev server
- **TailwindCSS** - Utility-first CSS framework
- **Shadcn/ui** - Re-usable component library
- **i18next** - Internationalization (English/Chinese)

### Backend
- **Django** - Web framework
- **Django REST Framework** - RESTful API toolkit
- **PostgreSQL** - Primary database
- **pgvector** - Vector similarity search extension
- **Pipenv** - Python dependency management

## Getting Started

### Prerequisites
- Node.js 22+ and npm
- Python 3.11+
- PostgreSQL 15+ with pgvector extension
- Pipenv

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Backend Setup

```bash
cd backend
pipenv install
pipenv shell

# Setup database
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

The backend API will be available at `http://localhost:8000`

### Database Setup

1. Install PostgreSQL and pgvector extension:
```bash
# macOS
brew install postgresql pgvector
brew services start postgresql

# Create database
createdb monkeyui_dev
psql monkeyui_dev -c 'CREATE EXTENSION vector;'
```

2. Update backend `.env` file with your database credentials.

## Development

### Running Both Services

For convenience, you can run both frontend and backend concurrently:

```bash
# Terminal 1 - Frontend
cd frontend && npm run dev

# Terminal 2 - Backend
cd backend && pipenv run python manage.py runserver
```

## Internationalization (i18n)

This project supports English (default) and Chinese. Language files are located in:
- Frontend: `frontend/src/locales/`
- Backend: `backend/locale/`

## Contributing

Please read our contributing guidelines before submitting pull requests.

## License

MIT
