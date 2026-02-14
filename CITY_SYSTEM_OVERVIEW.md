# City Onboarding System - Visual Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CIVICQ PLATFORM                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │              CITY ONBOARDING SYSTEM                     │    │
│  │                                                          │    │
│  │  Registration → Verification → Setup → Launch → Manage  │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │   CITY PORTAL    │  │   VOTER PORTAL   │  │  CANDIDATE   │ │
│  │                  │  │                  │  │   PORTAL     │ │
│  │  - Dashboard     │  │  - Questions     │  │  - Profile   │ │
│  │  - Ballots       │  │  - Voting        │  │  - Answers   │ │
│  │  - Analytics     │  │  - Candidates    │  │  - Analytics │ │
│  │  - Moderation    │  │  - Results       │  │  - Rebuttals │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Onboarding Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      CITY REGISTRATION FLOW                      │
└─────────────────────────────────────────────────────────────────┘

    City Official
         │
         ├──► Visit /city/register
         │
         ├──► Fill Registration Form
         │    ├─ City info (name, state, county)
         │    ├─ Contact info (name, email, phone)
         │    ├─ Verification (domain, docs)
         │    └─ Password
         │
         ├──► Submit Registration
         │    │
         │    ├──► Create City Record (status: pending)
         │    ├──► Create User Account (role: city_staff)
         │    ├──► Link as Owner (via CityStaff)
         │    └──► Email Admin Team
         │
         ├──► Redirected to /city/{id}/pending-verification
         │
         ├──► Wait for Admin Verification (24 hours)
         │
         ├──► Receive Email: "City Verified!"
         │
         ├──► Login & Redirected to /city/{id}/setup
         │
         └──► Complete Setup Wizard (5 steps)

┌─────────────────────────────────────────────────────────────────┐
│                       SETUP WIZARD (5 STEPS)                     │
└─────────────────────────────────────────────────────────────────┘

  Step 1: ⏳ Verification Pending
    │
    ├─ Status: Waiting for admin verification
    ├─ Shows: What to expect, timeline
    └─ Action: Wait for email notification

  Step 2: 🗳️ Import Ballot Data
    │
    ├─ Manual Entry:
    │   ├─ Add contests (races, measures)
    │   ├─ Add candidates
    │   └─ Add ballot measures
    │
    ├─ API Import:
    │   ├─ VotingWorks
    │   ├─ Democracy Works
    │   └─ Custom JSON
    │
    └─ Skip allowed

  Step 3: 🎨 Customize Branding
    │
    ├─ Logo URL
    ├─ Primary Color
    ├─ Secondary Color
    ├─ Live Preview
    └─ Skip allowed

  Step 4: 👥 Invite Staff
    │
    ├─ Add team members:
    │   ├─ Email
    │   ├─ Role (owner/admin/editor/moderator/viewer)
    │   └─ Send invitation
    │
    └─ Skip allowed

  Step 5: 🚀 Review & Launch
    │
    ├─ Review setup
    ├─ Confirm details
    └─ Click "Launch"
         │
         ├──► onboarding_completed = true
         ├──► status = active
         └──► Redirect to /city/{id}/dashboard

┌─────────────────────────────────────────────────────────────────┐
│                         CITY DASHBOARD                           │
└─────────────────────────────────────────────────────────────────┘

  Dashboard Home
    │
    ├─ Statistics:
    │   ├─ Total Voters
    │   ├─ Total Questions
    │   ├─ Total Candidates
    │   └─ Total Contests
    │
    ├─ Engagement Metrics:
    │   ├─ Avg Questions per Contest
    │   ├─ Avg Votes per Question
    │   ├─ Questions This Week
    │   └─ Voters This Week
    │
    ├─ Quick Actions:
    │   ├─ Manage Ballots
    │   ├─ Moderate Questions
    │   ├─ Invite Staff
    │   ├─ Customize Branding
    │   ├─ View Analytics
    │   └─ Export Data
    │
    └─ Recent Activity:
        ├─ New questions
        ├─ New voters
        └─ Candidate answers
```

## Database Schema Relationships

```
┌──────────────┐
│    Cities    │
│──────────────│
│ id           │───┐
│ name         │   │
│ slug         │   │ 1:N
│ state        │   │
│ status       │   │
└──────────────┘   │
                   │
         ┌─────────┴───────────┐
         │                     │
         ▼                     ▼
