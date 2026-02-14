# City Onboarding System

## Overview

The CivicQ City Onboarding System allows ANY city in America to sign up, get verified, and launch their own CivicQ portal in under 30 minutes. This document explains the complete onboarding flow, architecture, and API endpoints.

## Features

- **5-Minute Registration** - Simple form for city officials to register
- **Official Verification** - Email domain + documentation verification
- **Setup Wizard** - Guided 5-step setup process
- **Ballot Import** - Manual entry or API import from election systems
- **Customization** - Logo, colors, and branding
- **Team Management** - Invite city staff with role-based access
- **Multi-City Architecture** - Supports thousands of cities on one platform

## Architecture

### Multi-Tenancy Model

CivicQ uses a **shared database, partitioned by city** model:

- All data is scoped by `city_id`
- Each city has isolated data (ballots, questions, voters)
- Shared infrastructure scales efficiently
- City-specific branding and customization

### Key Models

#### City
```python
class City(Base):
    id: int
    name: str
    slug: str  # URL-friendly: "springfield-il"
    state: str
    status: CityStatus  # pending_verification, active, suspended, inactive

    # Contact
    primary_contact_name: str
    primary_contact_email: str

    # Verification
    verification_method: str
    verified_at: datetime
    official_email_domain: str
    documentation_urls: list

    # Branding
    logo_url: str
    primary_color: str
    secondary_color: str

    # Onboarding
    onboarding_completed: bool
    onboarding_step: int
```

#### CityStaff
```python
class CityStaff(Base):
    city_id: int
    user_id: int
    role: CityStaffRole  # owner, admin, editor, moderator, viewer
    is_active: bool
```

#### CityInvitation
```python
class CityInvitation(Base):
    city_id: int
    email: str
    role: CityStaffRole
    token: str
    expires_at: datetime
```

## Onboarding Flow

### Step 1: Registration

**URL:** `/city/register`

City officials fill out a registration form with:

1. **City Information**
   - City name
   - State (2-letter code)
   - County (optional)
   - Population (optional)

2. **Primary Contact** (usually City Clerk)
   - Full name
   - Email
   - Phone
   - Title

3. **Verification**
   - Official email domain (e.g., "cityofboston.gov")
   - Documentation URLs (links to official city website, roster)

4. **Account Security**
   - Password (min 8 chars, uppercase, lowercase, number)

**What Happens:**
- Creates `City` record with status `pending_verification`
- Creates `User` account for primary contact with role `city_staff`
- Links user as city owner via `CityStaff`
- Email sent to admin team for verification

### Step 2: Verification (Admin Only)

**URL:** `/api/cities/{city_id}/verify` (superuser only)

Admin team verifies:
- Email domain matches official city domain
- Documentation confirms identity
- Contact is legitimate city official

**Verification Methods:**
- `email_domain` - Official .gov or .us email
- `documentation` - Official city website listing
- `phone_verification` - Call to verify
- `manual_review` - Full manual review

Once verified:
- City status → `active`
- City contact receives email
- Onboarding step → 2 (Ballot Import)

### Step 3: Ballot Import

**URL:** `/city/{city_id}/setup` → Step 2

City staff can import ballot data via:

#### Manual Entry
**URL:** `/city/{city_id}/import/manual`

- Add contests one by one
- Enter candidate information
- Add ballot measures
- Simple form-based interface

#### API Import
**URL:** `/city/{city_id}/import/api`

Supported formats:
- **VotingWorks** - JSON format
- **Democracy Works** - TurboVote API
- **Custom API** - Generic JSON schema

**Endpoint:** `POST /api/cities/{city_id}/import-ballot`

```json
{
  "election_date": "2026-11-03",
  "contests": [
    {
      "title": "Mayor",
      "type": "race",
      "office": "Mayor",
      "jurisdiction": "Citywide",
      "seat_count": 1,
      "candidates": [
        {
          "name": "Jane Smith",
          "email": "jane@example.com",
          "phone": "555-1234",
          "website": "https://janeformayor.com"
        }
      ]
    }
  ]
}
```

