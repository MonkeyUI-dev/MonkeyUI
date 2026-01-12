# MonkeyUI Project Structure

```
monkeyui/
├── .github/
│   └── copilot-instructions.md    # GitHub Copilot configuration
│
├── frontend/                       # React frontend application
│   ├── public/
│   │   └── locales/               # i18n translation files
│   │       ├── en/
│   │       │   └── translation.json
│   │       └── zh/
│   │           └── translation.json
│   ├── src/
│   │   ├── components/
│   │   │   └── ui/                # Shadcn/ui components
│   │   │       └── button.jsx
│   │   ├── lib/
│   │   │   └── utils.js           # Utility functions
│   │   ├── App.jsx                # Main app component
│   │   ├── main.jsx               # Entry point
│   │   ├── i18n.js                # i18n configuration
│   │   └── index.css              # Global styles
│   ├── index.html
│   ├── vite.config.js             # Vite configuration
│   ├── tailwind.config.js         # TailwindCSS configuration
│   ├── postcss.config.js
│   ├── components.json            # Shadcn/ui configuration
│   ├── package.json
│   └── README.md
│
├── backend/                        # Django backend application
│   ├── config/                    # Project configuration
│   │   ├── settings.py            # Django settings
│   │   ├── urls.py                # Root URL configuration
│   │   ├── wsgi.py
│   │   ├── asgi.py
│   │   └── __init__.py
│   ├── apps/                      # Django apps
│   │   ├── __init__.py
│   │   └── core/                  # Core application
│   │       ├── models.py
│   │       ├── views.py
│   │       ├── serializers.py
│   │       ├── urls.py
│   │       ├── admin.py
│   │       ├── apps.py
│   │       ├── tests.py
│   │       └── __init__.py
│   ├── locale/                    # i18n translation files
│   ├── manage.py
│   ├── Pipfile                    # Python dependencies
│   ├── .env.example               # Environment variables example
│   ├── .flake8                    # Flake8 configuration
│   ├── pytest.ini                 # Pytest configuration
│   └── README.md
│
├── docs/                          # Documentation
│   └── README.md
│
├── .gitignore
├── README.md                      # Main project README
├── CONTRIBUTING.md                # Contribution guidelines
├── LICENSE
├── package.json                   # Root package.json (workspaces)
└── setup.sh                       # Setup script
```

## Key Components

### Frontend Structure
- **public/locales/**: Translation files for i18n
- **src/components/ui/**: Reusable Shadcn/ui components
- **src/lib/**: Utility functions and helpers
- **vite.config.js**: Vite configuration with API proxy
- **tailwind.config.js**: TailwindCSS with Shadcn theme

### Backend Structure
- **config/**: Django project settings and configuration
- **apps/**: Modular Django applications
- **apps/core/**: Core functionality and base models
- **locale/**: Translation files for Django i18n
- **Pipfile**: Python dependencies managed by pipenv

## Technology Stack

### Frontend
- React 18.3
- Vite 5.4
- TailwindCSS 3.4
- Shadcn/ui
- react-i18next 14.0
- Axios 1.6

### Backend
- Django 5.0
- Django REST Framework 3.14
- PostgreSQL with pgvector
- Python 3.11+
- drf-spectacular (API docs)

## Development Ports
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/api/docs/