┌──────────────┐      ┌──────────────────┐
│  CityStaff   │      │ CityInvitations  │
│──────────────│      │──────────────────│
│ city_id      │◄─────│ city_id          │
│ user_id      │      │ email            │
│ role         │      │ token            │
│ is_active    │      │ role             │
└──────────────┘      │ expires_at       │
                      └──────────────────┘
         │
         │ N:1
         ▼
┌──────────────┐
│    Users     │
│──────────────│
│ id           │
│ email        │
│ role         │
│ city_id      │
└──────────────┘
         │
         │ 1:N
         ▼
┌──────────────┐      ┌──────────────┐
│   Ballots    │      │  Questions   │
│──────────────│      │──────────────│
│ city_id      │      │ contest_id   │
│ election_date│      │ author_id    │
└──────────────┘      └──────────────┘
         │
         │ 1:N
         ▼
┌──────────────┐
│   Contests   │
│──────────────│
│ ballot_id    │
│ type         │
│ title        │
└──────────────┘
         │
         │ 1:N
         ▼
┌──────────────┐
│  Candidates  │
│──────────────│
│ contest_id   │
│ user_id      │
│ name         │
└──────────────┘
```

## API Endpoint Map

```
PUBLIC ENDPOINTS
├─ POST   /api/cities/register           → Register new city
├─ GET    /api/cities/list               → List all cities
└─ POST   /api/cities/accept-invite      → Accept staff invitation

AUTHENTICATED ENDPOINTS (requires city staff access)
├─ GET    /api/cities/{id}               → Get city details
├─ PUT    /api/cities/{id}/branding      → Update branding
├─ PUT    /api/cities/{id}/election      → Update election info
├─ PUT    /api/cities/{id}/settings      → Update settings
├─ POST   /api/cities/{id}/complete-onboarding → Complete onboarding
├─ POST   /api/cities/{id}/staff/invite  → Invite staff member
├─ GET    /api/cities/{id}/staff         → List staff members
├─ GET    /api/cities/{id}/dashboard     → Get dashboard stats
└─ POST   /api/cities/{id}/import-ballot → Import ballot data

ADMIN ENDPOINTS (superuser only)
└─ POST   /api/cities/{id}/verify        → Verify/reject city
```

## Role Hierarchy & Permissions

```
┌────────────────────────────────────────────────────────────────┐
│                    ROLE HIERARCHY                               │
└────────────────────────────────────────────────────────────────┘

    OWNER (City Clerk)
      │
      ├─ Full control
      ├─ Can delete city
      └─ Can change ownership
         │
         ▼
    ADMIN (Deputy/Assistant)
      │
      ├─ Full admin access
      ├─ Cannot delete city
      └─ Cannot change ownership
         │
         ▼
    EDITOR (Elections Staff)
      │
      ├─ Import/edit ballots
      ├─ Manage contests/candidates
      └─ Cannot invite staff
         │
         ▼
    MODERATOR (Communications)
      │
      ├─ Moderate questions
      ├─ Review reports
      └─ Cannot edit ballots
         │
         ▼
    VIEWER (Read-only)
      │
      ├─ View dashboard
      ├─ View statistics
      └─ Cannot edit anything

┌────────────────────────────────────────────────────────────────┐
│                   PERMISSION MATRIX                             │
└────────────────────────────────────────────────────────────────┘

Action                  Owner  Admin  Editor  Moderator  Viewer
──────────────────────  ─────  ─────  ──────  ─────────  ──────
View Dashboard            ✓      ✓      ✓        ✓        ✓
Import Ballots            ✓      ✓      ✓        ✗        ✗
Edit Ballots              ✓      ✓      ✓        ✗        ✗
Moderate Questions        ✓      ✓      ✓        ✓        ✗
Update Branding           ✓      ✓      ✗        ✗        ✗
Invite Staff              ✓      ✓      ✗        ✗        ✗
Manage Staff              ✓      ✓      ✗        ✗        ✗
View Analytics            ✓      ✓      ✓        ✗        ✗
Export Data               ✓      ✓      ✓        ✗        ✗
Delete City               ✓      ✗      ✗        ✗        ✗
Change Ownership          ✓      ✗      ✗        ✗        ✗
```

## Multi-City Data Isolation

```
┌────────────────────────────────────────────────────────────────┐
│                    DATA ISOLATION MODEL                         │
└────────────────────────────────────────────────────────────────┘

    Shared Database
         │
         ├──► City 1 (Springfield, IL)
         │     ├─ city_id = 1
         │     ├─ Ballots (city_id=1)
         │     ├─ Questions (via contest.ballot.city_id=1)
         │     ├─ Voters (city_id="1")
         │     └─ Staff (city_id=1)
         │
         ├──► City 2 (Boston, MA)
         │     ├─ city_id = 2
         │     ├─ Ballots (city_id=2)
         │     ├─ Questions (via contest.ballot.city_id=2)
         │     ├─ Voters (city_id="2")
         │     └─ Staff (city_id=2)
         │
         └──► City 3 (Austin, TX)
               ├─ city_id = 3
               ├─ Ballots (city_id=3)
               ├─ Questions (via contest.ballot.city_id=3)
               ├─ Voters (city_id="3")
               └─ Staff (city_id=3)

