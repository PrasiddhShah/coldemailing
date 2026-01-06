# Apollo Cold Emailer - Frontend

React frontend for the Apollo Cold Emailer application built with Vite.

## Tech Stack

- **React 19.2** - UI framework
- **Vite 7.2** - Build tool and dev server
- **ESLint** - Code linting
- **Vanilla CSS** - Minimal styling (no frameworks)

## Project Structure

```
web/
├── src/
│   ├── App.jsx              # Main application container
│   ├── App.css              # Component styles (mostly unused)
│   ├── index.css            # Global styles & CSS variables
│   ├── main.jsx             # React entry point
│   └── components/
│       ├── SearchForm.jsx   # Company/role search interface
│       ├── ContactGrid.jsx  # Contact card grid display
│       └── EmailComposer.jsx # Email drafting modal
├── index.html               # HTML entry point
├── package.json             # Dependencies
├── vite.config.js           # Vite configuration
└── eslint.config.js         # ESLint rules
```

## Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

## Development

### Running the Frontend

```bash
npm run dev
```

Starts dev server at http://localhost:5173

**Important:** The backend must be running on port 8000 for API calls to work.

### API Configuration

The frontend connects to the backend API at `http://localhost:8000/api`:

```javascript
const API_BASE = 'http://localhost:8000/api';
```

If you change the backend port, update this in:
- `src/App.jsx` (line 6)
- `src/components/EmailComposer.jsx` (line 30)

## Components

### App.jsx

Main application container that manages:
- Contact state
- Company context (job descriptions per company)
- Search/enrich/email workflows
- Notifications

**State:**
- `contacts` - Array of contact objects
- `draftingContact` - Currently selected contact for emailing
- `companyContexts` - Saved job descriptions by company name
- `isLoading` - Loading state for searches
- `error` - Error messages
- `notification` - Toast notifications

### SearchForm.jsx

Company and role search interface.

**Props:**
- `onSearch(params)` - Callback when search submitted
- `isLoading` - Disable form during search

**Features:**
- Company name/domain input
- Multi-select role buttons (6 role types)
- Max results slider
- Form validation

### ContactGrid.jsx

Grid display of contact cards.

**Props:**
- `contacts` - Array of contact objects
- `onEnrich(contact)` - Callback to enrich single contact
- `onDraftEmail(contact)` - Callback to open email composer

**Features:**
- Responsive grid layout (auto-fill, min 300px)
- Status badges (Enriched/No Email)
- Conditional buttons based on email status
- Shows: name, title, company, location, email

### EmailComposer.jsx

Full-screen modal for email drafting.

**Props:**
- `contact` - Contact object to email
- `onClose()` - Close modal callback
- `onSend(emailData)` - Send email callback
- `savedContext` - Saved job description for company
- `savedJobLink` - Saved job posting URL
- `onUpdateContext(desc, link)` - Save context callback

**Features:**
- Two-panel layout (context + composer)
- AI email generation button
- Subject/body editing
- Resume attachment toggle
- Context persistence across contacts

## Styling

### Theme (index.css)

Minimal dark theme with CSS variables:

```css
--bg-primary: #0a0a0a      /* Main background */
--bg-secondary: #141414    /* Secondary surfaces */
--bg-card: #1a1a1a         /* Card backgrounds */
--text-primary: #e5e5e5    /* Main text */
--text-secondary: #888888  /* Secondary text */
--border-color: #2a2a2a    /* Borders */
```

### Design Principles

- **Minimal**: No colors, black/white/gray only
- **Flat**: No shadows or gradients
- **Simple**: Clean lines and consistent spacing
- **Readable**: High contrast, clear hierarchy

## API Integration

### Endpoints Used

**POST /api/search**
```javascript
{
  company: "google.com",
  roles: ["recruiter"],
  limit: 10
}
```

**POST /api/enrich**
```javascript
{
  contacts: [{ id, first_name, last_name, ... }]
}
```

**POST /api/generate-email**
```javascript
{
  contact: { ... },
  user_context: "job description",
  job_link: "https://..."
}
```

**POST /api/send-email**
```javascript
{
  to_email: "john@example.com",
  subject: "...",
  body: "...",
  attach_resume: true
}
```

## Build & Deploy

### Production Build

```bash
npm run build
```

Creates optimized build in `dist/` folder:
- Minified JavaScript
- Optimized CSS
- Compressed assets

### Preview Production Build

```bash
npm run preview
```

Serves production build locally for testing.

### Deployment Options

**Static Hosting:**
- Netlify
- Vercel
- GitHub Pages
- AWS S3 + CloudFront

**Important:** Update `API_BASE` URL to your production backend URL before deploying.

## Environment Variables

Create `.env.local` for frontend-specific config:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

Then use in code:
```javascript
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
```

## Development Tips

### Hot Module Replacement

Vite provides instant HMR - changes appear without full page reload.

### React DevTools

Install React DevTools browser extension for debugging:
- Chrome: https://chrome.google.com/webstore
- Firefox: https://addons.mozilla.org/

### VS Code Extensions

Recommended extensions:
- ESLint
- Prettier
- ES7+ React/Redux/React-Native snippets

### Common Issues

**"Failed to fetch"**
- Backend not running
- CORS issue (check backend CORS config)
- Wrong API URL

**"Blank page"**
- Check browser console for errors
- Verify `npm run dev` is running
- Check port 5173 is available

**"Module not found"**
- Run `npm install`
- Delete `node_modules` and reinstall

## Code Style

### ESLint Configuration

Custom ESLint rules in `eslint.config.js`:
- React hooks rules
- React refresh plugin
- No unused vars warnings

Run linter:
```bash
npm run lint
```

### Component Patterns

**Functional Components:**
```javascript
const MyComponent = ({ prop1, prop2 }) => {
  return <div>{prop1}</div>;
};
```

**Hooks:**
```javascript
const [state, setState] = useState(initialValue);
useEffect(() => { /* side effects */ }, [deps]);
```

**Event Handlers:**
```javascript
const handleClick = async () => {
  // async operations
};
```

## Testing

Currently no tests configured. To add:

```bash
npm install --save-dev vitest @testing-library/react
```

Create `vite.config.js` test config:
```javascript
export default {
  test: {
    environment: 'jsdom',
  }
}
```

## Performance

### Optimizations Applied

- Vite code splitting
- CSS minification
- Image optimization
- Tree shaking

### Future Improvements

- Lazy load components
- Virtual scrolling for large contact lists
- Service worker for offline support
- Image lazy loading

## Browser Support

Targets modern browsers:
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## License

Part of Apollo Cold Emailer project - personal use only.

## Contributing

This is a personal project, but feel free to fork and customize for your needs.

## Resources

- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vite.dev/)
- [ESLint Rules](https://eslint.org/docs/rules/)
