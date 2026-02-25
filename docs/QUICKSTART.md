# MonkeyUI - Quick Start Guide

Welcome to MonkeyUI! This guide will help you get started quickly.

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
uv sync
cp .env.example .env
# Edit .env with your database credentials
```

### 3. Database Setup

```bash
# Create database
createdb monkeyui_dev

# Enable pgvector extension
psql monkeyui_dev -c 'CREATE EXTENSION vector;'
```

### 4. Django Setup

```bash
cd backend
uv run python manage.py migrate
uv run python manage.py createsuperuser
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
uv run python manage.py runserver
```
Backend API will be available at: http://localhost:8000

### API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/api/docs/
- API Schema: http://localhost:8000/api/schema/

## 🌍 Internationalization (i18n)

The application supports English and Chinese.

### Frontend
- Translation files: `frontend/public/locales/en|zh-CN/translation.json`
- Use `t()` function from `react-i18next` in components
- Never hardcode user-facing text

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
uv run python manage.py runserver          # Start dev server
uv run python manage.py makemigrations     # Create migrations
uv run python manage.py migrate            # Apply migrations
uv run python manage.py createsuperuser    # Create admin user
uv run python manage.py test               # Run tests
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
monkeyui/
├── frontend/          # React + Vite application
├── backend/           # Django + DRF API
├── docs/              # Documentation
└── .github/           # GitHub configuration & Copilot instructions
```

## 📚 Documentation

- [Main README](../README.md) - Project overview
- [Frontend README](../frontend/README.md) - Frontend documentation
- [Backend README](../backend/README.md) - Backend documentation
- [Contributing Guide](../CONTRIBUTING.md) - How to contribute

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
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/monkeyui_dev
```

## 🐛 Troubleshooting

### Database Connection Error
- Ensure PostgreSQL is running: `brew services start postgresql` (macOS)
- Check database credentials in `backend/.env`
- Verify database exists: `psql -l`

### Frontend Build Error
- Clear cache: `rm -rf node_modules && npm install`
- Check Node.js version: `node --version` (should be 22+)

### Backend Import Error
- Reinstall dependencies: `uv sync`

## 💡 Next Steps

1. ✅ Run `./setup.sh` to set up the project
2. ✅ Create and configure the database
3. ✅ Update `backend/.env` with your credentials
4. ✅ Run migrations
5. ✅ Create a superuser
6. ✅ Start both frontend and backend servers
7. ✅ Visit http://localhost:5173 to see the app!

## 🎉 You're All Set!

Start building amazing features with MonkeyUI!

For questions or issues, please open an issue.

Happy coding! 🐒
