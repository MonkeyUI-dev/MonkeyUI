# GitHub Copilot Instructions for MonkeyUI

## Project Overview
This is a monorepo full-stack application with React frontend and Django backend.

## Code Standards

### General Guidelines
- **Primary Language**: English for all code, comments, documentation, and user-facing text
- **Internationalization**: Support i18n for English and Chinese languages
  - Always use i18n keys instead of hardcoded strings in UI components
  - Frontend: Use `react-i18next` with translation keys
  - Backend: Use Django's translation utilities (`gettext`, `ugettext_lazy`)
- **Code Style**: Follow industry best practices for React and Django
- **Comments**: Write clear, concise comments in English

### Frontend (React + Vite + TailwindCSS)
- Use functional components with React Hooks
- Prefer TypeScript for type safety (if using TS)
- Use Shadcn/ui components when possible
- Follow Tailwind utility-first approach
- Keep components small and focused
- Use proper semantic HTML
- Organize imports: React → Third-party → Local components → Utilities → Styles

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

### Backend (Django + DRF)
- Follow Django project structure best practices
- Use class-based views or ViewSets for DRF
- Implement proper serializers for API endpoints
- Use environment variables for sensitive configuration
- Keep models focused and normalized
- Write comprehensive docstrings for views and serializers
- Use Django's translation utilities for all user-facing strings

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

### Database (PostgreSQL + pgvector)
- Use meaningful table and column names in snake_case
- Always include created_at and updated_at timestamps
- Add appropriate indexes for query optimization
- Use pgvector for vector similarity search when needed

**Model Example:**
```python
from django.db import models
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

## Design System

MonkeyUI follows a **minimalist black-and-white design aesthetic** inspired by Notion, with carefully chosen accent colors for emphasis. All generated UI components should adhere to this design language.

### Design Principles
- **Minimalism First**: Clean, uncluttered interfaces with generous whitespace
- **High Contrast**: Strong black-on-white contrast for readability
- **Selective Accent**: Use vibrant accent colors (red, yellow, blue) sparingly for emphasis and CTAs
- **Subtle Depth**: Prefer borders over heavy shadows; use subtle shadows only when needed
- **Modern Typography**: Sans-serif fonts with clear hierarchy (extra-bold headings, regular body text)

### CSS Variables Reference

Apply these CSS custom properties in your components to maintain visual consistency:

```css
:root {
  /* =========================================================
   * Brand Colors
   * ========================================================= */
  --brand-primary: #000000;    /* Pure black for primary brand */
  --brand-secondary: #2A99D3;  /* Blue accent for secondary elements */

  /* =========================================================
   * Neutral Colors
   * ========================================================= */
  --bg-canvas: #FFFFFF;        /* Main background (pure white) */
  --bg-surface: #F8F8F8;       /* Secondary surface (subtle gray) */
  
  --border-subtle: #E8E8E8;    /* Light borders/dividers */
  --border-default: #E0E0E0;   /* Default borders */
  
  --text-primary: #101010;     /* Main text (near-black) */
  --text-secondary: #525252;   /* Secondary text (medium gray) */
  --text-tertiary: #737373;    /* Tertiary text (light gray) */
  --text-on-dark: #FFFFFF;     /* Text on dark backgrounds */

  /* =========================================================
   * Accent Colors (Use Sparingly)
   * ========================================================= */
  --accent-red: #F8534E;       /* Red for highlights/illustrations */
  --accent-yellow: #FBC113;    /* Yellow for warnings/highlights */
  --accent-blue: #2A99D3;      /* Blue for icons/interactive elements */

  /* =========================================================
   * Functional Colors
   * ========================================================= */
  --color-success: #22C55E;    /* Success states */
  --color-warning: #F59E0B;    /* Warning states */
  --color-error: #EF4444;      /* Error states */
  --color-info: #3B82F6;       /* Info states */

  /* =========================================================
   * Typography
   * ========================================================= */
  --font-sans: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans";
  
  --font-weight-heading: 800;  /* Extra-bold for headings */
  --font-weight-body: 400;     /* Regular for body text */
  
  --text-h1-size: 4rem;        /* ~64px for hero headings */
  --text-h1-line: 1.05;
  --text-body-size: 1.125rem;  /* ~18px for body text */
  --text-body-line: 1.6;

  /* =========================================================
   * Spacing & Radius
   * ========================================================= */
  --radius-md: 10px;           /* Medium border radius for buttons/cards */

  /* =========================================================
   * Elevation (Shadows)
   * ========================================================= */
  --shadow-none: none;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.06);      /* Subtle hover states */
  --shadow-md: 0 8px 24px rgba(0, 0, 0, 0.12);     /* Dropdowns/popovers */
  --shadow-lg: 0 16px 48px rgba(0, 0, 0, 0.16);    /* Modals (use sparingly) */

  /* =========================================================
   * Component Semantics
   * ========================================================= */
  --btn-primary-bg: #101010;   /* Primary button background */
  --btn-primary-fg: #FFFFFF;   /* Primary button text */
  --link-default: #2A99D3;     /* Default link color */
}
```

### Using Design Tokens with Tailwind

When Tailwind classes align with our design system, prefer them. Otherwise, use CSS variables:

```jsx
// ✅ Good: Using CSS variables for custom colors
<div className="bg-white border" style={{ borderColor: 'var(--border-subtle)' }}>
  <h1 style={{ color: 'var(--text-primary)', fontWeight: 'var(--font-weight-heading)' }}>
    {t('hero.title')}
  </h1>
</div>

// ✅ Good: Using Tailwind for standard utilities
<Button className="rounded-xl bg-black text-white px-6 py-3">
  {t('common.getStarted')}
</Button>

// ❌ Avoid: Hardcoding colors
<div className="bg-[#F8F8F8]">...</div>
```

### Component Design Guidelines

1. **Buttons**: Use `--btn-primary-bg` with `--radius-md` for primary CTAs
2. **Text Hierarchy**: H1 should use `--font-weight-heading` (800), body uses `--font-weight-body` (400)
3. **Spacing**: Embrace whitespace; use generous padding around key sections
4. **Borders Over Shadows**: Prefer subtle borders (`--border-subtle`) to separate sections
5. **Accent Colors**: Reserve for interactive elements, icons, and key highlights only

## i18n Implementation

### Frontend i18n Setup
- Translation files location: `frontend/src/locales/`
- Structure: `locales/en/translation.json` and `locales/zh/translation.json`
- Always add both English and Chinese translations when creating new keys
- Use nested keys for better organization: `{ "common": { "button": { "save": "Save" } } }`

### Backend i18n Setup
- Use Django's internationalization framework
- Mark all user-facing strings with `gettext_lazy` or `gettext`
- Generate translation files: `python manage.py makemessages -l zh_Hans`
- Compile translations: `python manage.py compilemessages`

## Testing
- Write unit tests for critical business logic
- Frontend: Use Vitest or Jest
- Backend: Use Django's test framework or pytest
- Aim for meaningful test coverage, not just high percentages

## Security
- Never commit sensitive credentials or API keys
- Always validate and sanitize user input
- Use Django's built-in security features (CSRF, XSS protection)
- Implement proper authentication and authorization

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
8. **Visual Consistency**: Generated UI should reflect the minimalist Notion-inspired aesthetic
