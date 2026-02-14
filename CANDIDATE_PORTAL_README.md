# CivicQ Candidate Portal - Demo Guide

This guide explains how to use the new Candidate Portal features that make CivicQ actually usable for politicians and candidates.

## What's New

The Candidate Portal provides a complete, working demo that politicians can use to:

1. **View questions voters are asking** - See all approved questions in their race, ranked by voter interest
2. **Record video answers** - Browser-based video recording interface (placeholder UI ready for production integration)
3. **Manage their profile** - Edit bio, contact info, priorities, and endorsements
4. **Track engagement** - Dashboard with answer statistics, views, and pending questions
5. **Onboard easily** - Step-by-step onboarding flow for new candidates

## Quick Start

### 1. Create a Demo Candidate Account

Run the demo account creation script:

```bash
cd backend
python scripts/create_demo_candidate.py
```

This creates:
- Demo user: `demo.candidate@civicq.com`
- Password: `DemoCandidate2024!`
- Candidate profile: Sarah Johnson (City Council - District 3)
- 7 sample questions awaiting answers
- 2 additional candidate profiles for comparison

### 2. Start the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

### 3. Log In as a Candidate

1. Navigate to http://localhost:3000
2. Click "Sign In"
3. Log in with:
   - Email: `demo.candidate@civicq.com`
   - Password: `DemoCandidate2024!`

### 4. Explore the Candidate Portal

Once logged in, you'll have access to:

#### Candidate Dashboard (`/candidate/dashboard`)
- **Overview Stats**: Total questions, answered/pending counts, views, answer rate
- **Questions Awaiting Answers**: List of top-ranked questions sorted by voter interest
- **Recent Activity**: Timeline of your answered questions
- **Quick Actions**: Links to edit profile, view analytics, get help

#### Answer Questions (`/candidate/answer/:questionId`)
- Click "Answer" on any pending question
- See question details with context and issue tags
- Use the **Video Answer Recorder** component:
  - Start camera (browser will ask for permissions)
  - Record up to 2 minutes
  - Review your answer before submitting
  - Submit or retake as needed

#### Edit Profile (`/candidate/profile/edit`)
- Update basic information (name, email, phone, website)
- Edit profile photo URL
- Add biography and background
- List education and experience
- Define campaign priorities
- Share endorsements

#### Onboarding (`/candidate/onboarding`)
New candidates go through a 4-step process:
1. Welcome & platform introduction
2. Verify candidacy (filing ID)
3. Complete profile information
4. Ready to start answering questions

## Features Implemented

### Backend API Endpoints

#### Candidate Dashboard
```
GET /api/candidates/{candidate_id}/dashboard
```
Returns:
- Total questions in contest
- Answered questions count
- Pending questions count
- Total views across all answers
- Total upvotes on answered questions
- Answer rate percentage
- Recent activity timeline

#### Pending Questions
```
GET /api/candidates/{candidate_id}/questions/pending
```
Returns all approved questions the candidate hasn't answered yet, sorted by rank score.

#### Update Profile
```
PUT /api/candidates/{candidate_id}/profile
```
Allows candidates to update:
- Name, email, phone, website
- Photo URL
- Custom profile fields (bio, education, experience, priorities, endorsements)

### Frontend Components

#### `CandidateDashboardPage.tsx`
Full-featured dashboard showing:
- 4 key metrics (questions, answered, pending, views)
- Visual answer rate progress bar
- List of pending questions with "Answer" buttons
- Recent activity feed
- Quick action cards

#### `VideoAnswerRecorder.tsx`
Professional video recording interface:
- Browser-based webcam/mic access
- Recording timer with 2-minute limit
- Preview before submitting
- Retake functionality
- Upload progress indicator
- Recording guidelines and tips

#### `CandidateProfileEditPage.tsx`
Comprehensive profile editor:
- Form validation
- Character counters for text areas
- Auto-save functionality
- Profile privacy notice

#### `CandidateAnswerPage.tsx`
Dedicated question answering page:
- Question context and details
- Issue tag display
- Voter engagement metrics
- Tips for great answers
- Integrated video recorder

#### `CandidateOnboardingPage.tsx`
Multi-step onboarding flow:
- Progress indicator
- Welcome screen with platform benefits
- Candidacy verification
- Profile setup
- Completion confirmation

### Navigation Integration

The navbar automatically shows:
- "Dashboard" link in main navigation for candidates
- "Candidate Dashboard" option in profile dropdown
- Mobile-responsive menu items

## Database Schema

The implementation uses existing models:
- `User` with `role='candidate'`
- `Candidate` profile linked to user
- `Contest` for the race
- `Question` with approval status
- `VideoAnswer` for recorded responses

## Video Recording Notes

The `VideoAnswerRecorder` component uses:
- **MediaRecorder API** for browser-based recording
- **getUserMedia** for camera/mic access
- WebM format with VP8 video codec
- Automatic duration tracking
- Recording state management

**For Production:**
1. Upload video blob to S3 or video hosting service
2. Generate transcript using speech-to-text API
3. Create video thumbnail
4. Add provenance hash for authenticity
5. Process video for different quality levels

## Demo Flow

Here's a complete demo flow:

1. **Login** as demo candidate
2. **View Dashboard** - See 7 pending questions
3. **Click "Answer"** on top question about housing affordability
4. **Start Camera** - Allow browser permissions
5. **Record Answer** - Practice answering the question
6. **Review & Submit** - Preview before posting
7. **Return to Dashboard** - See updated stats
8. **Edit Profile** - Add more details to candidate bio
9. **View All Questions** - Browse remaining questions to answer

## Customization

### Changing the Demo Candidate

Edit `backend/scripts/create_demo_candidate.py` to customize:
- Candidate name and details
- Contest type and jurisdiction
- Sample questions
- Profile information

### Adding More Features

Potential enhancements:
- Answer drafts (save and resume later)
- Analytics dashboard (viewer demographics, watch time)
- Question categories and filtering
- Bulk answer operations
- Campaign team collaboration

## Troubleshooting

### Camera Access Issues
- Ensure browser has camera/mic permissions
- Use HTTPS in production (required for getUserMedia)
- Check browser compatibility (Chrome, Firefox, Safari supported)

### Backend Errors
- Verify database is running and migrations are applied
- Check that demo data was created successfully
- Ensure API server is running on port 8000

### Frontend Issues
- Clear browser cache and refresh
- Check console for JavaScript errors
- Verify API_BASE_URL in frontend `.env`

## Production Considerations

Before deploying to production:

1. **Video Infrastructure**
   - Set up S3 or video hosting (Cloudflare Stream, Mux, etc.)
   - Implement server-side video processing
   - Add video compression and transcoding
   - Generate captions/transcripts

2. **Authentication**
   - Replace mock candidate_id with actual user-candidate mapping
   - Add proper authorization checks
   - Implement session management

3. **Security**
   - Add CSRF protection
   - Implement rate limiting on video uploads
   - Validate file types and sizes
   - Add provenance tracking for video authenticity

4. **User Experience**
   - Add video preview thumbnails
   - Implement auto-save for profile edits
   - Add notification system for new questions
   - Create mobile-optimized recording interface

## Support

For questions or issues:
1. Check the main README.md
2. Review API_ENDPOINTS.md for backend details
3. Check the CivicQ documentation in `/docs`

---

**Built to make local democracy more accessible for candidates and voters alike.**