### Step 4: Customize Branding

**URL:** `/city/{city_id}/setup` → Step 3

City staff can customize:
- **Logo** - Upload city logo (via URL)
- **Primary Color** - Main brand color (hex code)
- **Secondary Color** - Accent color (hex code)

**Endpoint:** `PUT /api/cities/{city_id}/branding`

```json
{
  "logo_url": "https://cdn.example.com/city-logo.png",
  "primary_color": "#003366",
  "secondary_color": "#0066CC"
}
```

### Step 5: Invite Staff

**URL:** `/city/{city_id}/setup` → Step 4

Invite colleagues to help manage:

**Roles:**
- **Owner** - Full control (City Clerk)
- **Admin** - Full administrative access
- **Editor** - Can edit ballots and content
- **Moderator** - Can moderate questions
- **Viewer** - Read-only access

**Endpoint:** `POST /api/cities/{city_id}/staff/invite`

```json
{
  "email": "colleague@cityofspringfield.gov",
  "role": "editor"
}
```

**Invitation Flow:**
1. City staff sends invitation
2. Email sent with unique token
3. Recipient clicks link → accepts invite
4. If no account, creates one
5. Added to city staff

### Step 6: Review & Launch

**URL:** `/city/{city_id}/setup` → Step 5

Final review and launch:
- Confirm ballot data
- Verify branding
- Review team
- Launch city portal

**Endpoint:** `POST /api/cities/{city_id}/complete-onboarding`

City is now live!

## City Dashboard

**URL:** `/city/{city_id}/dashboard`

Real-time statistics:
- Total voters registered
- Questions submitted
- Candidates participating
- Engagement metrics

**Quick Actions:**
- Manage ballots
- Moderate questions
- Invite staff
- Customize branding
- View analytics
- Export data

## API Endpoints

### Public Endpoints

#### List Cities
```
GET /api/cities/list?state=CA&status=active
```

Returns all active cities (for public directory).

### Authentication Required

#### Register City
```
POST /api/cities/register
```

Create new city registration (pending verification).

#### Get City Details
```
GET /api/cities/{city_id}
```

Get city information (requires staff access).

#### Update Branding
```
PUT /api/cities/{city_id}/branding
```

Update logo and colors (requires admin role).

#### Update Election Info
```
PUT /api/cities/{city_id}/election
```

Update election date and info URL (requires admin role).

#### Update Settings
```
PUT /api/cities/{city_id}/settings
```

Update timezone and settings (requires admin role).

#### Complete Onboarding
```
POST /api/cities/{city_id}/complete-onboarding
```

Mark onboarding as complete (requires admin role).

#### Invite Staff
```
POST /api/cities/{city_id}/staff/invite
```

Invite user to join city staff (requires admin role).

#### Accept Invitation
```
POST /api/cities/accept-invite
Body: { "token": "...", "password": "..." }
```

Accept staff invitation (public, token-authenticated).

#### List Staff
```
GET /api/cities/{city_id}/staff
```

List all city staff members (requires viewer role).

#### Dashboard Stats
```
GET /api/cities/{city_id}/dashboard
```

Get dashboard statistics (requires viewer role).

#### Import Ballot
```
POST /api/cities/{city_id}/import-ballot
```

Import ballot data (requires editor role).

### Admin Only

#### Verify City
```
POST /api/cities/{city_id}/verify
Body: {
  "city_id": 1,
  "verification_method": "email_domain",
  "verification_notes": "Verified via official .gov email",
  "approved": true
}
```

Verify or reject city registration (superuser only).

## Role-Based Access Control

### Role Hierarchy

```
Owner > Admin > Editor > Moderator > Viewer
```

### Permissions Matrix

