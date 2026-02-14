# CivicQ Candidate Portal - Demo Quick Reference

## 🚀 Quick Start

### 1. Setup (One Time)
```bash
cd /path/to/CivicQ
./setup-candidate-demo.sh
```

### 2. Run Application (Every Time)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

### 3. Access Demo
- URL: http://localhost:3000
- Email: `demo.candidate@civicq.com`
- Password: `DemoCandidate2024!`

---

## 📍 Key Pages

| Page | URL | Purpose |
|------|-----|---------|
| Dashboard | `/candidate/dashboard` | Main hub, view questions & stats |
| Answer Question | `/candidate/answer/:id` | Record video answers |
| Edit Profile | `/candidate/profile/edit` | Update candidate info |
| Onboarding | `/candidate/onboarding` | New candidate setup flow |

---

## 🎯 Demo Flow (5 Minutes)

### Flow 1: View & Answer Questions
1. **Login** with demo credentials
2. **Click** "Dashboard" in navigation
3. **Review** 7 pending questions
4. **Click** "Answer" on housing question (127 upvotes)
5. **Grant** camera permissions
6. **Record** a practice answer
7. **Preview** and submit
8. **Return** to dashboard to see updated stats

### Flow 2: Manage Profile
1. **Navigate** to Dashboard
2. **Click** "Edit Profile" quick action
3. **Update** biography field
4. **Add** campaign priorities
5. **Save** changes
6. **View** updated profile

### Flow 3: New Candidate Onboarding
1. **Navigate** to `/candidate/onboarding`
2. **Step through** 4-part flow:
   - Welcome & benefits
   - Verify candidacy
   - Complete profile
   - Ready to start
3. **Land** on dashboard ready to answer

---

## 📊 Dashboard Metrics Explained

| Metric | Description | Demo Value |
|--------|-------------|------------|
| Total Questions | All approved questions in your race | 7 |
| Answered | Questions you've answered | 0 (start) |
| Pending | Questions awaiting your answer | 7 (start) |
| Total Views | Video answer views across all responses | 0 (start) |
| Answer Rate | Percentage of questions answered | 0% (start) |

---

## 🎥 Video Recorder Features

### Controls
- **Start Camera** - Request browser permissions
- **Start Recording** - Begin recording (max 2 min)
- **Stop Recording** - End and preview
- **Retake** - Record again
- **Submit Answer** - Upload and publish

### Guidelines
- Good lighting (face camera)
- Clear audio (test microphone)
- Answer directly (be concise)
- Stay under 2 minutes
- Review before submitting

---

## 👤 Demo Account Details

### Candidate Profile
- **Name**: Sarah Johnson
- **Race**: City Council - District 3
- **Location**: Santa Monica, CA
- **Election**: November 5, 2024
- **Filing ID**: CC-D3-2024-001

### Sample Questions (7 total)

1. **Housing Affordability** (127 upvotes, 8.5 score)
   - Issue tags: housing, affordability, development

2. **Homelessness** (143 upvotes, 9.1 score)
   - Issue tags: homelessness, social services, housing

3. **Small Business Support** (89 upvotes, 7.2 score)
   - Issue tags: economy, small business, sustainability

4. **Public Transportation** (76 upvotes, 6.8 score)
   - Issue tags: transportation, public transit, infrastructure

5. **Beach Development** (92 upvotes, 7.5 score)
   - Issue tags: development, environment, beaches

6. **Public Safety** (105 upvotes, 8.0 score)
   - Issue tags: public safety, police, community

7. **Government Transparency** (68 upvotes, 6.4 score)
   - Issue tags: governance, transparency, accountability

---

## 🔧 Troubleshooting

### Camera Not Working
- Check browser permissions (Settings → Privacy → Camera)
- Use Chrome, Firefox, or Safari
- Ensure no other apps are using camera
- Try reloading the page

### Can't Login
- Verify: `demo.candidate@civicq.com`
- Password: `DemoCandidate2024!` (case sensitive)
- Check backend is running on port 8000
- Clear browser cache/cookies

### Backend Won't Start
```bash
# Check if database exists
psql -l | grep civicq

# If not, create it
createdb civicq

# Run migrations
cd backend
alembic upgrade head
```

### Frontend Won't Start
```bash
# Install dependencies
cd frontend
npm install

# Clear cache and restart
rm -rf node_modules package-lock.json
npm install
npm start
```

