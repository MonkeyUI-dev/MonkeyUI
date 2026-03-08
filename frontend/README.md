# Frontend

React + Vite frontend application for MonkeyUI.

## Setup

```bash
npm install
npm run dev
```

## Tech Stack

- React 18
- Vite
- TailwindCSS
- Shadcn/ui
- React Router
- i18next (internationalization)
- Axios

## Project Structure

```
frontend/
├── public/
│   └── locales/          # i18n translation files
├── src/
│   ├── components/       # React components
│   │   └── ui/          # Shadcn/ui components
│   ├── lib/             # Utilities
│   ├── App.jsx          # Main app component
│   ├── i18n.js          # i18n configuration
│   ├── main.jsx         # Entry point
│   └── index.css        # Global styles
├── index.html
├── vite.config.js
├── tailwind.config.js
└── package.json
```

## Adding Shadcn/ui Components

To add more Shadcn/ui components:

```bash
npx shadcn-ui@latest add [component-name]
```

For example:
```bash
npx shadcn-ui@latest add card
npx shadcn-ui@latest add input
npx shadcn-ui@latest add dialog
```

## i18n Usage

```jsx
import { useTranslation } from 'react-i18next';

function MyComponent() {
  const { t } = useTranslation();
  
  return <div>{t('common.save')}</div>;
}
```

## Environment Variables

Create a `.env` file:

```
VITE_API_URL=http://localhost:8000/api
VITE_GA_MEASUREMENT_ID=G-XXXXXXXXXX
```

`VITE_GA_MEASUREMENT_ID` is optional. When it is not set, Google Analytics is not initialized and no page view events are sent.
