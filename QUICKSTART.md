# designmonkey - Quick Start Guide

Welcome to designmonkey! This guide will help you get started quickly.

## 🚀 Automated Setup

Run the setup script to install all dependencies:

```bash
./setup.sh
```

This will:
- Check prerequisites (Node.js, Python, PostgreSQL)
- Install frontend dependencies
- Install backend dependencies
- Create `.env` file from example

## 📋 Manual Setup

If you prefer manual setup, follow these steps:

### 1. Frontend Setup

```bash
cd frontend
npm install
```

### 2. Backend Setup

```bash
cd backend
pipenv install --dev
cp .env.example .env
# Edit .env with your database credentials
```

### 3. Database Setup

```bash
# Create database
createdb designmonkey_dev

# Enable pgvector extension
psql designmonkey_dev -c 'CREATE EXTENSION vector;'
```

### 4. Django Setup

```bash
cd backend
pipenv shell
python manage.py migrate
python manage.py createsuperuser
```

## 🏃 Running the Application

### Start Both Services

**Terminal 1 - Frontend:**
```bash
cd frontend
npm run dev
```
Frontend will be available at: http://localhost:5173

**Terminal 2 - Backend:**
```bash
cd backend
pipenv shell
python manage.py runserver
```
Backend API will be available at: http://localhost:8000

### API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/api/docs/
- API Schema: http://localhost:8000/api/schema/

## 🌍 Internationalization (i18n)

The application supports English and Chinese.

### Frontend
- Translation files: `frontend/public/locales/en|zh/translation.json`
- Use `t()` function from `react-i18next` in components
- Never hardcode user-facing text

### Backend
- Use `gettext_lazy()` for all user-facing strings
- Generate translations: `python manage.py makemessages -l zh_Hans`
- Compile translations: `python manage.py compilemessages`

## 🛠 Development Tools

### Frontend Commands
```bash
npm run dev      # Start dev server
npm run build    # Build for production
npm run preview  # Preview production build
npm run lint     # Run ESLint
```

### Backend Commands
```bash
python manage.py runserver          # Start dev server
python manage.py makemigrations     # Create migrations
python manage.py migrate            # Apply migrations
python manage.py createsuperuser    # Create admin user
python manage.py test               # Run tests
black .                             # Format code
flake8                              # Check code style
```

## 📦 Adding Shadcn/ui Components

To add more UI components:

```bash
cd frontend
npx shadcn-ui@latest add [component-name]
```

Examples:
```bash
npx shadcn-ui@latest add card
npx shadcn-ui@latest add input
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add table
```

## 🔍 Project Structure

```
designmonkey/
├── frontend/          # React + Vite application
├── backend/           # Django + DRF API
├── docs/              # Documentation
└── .github/           # GitHub configuration & Copilot instructions
```

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed structure.

## 📚 Documentation

- [Main README](README.md) - Project overview
- [Frontend README](frontend/README.md) - Frontend documentation
- [Backend README](backend/README.md) - Backend documentation
- [Contributing Guide](CONTRIBUTING.md) - How to contribute
- [Documentation](docs/README.md) - Detailed documentation

## ⚙️ Configuration

### Frontend Environment Variables
Create `frontend/.env`:
```
VITE_API_URL=http://localhost:8000/api
```

### Backend Environment Variables
Edit `backend/.env`:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/designmonkey_dev
```

## 🤖 GitHub Copilot

This project includes GitHub Copilot instructions at `.github/copilot-instructions.md`. These instructions ensure that:
- All code uses English
- i18n is properly implemented
- Best practices are followed
- Code style is consistent

## 🐛 Troubleshooting

### Database Connection Error
- Ensure PostgreSQL is running: `brew services start postgresql` (macOS)
- Check database credentials in `backend/.env`
- Verify database exists: `psql -l`

### Frontend Build Error
- Clear cache: `rm -rf node_modules && npm install`
- Check Node.js version: `node --version` (should be 18+)

### Backend Import Error
- Activate virtual environment: `pipenv shell`
- Reinstall dependencies: `pipenv install`

## 💡 Next Steps

1. ✅ Run `./setup.sh` to set up the project
2. ✅ Create and configure the database
3. ✅ Update `backend/.env` with your credentials
4. ✅ Run migrations
5. ✅ Create a superuser
6. ✅ Start both frontend and backend servers
7. ✅ Visit http://localhost:5173 to see the app!

## 🎉 You're All Set!

Start building amazing features with designmonkey!

For questions or issues, please refer to the documentation or open an issue.

Happy coding! 🐒