| Action | Owner | Admin | Editor | Moderator | Viewer |
|--------|-------|-------|--------|-----------|--------|
| View Dashboard | ✅ | ✅ | ✅ | ✅ | ✅ |
| Import Ballots | ✅ | ✅ | ✅ | ❌ | ❌ |
| Edit Ballots | ✅ | ✅ | ✅ | ❌ | ❌ |
| Moderate Questions | ✅ | ✅ | ✅ | ✅ | ❌ |
| Update Branding | ✅ | ✅ | ❌ | ❌ | ❌ |
| Invite Staff | ✅ | ✅ | ❌ | ❌ | ❌ |
| Manage Staff | ✅ | ✅ | ❌ | ❌ | ❌ |
| Delete City | ✅ | ❌ | ❌ | ❌ | ❌ |

## Database Schema

### Migration File

Location: `backend/database/migrations/versions/city_onboarding_migration.py`

Creates:
- `cities` table
- `city_staff` table
- `city_invitations` table
- `citystatus` enum
- `citystaffrole` enum

## Frontend Components

### Pages

1. **CityRegistrationPage** (`/city/register`)
   - Registration form
   - US states dropdown
   - Password validation
   - Documentation URLs

2. **CitySetupWizardPage** (`/city/{cityId}/setup`)
   - 5-step wizard
   - Progress indicator
   - Step-by-step guidance

3. **CityDashboardPage** (`/city/{cityId}/dashboard`)
   - Real-time stats
   - Quick actions
   - Recent activity

4. **CityBallotImportPage** (`/city/{cityId}/import/manual`)
   - Contest builder
   - Candidate entry
   - Measure entry

## Scaling to 1000s of Cities

### Database Optimization

- **Indexes** on `city_id` for all scoped tables
- **Partitioning** by `city_id` for large tables
- **Caching** city settings and branding

### Performance

- **CDN** for city logos and static assets
- **Redis** for city configuration caching
- **Database connection pooling** per city

### Cost Optimization

- **Shared infrastructure** - All cities on same servers
- **Resource-based pricing** - Cities pay for usage
- **Tiered plans** - Free, Pro, Enterprise

## Security

### Verification Process

1. **Email Domain Check** - Verify official .gov/.us email
2. **Documentation Review** - Check official city website
3. **Manual Review** - Admin team verification
4. **Phone Verification** - Optional call to verify

### Access Control

- **Role-based permissions** - Granular access control
- **City data isolation** - Each city sees only their data
- **Audit logging** - Track all city staff actions
- **Token-based invitations** - Secure staff invitations

## Testing

### Test City Registration

```bash
curl -X POST http://localhost:8000/api/cities/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Springfield",
    "state": "IL",
    "primary_contact_name": "Jane Smith",
    "primary_contact_email": "jane@cityofspringfield.gov",
    "primary_contact_title": "City Clerk",
    "official_email_domain": "cityofspringfield.gov",
    "password": "SecurePass123"
  }'
```

### Test Ballot Import

```bash
curl -X POST http://localhost:8000/api/cities/1/import-ballot \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "election_date": "2026-11-03",
    "contests": [
      {
        "title": "Mayor",
        "type": "race",
        "office": "Mayor",
        "candidates": [
          {"name": "John Doe", "email": "john@example.com"}
        ]
      }
    ]
  }'
```

## Deployment

### Database Migration

```bash
cd backend
alembic upgrade head
```

### Environment Variables

```bash
# Add to .env
FRONTEND_URL=https://civicq.org
ADMIN_EMAIL=admin@civicq.org
```

## Support

For city onboarding support:
- Email: cities@civicq.org
- Documentation: https://docs.civicq.org/cities
- Demo: Schedule at https://civicq.org/demo

## Roadmap

- [ ] Automated verification via .gov email
- [ ] VotingWorks API integration
- [ ] Bulk ballot import from CSV
- [ ] City analytics dashboard
- [ ] White-label options
- [ ] Multi-language support
- [ ] Mobile app for city staff
