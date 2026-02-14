# CivicQ Demo Mode

CivicQ now includes a fully functional **Demo Mode** that allows voters to explore and interact with the platform even when the backend is not running!

## What is Demo Mode?

Demo Mode provides a complete, interactive experience using realistic mock data. When the backend API is unavailable, the frontend automatically switches to Demo Mode, allowing users to:

- Browse sample ballots from different cities (Los Angeles, Santa Monica, Pasadena)
- View realistic contests including mayoral races, city council races, and ballot measures
- See candidate profiles with photos and biographical information
- Read voter questions and see upvote/downvote counts
- Watch demo video answers from candidates
- Interact with voting features (votes are stored client-side in localStorage)
- Explore the full user experience without needing a running backend

## Features Available in Demo Mode

### Fully Functional Pages:
- **Home Page**: Shows all available demo ballots with city names and election dates
- **Ballot Page**: Displays contests and measures for each city
- **Contest Page**: Shows candidates and questions for each race
- **Question Page**: Displays video answers from candidates
- **Candidate Page**: Shows candidate profiles and their video answers

### Interactive Features:
- **Client-side Voting**: Upvote/downvote questions (stored in browser localStorage)
- **Video Playback**: Watch sample video answers from candidates
- **Navigation**: Full routing and navigation between pages works perfectly

### Read-Only Limitations:
- Cannot create new questions (shows helpful error message)
- Cannot submit video answers
- Cannot modify candidate profiles
- Authentication is disabled in demo mode

## Demo Mode Banner

When demo mode is active, a prominent banner appears at the top of every page:

- **Amber/orange gradient** for high visibility
- Clear messaging that this is demo data
- Dismissible (users can hide it if they understand)
- Automatically appears when backend is unavailable

## Mock Data Included

### 3 Sample Ballots:
1. **Los Angeles** - November 3, 2026
   - Mayor of Los Angeles (3 candidates)
   - City Council District 5 (2 candidates)
   - Measure A: Affordable Housing Bond

2. **Santa Monica** - November 3, 2026
   - Mayor of Santa Monica (2 candidates)

3. **Pasadena** - November 3, 2026
   - (Additional contests can be added)

### 7 Sample Candidates:
- Karen Bass, Rick Caruso, Kevin de León (LA Mayor)
- Katy Yaroslavsky, Sam Yebri (LA City Council District 5)
- Gleam Davis, Phil Brock (Santa Monica Mayor)

All candidates have:
- Realistic biographical information
- Profile photos (using placeholder avatars)
- Website links
- Professional backgrounds

### 7 Sample Questions:
- Homelessness policy
- Public transportation
- Public safety and police reform
- Affordable housing
- Sustainable development
- Parks and recreation
- Small business support

### Video Answers:
- Multiple video answers per question
- Sample videos using Creative Commons test videos
- Full metadata including transcripts, position summaries, rationales
- Implementation plans and success metrics

## How It Works Technically

### Automatic Fallback
The API service automatically detects when the backend is unavailable and switches to demo mode:

```typescript
try {
  const response = await apiClient.get('/ballots');
  return response.data;
} catch (error) {
  if (axios.isAxiosError(error) && (!error.response || error.code === 'ERR_NETWORK')) {
    setDemoMode(true);
    return getMockBallots();
  }
  throw error;
}
```

### Demo Mode State
- Tracked via `services/demoMode.ts`
- Global flag accessible throughout the app
- Persists for the session
- Console logs when demo mode is activated

### Data Structure
- All mock data in `data/mockData.ts`
- Matches production TypeScript interfaces exactly
- Properly typed and validated
- Easy to extend with more data

## Running in Demo Mode

### Option 1: No Backend Running
Simply start the frontend without the backend:

```bash
cd frontend
npm start
```

The app will automatically enter demo mode when it cannot connect to the API.

### Option 2: Force Demo Mode
Demo mode activates automatically when API calls fail. No configuration needed!

## For Developers

### Adding More Mock Data

To add more sample ballots, contests, or candidates:

1. Edit `frontend/src/data/mockData.ts`
2. Add new entries to the relevant arrays (MOCK_BALLOTS, MOCK_CONTESTS, etc.)
3. Ensure IDs are unique
4. Follow the existing data structure

### Customizing the Banner

Edit `frontend/src/components/DemoModeBanner.tsx` to change:
- Colors and styling
- Messaging
- Dismiss behavior
- Position

## Benefits for Voters

Demo Mode makes CivicQ accessible to everyone:

1. **Try Before Registering**: Explore the full interface without creating an account
2. **See Real Examples**: Understand how candidates answer questions
3. **Learn the System**: Get familiar with the voting and question workflow
4. **Test the Interface**: See if CivicQ meets your needs before your city adopts it
5. **Share and Demonstrate**: Show others how CivicQ works without setup

## Benefits for Developers

1. **Faster Development**: Test UI changes without running the backend
2. **Demo Presentations**: Show stakeholders the full experience instantly
3. **Integration Testing**: Verify frontend logic with controlled data
4. **Documentation**: Living examples of how data flows through the app

## Future Enhancements

Potential improvements to demo mode:

- [ ] Add more cities and elections
- [ ] Include more diverse candidates
- [ ] Add ballot measure examples (Yes/No questions)
- [ ] Sample rebuttal videos
- [ ] Claim verification examples
- [ ] Multiple election cycles
- [ ] Different types of local races (school board, judges, etc.)

## Technical Details

**Files Modified/Created:**
- `frontend/src/data/mockData.ts` - All sample data
- `frontend/src/services/demoMode.ts` - Demo mode state management
- `frontend/src/services/api.ts` - Fallback logic for all API calls
- `frontend/src/components/DemoModeBanner.tsx` - User notification banner
- `frontend/src/components/Layout.tsx` - Banner integration
- `frontend/src/pages/SimpleHomePage.tsx` - Ballot list display

**Dependencies:**
- No new dependencies required
- Uses existing React Query infrastructure
- Leverages TypeScript type safety

---

**Demo Mode makes CivicQ accessible, demonstrable, and ready to showcase to voters, cities, and stakeholders without requiring full backend infrastructure!**
