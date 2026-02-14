# CivicQ Frontend - Quick Start Guide

## Setup (First Time)

```bash
# Navigate to frontend directory
cd /Users/joelnewton/Desktop/2026-Code/projects/CivicQ/frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Update .env with your API URL
# REACT_APP_API_URL=http://localhost:8000/api

# Start development server
npm start
```

The app will open at http://localhost:3000

## Common Development Tasks

### Running the App
```bash
npm start          # Start development server
npm run build      # Build for production
npm test           # Run tests
npm run lint       # Lint code
```

### Working with Components

Import from centralized exports:
```typescript
import { Layout, QuestionCard, VoteButton } from '../components';
```

### Working with Hooks

```typescript
import { useAuth, useBallot, useVote } from '../hooks';

function MyComponent() {
  const { user, isAuthenticated } = useAuth();
  const { data: ballot, isLoading } = useBallot(ballotId);
  const { upvote, downvote } = useVote(questionId);

  // Your component logic
}
```

### Working with API

```typescript
import { ballotAPI, questionAPI } from '../services/api';

// In a mutation or async function
const ballot = await ballotAPI.getById(1);
const question = await questionAPI.create({
  contest_id: 1,
  question_text: 'What is your plan?'
});
```

### Adding a New Page

1. Create file in `src/pages/NewPage.tsx`
2. Import Layout and any needed components
3. Add route in `src/App.tsx`:
```typescript
<Route path="/new-path" element={<NewPage />} />
```

### Adding a New Component

1. Create file in `src/components/MyComponent.tsx`
2. Export from `src/components/index.ts`:
```typescript
export { default as MyComponent } from './MyComponent';
```
3. Use in pages:
```typescript
import { MyComponent } from '../components';
```

### Adding a New Hook

1. Create file in `src/hooks/useMyHook.ts`
2. Export from `src/hooks/index.ts`:
```typescript
export * from './useMyHook';
```
3. Use in components:
```typescript
import { useMyHook } from '../hooks';
```

## Project Structure Quick Reference

```
src/
├── components/     # UI components (Layout, Cards, Buttons)
├── contexts/       # React contexts (Auth)
├── hooks/          # Custom hooks (useAuth, useBallot, etc.)
├── pages/          # Page components (Home, Ballot, Contest, etc.)
├── services/       # API client
├── types/          # TypeScript types
├── utils/          # Helper functions
├── App.tsx         # Main app with routing
└── index.tsx       # Entry point
```

## Common Patterns

### Loading State
```typescript
if (isLoading) return <LoadingSpinner />;
if (error) return <ErrorMessage message="..." />;
return <YourComponent data={data} />;
```

### Protected Content
```typescript
const { isAuthenticated } = useAuth();

{isAuthenticated ? (
  <AuthenticatedContent />
) : (
  <Link to="/login">Login to continue</Link>
)}
```

### Form Submission
```typescript
const createMutation = useCreateQuestion();

const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  try {
    await createMutation.mutateAsync(formData);
    // Success handling
  } catch (error) {
    // Error handling
  }
};
```

### Navigation
```typescript
import { useNavigate, Link } from 'react-router-dom';

// Programmatic navigation
const navigate = useNavigate();
navigate('/ballot');

// Link component
<Link to="/ballot">View Ballot</Link>
```

## Styling Tips

### Tailwind Classes
```typescript
// Card
className="bg-white rounded-lg shadow-md p-6"

// Button (primary)
className="px-6 py-2 bg-civic-blue text-white rounded-lg hover:bg-blue-700"

// Button (secondary)
className="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"

// Grid layout
className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"

// Flex layout
className="flex items-center justify-between"
```

### Custom Colors
- `civic-blue` - Primary brand color (#1E40AF)
- `civic-green` - Success/verification (#059669)
- `civic-gray` - Secondary text (#6B7280)

## Debugging Tips

### Check API Calls
Open browser DevTools → Network tab → Filter by XHR

### Check React Query Cache
Install React Query DevTools:
```typescript
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

// In App.tsx
<ReactQueryDevtools initialIsOpen={false} />
```

### Check Auth State
```typescript
const { user } = useAuth();
console.log('Current user:', user);
console.log('Token:', localStorage.getItem('access_token'));
```

### Clear Cache/Reset
```typescript
// In browser console
localStorage.clear();
window.location.reload();
```

## Environment Variables

Add to `.env` (don't commit):
```bash
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_ENV=development
```

Access in code:
```typescript
const apiUrl = process.env.REACT_APP_API_URL;
```

## Common Issues

### API Connection Failed
- Check backend is running
- Verify `REACT_APP_API_URL` in `.env`
- Check CORS configuration on backend

### 401 Unauthorized
- Token expired - log out and log back in
- Clear localStorage: `localStorage.clear()`

### Build Fails
- Check for TypeScript errors
- Run `npm install` to ensure dependencies are up to date
- Delete `node_modules` and reinstall

### Component Not Found
- Check import path is correct
- Verify export in barrel file (index.ts)
- Restart dev server

## Helpful Commands

```bash
# Find all TypeScript files
find src -name "*.ts*"

# Count lines of code
find src -name "*.ts*" | xargs wc -l

# Search for text in code
grep -r "searchTerm" src/

# Format all files
npm run format
```

## Resources

- **React Docs**: https://react.dev
- **React Router**: https://reactrouter.com
- **React Query**: https://tanstack.com/query
- **Tailwind CSS**: https://tailwindcss.com
- **TypeScript**: https://www.typescriptlang.org

## Getting Help

1. Check FRONTEND_GUIDE.md for detailed documentation
2. Check IMPLEMENTATION_SUMMARY.md for architecture overview
3. Review existing components for patterns
4. Check browser console for errors
5. Use TypeScript hints in your IDE

## Next Steps

1. Start backend: `cd ../backend && make dev`
2. Test authentication flow
3. Browse ballots and contests
4. Submit questions and vote
5. Watch candidate video answers
6. Explore candidate portal (if logged in as candidate)

Happy coding! 🚀