### Demo Account Missing
```bash
# Recreate demo data
cd backend
python scripts/create_demo_candidate.py
```

---

## 🎨 UI Components

### Dashboard Cards
- **Blue border**: Active/clickable
- **Green icon**: Completed status
- **Yellow icon**: Pending status
- **Purple icon**: Views/metrics

### Status Badges
- **Green**: Published
- **Yellow**: Processing/Draft
- **Red**: Withdrawn
- **Gray**: Inactive

### Buttons
- **Blue**: Primary action (Submit, Save)
- **Green**: Success action (Publish)
- **Red**: Destructive action (Delete, Record)
- **Gray**: Secondary action (Cancel, Back)

---

## 📱 Mobile Testing

To test mobile view:
1. Open browser dev tools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Select device (iPhone, iPad, etc.)
4. Reload page

Mobile features:
- Responsive cards
- Hamburger menu
- Touch-friendly buttons
- Optimized video recorder

---

## 🔑 Admin Access (Coming Soon)

Future admin features:
- Approve/moderate questions
- View all candidate answers
- Generate reports
- Manage contests/ballots

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `CANDIDATE_PORTAL_README.md` | Complete usage guide |
| `CANDIDATE_PORTAL_IMPLEMENTATION.md` | Technical details |
| `FEATURES_OVERVIEW.md` | Feature descriptions |
| `DEMO_QUICK_REFERENCE.md` | This file - quick lookup |
| `README.md` | Main project documentation |

---

## 🚦 API Endpoints Reference

### Authentication
```
POST /api/auth/login
POST /api/auth/signup
GET  /api/auth/me
```

### Candidate Portal
```
GET  /api/candidates/{id}/dashboard
GET  /api/candidates/{id}/questions/pending
PUT  /api/candidates/{id}/profile
POST /api/candidates/{id}/answers
GET  /api/candidates/{id}/answers
```

### Questions
```
GET  /api/questions/{id}
GET  /api/contests/{id}/questions
POST /api/questions/{id}/vote
```

---

## 💡 Demo Tips

### For Best Results
1. **Prepare talking points** before recording
2. **Test camera/mic** first time through
3. **Keep answers under 90 seconds** (not full 2 min)
4. **Answer top-ranked questions first**
5. **Complete profile** before answering

### Things to Showcase
- Question ranking by voter interest
- Real-time recording and preview
- Dashboard stats and metrics
- Profile editing capabilities
- Mobile responsiveness

### Common Questions
- **Can I edit answers?** No - ensures authenticity
- **How many questions should I answer?** Aim for 80%+ answer rate
- **Can voters see drafts?** No - only published answers
- **How are questions ranked?** Voter upvotes + algorithm

---

## 🎬 Script for Live Demo

> "Let me show you CivicQ's Candidate Portal..."

**[Login Page]**
> "I'll log in as our demo candidate, Sarah Johnson, who's running for City Council."

**[Dashboard]**
> "Here's the candidate dashboard. Sarah has 7 questions from voters awaiting answers.
> We can see the top question about housing affordability has 127 upvotes -
> clearly a priority for the community."

**[Answer Page]**
> "When I click 'Answer', I see the full question with context.
> The video recorder lets me record directly in the browser -
> no special software needed. I can preview before submitting,
> and the video is permanent and uneditable to ensure authenticity."

**[Profile]**
> "Candidates can also manage their profile - add their bio, experience,
> campaign priorities, and endorsements. Everything voters need to make
> an informed decision."

**[Dashboard Stats]**
> "Back on the dashboard, we track engagement - answer rate, views,
> and recent activity. This helps candidates see what's resonating
> with voters and stay on top of new questions."

---

## ✅ Pre-Demo Checklist

- [ ] Demo account created successfully
- [ ] Backend running (port 8000)
- [ ] Frontend running (port 3000)
- [ ] Can access dashboard
- [ ] Camera permissions granted
- [ ] Sample questions visible
- [ ] Profile page loads
- [ ] Video recorder starts
- [ ] Mobile view tested (if showing)
- [ ] Browser tab ready to share screen

---

## 🎓 Learning Resources

- [MediaRecorder API Docs](https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Router v6](https://reactrouter.com/)
- [Tailwind CSS](https://tailwindcss.com/)

---

**Quick Start**: `./setup-candidate-demo.sh` → Login → Dashboard → Answer Questions → Demo Complete!

**Need Help?** Check the full docs in `CANDIDATE_PORTAL_README.md`
