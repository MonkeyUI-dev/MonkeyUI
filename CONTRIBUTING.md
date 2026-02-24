# Contributing to MonkeyUI

Thank you for your interest in contributing to MonkeyUI! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and professional in all interactions.

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a new branch for your feature/fix
4. Make your changes
5. Test your changes
6. Submit a pull request

## Development Setup

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend
pipenv install --dev
pipenv shell
python manage.py migrate
python manage.py runserver
```

## Coding Standards

### General

- Write code in English
- All user-facing text must use i18n
- Add both English and Chinese translations
- Follow existing code patterns

### Frontend (React)

- Use functional components
- Follow React Hooks best practices
- Use Shadcn/ui components when available
- Follow TailwindCSS utility-first approach

### Backend (Django)

- Follow PEP 8
- Use class-based views or ViewSets
- Document all views and serializers
- Use Django's translation utilities

## Commit Messages

Follow conventional commits format:

```
type(scope): description

[optional body]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(auth): add JWT authentication
fix(api): resolve CORS issue
docs(readme): update installation instructions
```

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass
4. Update the README if needed
5. Request review from maintainers

## Questions?

Feel free to open an issue for any questions or concerns.
