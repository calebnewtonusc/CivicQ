# CivicQ Demo Quickstart for Voters

Welcome to CivicQ! This demo lets you explore a fully functional civic engagement platform.

## How to Start Exploring

### Option 1: Just Open the Frontend (Easiest)

```bash
cd frontend
npm install
npm start
```

The app will automatically load with demo data when the backend isn't running.

### Option 2: With Backend (Full Experience)

```bash
# Terminal 1 - Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm install
npm start
```

## What You Can Do in Demo Mode

### 1. Browse Ballots
- **Home Page**: See available ballots for Los Angeles, Santa Monica, and Pasadena
- Click on any city to view their full ballot

### 2. Explore Contests
From any ballot, you can:
- View mayoral races
- See city council contests
- Read about ballot measures

### 3. View Candidates
Each contest shows real candidate profiles with:
- Professional photos
- Biographical information
- Campaign websites
- Number of questions answered

### 4. Read Questions
See what voters are asking:
- Homelessness solutions
- Transportation improvements
- Public safety policies
- Housing affordability
- Environmental initiatives

Questions show real upvote/downvote counts!

### 5. Watch Video Answers
Click on any question to:
- See which candidates have answered
- Watch their video responses
- Read transcripts
- Review their policy details:
  - Position summary
  - Rationale
  - Implementation plan
  - Success metrics
  - Values statement

### 6. Vote on Questions (Demo)
While viewing questions, you can:
- Upvote questions you care about
- Downvote questions you find less important
- See your vote count update (stored locally)
- Change your vote at any time

### 7. Navigate Seamlessly
- Every link works
- Back button works
- All pages load properly
- Full responsive design

## Demo Data Included

### Cities & Elections
- **Los Angeles** - Nov 3, 2026
  - 3 contests (Mayor, City Council, Measure A)
  - 5 candidates total
  - 4 questions with video answers

- **Santa Monica** - Nov 3, 2026
  - 1 contest (Mayor)
  - 2 candidates
  - 1 question

### Sample Candidates
- Karen Bass (LA Mayor)
- Rick Caruso (LA Mayor)
- Kevin de León (LA Mayor)
- Katy Yaroslavsky (City Council)
- Sam Yebri (City Council)
- Gleam Davis (Santa Monica Mayor)
- Phil Brock (Santa Monica Mayor)

### Sample Questions
1. How will you address homelessness?
2. What's your plan for public transportation?
3. What are your priorities for public safety?
4. How will you tackle affordable housing?
5. What's your vision for sustainable development?
6. How will you improve parks and recreation?
7. What's your plan for small businesses?

## Interactive Features That Work

### Working Features:
- Voting on questions (client-side)
- Video playback
- Navigation between pages
- Filtering and sorting
- Responsive mobile design

### Demo-Only Limitations:
- Can't create new questions (shows helpful message)
- Can't log in (auth is disabled)
- Can't submit video answers
- Can't edit profiles

## Demo Mode Indicator

You'll see an orange banner at the top when in demo mode:

**"Demo Mode Active - You're viewing demo data. Features like voting and authentication are simulated."**

You can dismiss this banner if you understand you're using demo data.

## Testing Different Scenarios

### Try These Workflows:

1. **Voter Journey**:
   - Home → Pick Los Angeles → View Mayor Race → Click Karen Bass → Watch her answer on homelessness

2. **Question Explorer**:
   - Home → Los Angeles → Mayor Race → Click "How will you address homelessness?" → See all 3 candidates' video answers

3. **Candidate Comparison**:
   - View Mayor race → Compare all candidates side by side → Watch their answers to the same questions

4. **Issue-Based Research**:
   - Search for questions about housing → See which candidates have answered → Compare their approaches

## Sharing the Demo

Perfect for:
- Showing city officials what CivicQ can do
- Presenting to civic organizations
- Getting voter feedback on the interface
- Testing user flows without setup
- Screenshots and recordings
- Live demonstrations

## Technical Notes

### Browser Support
- Chrome, Firefox, Safari, Edge (latest versions)
- Works on mobile devices
- Responsive design adapts to all screen sizes

### Performance
- Instant loading (no API calls)
- Smooth video playback
- No backend required
- Works offline after initial load

### Data Persistence
- Votes stored in browser localStorage
- Resets when you clear browser data
- No server-side storage in demo mode

## Next Steps

Interested in deploying CivicQ for your city? See:
- `DEPLOYMENT.md` - Full deployment guide
- `README.md` - Complete project overview
- `SETUP.md` - Development environment setup

## Questions?

This is a demonstration of CivicQ's capabilities. The real platform would connect to a live backend with actual election data from your city.

---

**Enjoy exploring CivicQ!** This demo shows how local democracy can be more transparent, accessible, and focused on what voters actually care about.