All queries filtered by city_id → Complete data isolation
```

## Verification Process

```
┌────────────────────────────────────────────────────────────────┐
│                    VERIFICATION WORKFLOW                        │
└────────────────────────────────────────────────────────────────┘

City Registration
      │
      ├──► Status: pending_verification
      │
      ├──► Email sent to admin@civicq.org
      │
      ▼
Admin Reviews:
      │
      ├──► Check email domain (.gov or .us)
      ├──► Review documentation URLs
      ├──► Verify contact is city official
      └──► Optional: Phone call verification
           │
           ├──► APPROVED
           │     │
           │     ├─ Status → active
           │     ├─ verified_at → timestamp
           │     ├─ verified_by → admin email
           │     └─ Email city contact
           │
           └──► REJECTED
                 │
                 ├─ Status → suspended
                 └─ Email city contact with reason
```

## Frontend Page Flow

```
┌────────────────────────────────────────────────────────────────┐
│                       PAGE NAVIGATION                           │
└────────────────────────────────────────────────────────────────┘

/city/register
    │
    └──► [Submit] ──► /city/{id}/pending-verification
                           │
                           │ [Auto-redirect when verified]
                           │
                           ▼
                      /city/{id}/setup
                           │
                           ├─ Step 1: Pending
                           ├─ Step 2: Import → /city/{id}/import/manual
                           ├─ Step 3: Branding
                           ├─ Step 4: Invite
                           └─ Step 5: Launch
                                │
                                └──► /city/{id}/dashboard
                                      │
                                      ├─ Manage Ballots
                                      ├─ Moderate Questions
                                      ├─ View Analytics
                                      └─ City Settings
```

## Key Files Reference

```
BACKEND
├── models/
│   └── city.py                    # City, CityStaff, CityInvitation
├── schemas/
│   └── city.py                    # Request/response schemas
├── api/
│   └── cities.py                  # All city endpoints
└── database/migrations/versions/
    └── city_onboarding_migration.py  # Database schema

FRONTEND
├── pages/
│   ├── CityRegistrationPage.tsx       # Registration form
│   ├── CityPendingVerificationPage.tsx # Pending status
│   ├── CitySetupWizardPage.tsx        # 5-step wizard
│   ├── CityDashboardPage.tsx          # Admin dashboard
│   └── CityBallotImportPage.tsx       # Manual import
└── App.tsx                            # Route definitions

DOCUMENTATION
├── CITY_ONBOARDING.md              # Complete technical docs
├── CITY_QUICKSTART.md              # Quick start guide
├── CITY_IMPLEMENTATION_SUMMARY.md  # Implementation summary
└── CITY_SYSTEM_OVERVIEW.md         # This file
```

## Deployment Flow

```
1. Backend
   ├─ Run migration: alembic upgrade head
   ├─ Update main.py with cities router
   └─ Deploy API

2. Frontend
   ├─ Build: npm run build
   ├─ Deploy static files
   └─ Update API URL

3. Database
   ├─ cities table
   ├─ city_staff table
   └─ city_invitations table

4. Configuration
   ├─ Set FRONTEND_URL env var
   ├─ Configure email service (SMTP)
   └─ Set admin email for verification
```

## Success Flow Summary

```
City Official
    ↓
Register (5 min)
    ↓
Wait for Verification (24 hrs)
    ↓
Complete Setup Wizard (25 min)
    ├─ Import Ballot
    ├─ Customize Branding
    ├─ Invite Staff
    └─ Launch
        ↓
City Live on CivicQ!
    ├─ Voters Register
    ├─ Ask Questions
    ├─ Candidates Answer
    └─ Informed Democracy
```

---

**Total Time to Launch: Under 30 minutes** (after verification)
