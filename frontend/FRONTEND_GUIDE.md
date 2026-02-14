# CivicQ Frontend Guide

## Project Structure

```
frontend/src/
├── components/          # Reusable UI components
│   ├── Layout.tsx       # Main layout wrapper with nav/footer
│   ├── ProtectedRoute.tsx  # Authentication guard for routes
│   ├── QuestionCard.tsx    # Display question in card format
│   ├── CandidateCard.tsx   # Display candidate in card format
│   ├── ContestCard.tsx     # Display contest in card format
│   ├── VideoPlayer.tsx     # Video player with controls
│   ├── VoteButton.tsx      # Upvote/downvote button
│   ├── LoadingSpinner.tsx  # Loading indicator
│   ├── ErrorMessage.tsx    # Error display component
│   └── index.ts            # Component exports
├── contexts/            # React contexts
│   └── AuthContext.tsx  # Authentication context
├── hooks/              # Custom React hooks
│   ├── useAuth.ts      # Authentication hooks
│   ├── useBallots.ts   # Ballot data hooks
│   ├── useCandidates.ts # Candidate data hooks
│   ├── useQuestions.ts  # Question data hooks
│   ├── useVoting.ts    # Voting hooks
│   └── index.ts        # Hook exports
├── pages/              # Page components (routes)
│   ├── HomePage.tsx    # Landing page with ballot list
│   ├── BallotPage.tsx  # Ballot details with contests
│   ├── ContestPage.tsx # Contest with candidates & questions
│   ├── QuestionPage.tsx # Question with video answers
│   └── CandidatePage.tsx # Candidate profile & portal
├── services/           # API and external services
│   └── api.ts          # API client with all endpoints
├── types/              # TypeScript type definitions
│   └── index.ts        # All interfaces and enums
├── utils/              # Utility functions
│   ├── formatting.ts   # Format helpers
│   └── validation.ts   # Validation helpers
├── App.tsx             # Main app component
└── index.tsx           # Entry point

```

## Key Features

### Authentication
- JWT-based authentication with localStorage
- Auth context provides global auth state
- Protected routes require authentication
- Automatic token refresh on API calls

### Data Fetching
- React Query for server state management
- Automatic caching and refetching
- Optimistic updates for better UX
- Error handling and retry logic

### Components

#### Layout Components
- **Layout**: Main wrapper with navigation and footer
- **ProtectedRoute**: Wraps routes requiring authentication

#### Display Components
- **QuestionCard**: Shows question with voting, tags, and metadata
- **CandidateCard**: Shows candidate photo, status, and answer count
- **ContestCard**: Shows contest type, title, and stats
- **VideoPlayer**: React Player wrapper with transcript support

#### Interactive Components
- **VoteButton**: Upvote/downvote with visual feedback
- **LoadingSpinner**: Animated loading indicator
- **ErrorMessage**: Error display with retry option

### Custom Hooks

#### Authentication
```typescript
const { user, isAuthenticated, login, logout } = useAuth();
```

#### Ballots
```typescript
const { data: ballots } = useBallots({ city_id: 'SF' });
const { data: ballot } = useBallot(ballotId);
const { data: contest } = useContest(contestId);
```

#### Questions
```typescript
const { data: question } = useQuestion(questionId);
const { data: questions } = useContestQuestions(contestId);
const createQuestion = useCreateQuestion();
```

#### Voting
```typescript
const { currentVote, upvote, downvote } = useVote(questionId);
```

#### Candidates
```typescript
const { data: candidate } = useCandidate(candidateId);
const { data: answers } = useCandidateVideoAnswers(candidateId);
```

## Page Flows

### Voter Flow
1. **HomePage** → View available ballots
2. **BallotPage** → See all contests and measures
3. **ContestPage** → View candidates and questions
4. **QuestionPage** → Watch candidate answers and vote
5. **CandidatePage** → View candidate profile and all answers

### Candidate Flow
1. **CandidatePage** → Access candidate portal
2. View questions to answer
3. Record video answers
4. Manage published/draft answers
5. Update profile information

## Styling

### Tailwind CSS
- Utility-first CSS framework
- Custom color scheme in `tailwind.config.js`:
  - `civic-blue`: Primary brand color
  - `civic-green`: Success/verification color
  - `civic-gray`: Secondary text color

### Design Principles
- Clean, accessible interface
- Responsive design (mobile-first)
- Clear visual hierarchy
- Consistent spacing and typography

## API Integration

All API calls go through the centralized API client in `services/api.ts`:

```typescript
import { ballotAPI, questionAPI, voteAPI } from './services/api';

// Get all ballots
const ballots = await ballotAPI.getAll({ city_id: 'SF' });

// Submit a question
const question = await questionAPI.create({
  contest_id: 1,
  question_text: 'What is your plan?',
});

// Vote on a question
await voteAPI.upvote(questionId);
```

## Environment Variables

Create a `.env` file based on `.env.example`:

```bash
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_ENV=development
```

## Development

### Start Development Server
```bash
npm start
```

### Build for Production
```bash
npm run build
```

### Run Tests
```bash
npm test
```

### Lint Code
```bash
npm run lint
```

## Type Safety

All data structures are typed using TypeScript interfaces in `types/index.ts`:

- `User`, `Ballot`, `Contest`, `Candidate`
- `Question`, `Vote`, `VideoAnswer`
- API response types: `PaginatedResponse<T>`, `ApiError`

## Best Practices

1. **Use custom hooks** for data fetching instead of direct API calls
2. **Leverage React Query** for automatic caching and refetching
3. **Keep components small** and focused on single responsibility
4. **Use TypeScript** for type safety and better DX
5. **Handle loading and error states** in all data-dependent components
6. **Optimize with useMemo/useCallback** for expensive operations
7. **Follow accessibility guidelines** (ARIA labels, keyboard navigation)

## Future Enhancements

- [ ] Real-time notifications with WebSockets
- [ ] Video recording directly in browser
- [ ] Advanced search and filtering
- [ ] Social sharing features
- [ ] Mobile app with React Native
- [ ] Offline support with service workers
- [ ] Analytics dashboard for candidates
- [ ] Multi-language support

## Troubleshooting

### API Connection Issues
- Check `REACT_APP_API_URL` in `.env`
- Verify backend is running
- Check CORS configuration

### Authentication Issues
- Clear localStorage: `localStorage.clear()`
- Check token expiration
- Verify credentials

### Build Issues
- Clear cache: `rm -rf node_modules && npm install`
- Check TypeScript errors: `npm run build`
- Update dependencies: `npm update`
