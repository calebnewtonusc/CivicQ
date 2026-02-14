# CivicQ API Documentation

**Version:** v1.0
**Base URL:** `https://api.civicq.org/v1` (production) | `http://localhost:8000/v1` (development)
**Last Updated:** 2026-02-14

---

## Overview

The CivicQ API is a RESTful API built with FastAPI that provides programmatic access to all platform functionality. This document covers authentication, endpoints, request/response formats, and error handling.

### API Design Principles

- **RESTful conventions** with clear resource-based URLs
- **JSON** for all request and response bodies
- **Pagination** for all list endpoints
- **Versioning** via URL path (`/v1`, `/v2`, etc.)
- **Consistent error responses** with helpful messages
- **OpenAPI/Swagger** documentation at `/docs`

### Authentication

All authenticated endpoints require a JWT token in the `Authorization` header:

```
Authorization: Bearer <jwt_token>
```

Tokens are obtained via the `/auth/login` endpoint and are valid for 15 minutes (access token) or 7 days (refresh token).

---

## Table of Contents

1. [Authentication](#authentication-endpoints)
2. [Ballots & Contests](#ballots--contests)
3. [Questions](#questions)
4. [Answers](#answers)
5. [Voting & Ranking](#voting--ranking)
6. [Candidates](#candidates)
7. [Users & Verification](#users--verification)
8. [Admin & Moderation](#admin--moderation)
9. [Analytics](#analytics)
10. [Common Patterns](#common-patterns)

---

## Authentication Endpoints

### Register User

Create a new voter account.

```http
POST /auth/register
```

**Request Body:**
```json
{
  "email": "voter@example.com",
  "password": "SecurePassword123!",
  "address": {
    "street": "123 Main St",
    "city": "San Marino",
    "state": "CA",
    "zip": "91108"
  }
}
```

**Response:** `201 Created`
```json
{
  "user_id": "uuid",
  "email": "voter@example.com",
  "verification_required": true,
  "verification_methods": ["email", "sms"]
}
```

**Errors:**
- `400 Bad Request`: Invalid email or password
- `409 Conflict`: Email already registered

---

### Login

Authenticate and receive JWT tokens.

```http
POST /auth/login
```

**Request Body:**
```json
{
  "email": "voter@example.com",
  "password": "SecurePassword123!"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "uuid",
    "email": "voter@example.com",
    "verified": false,
    "roles": ["voter"]
  }
}
```

**Errors:**
- `401 Unauthorized`: Invalid credentials
- `429 Too Many Requests`: Rate limit exceeded (5 attempts/minute)

---

### Refresh Token

Exchange refresh token for new access token.

```http
POST /auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 900
}
```

---

### Logout

Invalidate current tokens.

```http
POST /auth/logout
```

**Headers:** `Authorization: Bearer <access_token>`

**Response:** `204 No Content`

---

## Ballots & Contests

### Get User Ballot

Retrieve personalized ballot based on user's address.

```http
GET /ballots/mine
```

**Headers:** `Authorization: Bearer <access_token>`

**Query Parameters:**
- `election_date` (optional): Filter by specific election date

**Response:** `200 OK`
```json
{
  "ballot_id": "uuid",
  "city": {
    "id": "uuid",
    "name": "San Marino",
    "state": "CA",
    "election_date": "2026-11-03"
  },
  "contests": [
    {
      "id": "uuid",
      "type": "race",
      "title": "Mayor",
      "description": "Elect one mayor for a 4-year term",
      "district": null,
      "candidates_count": 3,
      "questions_answered": 7,
      "top_questions_count": 10
    },
    {
      "id": "uuid",
      "type": "ballot_measure",
      "title": "Measure A - Public Transit Funding",
      "description": "Increase sales tax by 0.5% to fund transit expansion",
      "fiscal_impact": "$5M annually",
      "proponents_count": 2,
      "opponents_count": 1
    }
  ],
  "address_verified": true
}
```

---

### Get Contest Details

Retrieve detailed information about a specific contest.

```http
GET /contests/{contest_id}
```

**Path Parameters:**
- `contest_id`: UUID of the contest

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "type": "race",
  "title": "Mayor",
  "description": "Elect one mayor for a 4-year term",
  "election_date": "2026-11-03",
  "filing_deadline": "2026-08-15T23:59:59Z",
  "candidates": [
    {
      "id": "uuid",
      "name": "Jane Smith",
      "party": "Independent",
      "website": "https://janeformayor.com",
      "bio": "City council member for 6 years...",
      "photo_url": "https://cdn.civicq.org/candidates/jane-smith.jpg",
      "verified": true,
      "questions_answered": 7,
      "top_10_answered": 5
    }
  ],
  "top_questions": [
    {
      "id": "uuid",
      "question_text": "What is your plan for affordable housing?",
      "issue_tags": ["housing", "development"],
      "ranking": 1,
      "upvotes": 342,
      "candidates_answered": 2,
      "created_at": "2026-09-01T12:00:00Z"
    }
  ],
  "question_stats": {
    "total": 127,
    "answered": 45,
    "pending": 82
  }
}
```

---

## Questions

### List Questions

Get paginated list of questions for a contest.

```http
GET /contests/{contest_id}/questions
```

**Query Parameters:**
- `page` (default: 1): Page number
- `per_page` (default: 20, max: 100): Items per page
- `sort` (default: "ranking"): Sort by ranking, upvotes, or recent
- `issue_tag` (optional): Filter by issue tag
- `status` (default: "active"): Filter by status (active, pending, merged, rejected)

**Response:** `200 OK`
```json
{
  "questions": [
    {
      "id": "uuid",
      "contest_id": "uuid",
      "question_text": "What is your plan for affordable housing?",
      "context": "Housing costs have increased 40% in 5 years",
      "issue_tags": ["housing", "development"],
      "status": "active",
      "ranking": 1,
      "ranking_score": 87.5,
      "upvotes": 342,
      "downvotes": 18,
      "net_votes": 324,
      "viewpoint_cluster": 1,
      "candidates_answered": 2,
      "created_at": "2026-09-01T12:00:00Z",
      "created_by": "anonymous"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 127,
    "total_pages": 7,
    "has_next": true,
    "has_prev": false
  }
}
```

---

### Get Question Details

Retrieve full details for a specific question.

```http
GET /questions/{question_id}
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "contest_id": "uuid",
  "contest_title": "Mayor",
  "question_text": "What is your plan for affordable housing?",
  "context": "Housing costs have increased 40% in 5 years",
  "issue_tags": ["housing", "development"],
  "status": "active",
  "version": 1,
  "parent_id": null,
  "ranking": 1,
  "ranking_score": 87.5,
  "upvotes": 342,
  "downvotes": 18,
  "viewpoint_cluster": 1,
  "answers": [
    {
      "id": "uuid",
      "candidate": {
        "id": "uuid",
        "name": "Jane Smith",
        "photo_url": "https://cdn.civicq.org/candidates/jane-smith.jpg"
      },
      "video_url": "https://cdn.civicq.org/videos/answer-uuid.m3u8",
      "thumbnail_url": "https://cdn.civicq.org/thumbnails/answer-uuid.jpg",
      "duration_seconds": 145,
      "transcript": "My plan for affordable housing includes...",
      "sources": [
        {
          "claim": "50% of residents are cost-burdened",
          "url": "https://census.gov/data/housing",
          "description": "US Census Bureau Housing Data"
        }
      ],
      "view_count": 1234,
      "published_at": "2026-09-05T14:30:00Z"
    }
  ],
  "user_vote": "up",
  "created_at": "2026-09-01T12:00:00Z"
}
```

---

### Submit Question

Submit a new question (requires verified user).

```http
POST /contests/{contest_id}/questions
```

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "question_text": "What is your plan for improving public transit?",
  "context": "Many residents lack access to reliable transit options",
  "issue_tags": ["transportation", "infrastructure"]
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "question_text": "What is your plan for improving public transit?",
  "status": "pending",
  "message": "Question submitted for review. Similar questions found.",
  "similar_questions": [
    {
      "id": "uuid",
      "question_text": "How will you expand public transportation?",
      "similarity_score": 0.87
    }
  ]
}
```

**Errors:**
- `401 Unauthorized`: User not authenticated
- `403 Forbidden`: User not verified
- `429 Too Many Requests`: Rate limit exceeded (5 questions/day)
- `400 Bad Request`: Invalid question format

---

### Vote on Question

Upvote or downvote a question (requires verified user).

```http
POST /questions/{question_id}/vote
```

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "vote": "up"
}
```

**Values:** `"up"` or `"down"`

**Response:** `200 OK`
```json
{
  "question_id": "uuid",
  "vote": "up",
  "upvotes": 343,
  "downvotes": 18,
  "net_votes": 325
}
```

**Errors:**
- `401 Unauthorized`: User not authenticated
- `403 Forbidden`: User not verified
- `409 Conflict`: User already voted (use PUT to change vote)

---

### Change Vote

Change existing vote on a question.

```http
PUT /questions/{question_id}/vote
```

**Request Body:**
```json
{
  "vote": "down"
}
```

**Response:** `200 OK`

---

### Remove Vote

Remove vote from a question.

```http
DELETE /questions/{question_id}/vote
```

**Response:** `204 No Content`

---

## Answers

### Get Answer Details

Retrieve full details for a candidate's answer.

```http
GET /answers/{answer_id}
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "question": {
    "id": "uuid",
    "question_text": "What is your plan for affordable housing?",
    "contest_title": "Mayor"
  },
  "candidate": {
    "id": "uuid",
    "name": "Jane Smith",
    "party": "Independent",
    "photo_url": "https://cdn.civicq.org/candidates/jane-smith.jpg"
  },
  "video_url": "https://cdn.civicq.org/videos/answer-uuid.m3u8",
  "video_formats": {
    "hls": "https://cdn.civicq.org/videos/answer-uuid.m3u8",
    "mp4_1080p": "https://cdn.civicq.org/videos/answer-uuid-1080p.mp4",
    "mp4_720p": "https://cdn.civicq.org/videos/answer-uuid-720p.mp4",
    "mp4_480p": "https://cdn.civicq.org/videos/answer-uuid-480p.mp4"
  },
  "thumbnail_url": "https://cdn.civicq.org/thumbnails/answer-uuid.jpg",
  "duration_seconds": 145,
  "transcript": "My plan for affordable housing includes three key components...",
  "caption_url": "https://cdn.civicq.org/captions/answer-uuid.vtt",
  "sources": [
    {
      "claim": "50% of residents are cost-burdened",
      "url": "https://census.gov/data/housing",
      "description": "US Census Bureau Housing Data"
    }
  ],
  "provenance": {
    "video_hash": "sha256:abcdef123456...",
    "recorded_at": "2026-09-05T14:15:00Z",
    "verified": true
  },
  "analytics": {
    "view_count": 1234,
    "completion_rate": 0.78,
    "avg_watch_time": 113
  },
  "published_at": "2026-09-05T14:30:00Z"
}
```

---

### Record Answer (Candidate Only)

Upload a video answer to a question.

```http
POST /questions/{question_id}/answers
```

**Headers:** `Authorization: Bearer <candidate_jwt>`

**Request Body (multipart/form-data):**
- `video`: Video file (required, max 100MB, mp4/webm)
- `transcript_draft`: Initial transcript (optional)
- `sources`: JSON array of source citations (optional)

**Response:** `202 Accepted`
```json
{
  "answer_id": "uuid",
  "status": "processing",
  "message": "Video uploaded successfully. Processing will take 2-5 minutes.",
  "estimated_completion": "2026-09-05T14:20:00Z"
}
```

**Errors:**
- `401 Unauthorized`: Not authenticated as candidate
- `403 Forbidden`: Candidate not verified or already answered this question
- `413 Payload Too Large`: Video exceeds size limit
- `415 Unsupported Media Type`: Invalid video format

---

### Update Answer Transcript (Candidate Only)

Correct transcript errors (does not modify video).

```http
PATCH /answers/{answer_id}/transcript
```

**Headers:** `Authorization: Bearer <candidate_jwt>`

**Request Body:**
```json
{
  "transcript_corrected": "My plan for affordable housing includes three key components..."
}
```

**Response:** `200 OK`

**Note:** Original auto-generated transcript is preserved. Corrections are stored separately and displayed with a note.

---

## Candidates

### Get Candidate Profile

Retrieve public candidate profile.

```http
GET /candidates/{candidate_id}
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "name": "Jane Smith",
  "party": "Independent",
  "website": "https://janeformayor.com",
  "bio": "City council member for 6 years, focused on housing and transit...",
  "photo_url": "https://cdn.civicq.org/candidates/jane-smith.jpg",
  "verified": true,
  "contests": [
    {
      "id": "uuid",
      "title": "Mayor",
      "election_date": "2026-11-03"
    }
  ],
  "stats": {
    "questions_answered": 12,
    "top_10_answered": 8,
    "total_views": 5678,
    "avg_completion_rate": 0.82
  },
  "recent_answers": [
    {
      "id": "uuid",
      "question_text": "What is your plan for affordable housing?",
      "thumbnail_url": "https://cdn.civicq.org/thumbnails/answer-uuid.jpg",
      "published_at": "2026-09-05T14:30:00Z"
    }
  ]
}
```

---

### Verify Candidate (Candidate Only)

Submit identity verification for candidate account.

```http
POST /candidates/verify
```

**Headers:** `Authorization: Bearer <candidate_jwt>`

**Request Body:**
```json
{
  "contest_id": "uuid",
  "filing_id": "C-2026-12345",
  "verification_documents": [
    {
      "type": "filing_receipt",
      "url": "https://upload.civicq.org/temp/filing-receipt.pdf"
    },
    {
      "type": "photo_id",
      "url": "https://upload.civicq.org/temp/drivers-license.jpg"
    }
  ]
}
```

**Response:** `202 Accepted`
```json
{
  "verification_id": "uuid",
  "status": "pending_review",
  "message": "Verification submitted. Review typically takes 1-2 business days.",
  "contact_email": "verification@civicq.org"
}
```

---

## Users & Verification

### Get Current User

Retrieve current authenticated user profile.

```http
GET /users/me
```

**Headers:** `Authorization: Bearer <access_token>`

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "email": "voter@example.com",
  "address": {
    "street": "123 Main St",
    "city": "San Marino",
    "state": "CA",
    "zip": "91108"
  },
  "verified": true,
  "verification_method": "email",
  "verification_date": "2026-09-01T10:00:00Z",
  "roles": ["voter"],
  "stats": {
    "questions_submitted": 3,
    "votes_cast": 47,
    "videos_watched": 23
  },
  "created_at": "2026-08-28T14:00:00Z"
}
```

---

### Start Verification

Initiate identity verification process.

```http
POST /users/verify/start
```

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "method": "email",
  "city_id": "uuid"
}
```

**Methods:** `email`, `sms`, `id_me` (city-configurable)

**Response:** `200 OK`
```json
{
  "verification_id": "uuid",
  "method": "email",
  "message": "Verification code sent to voter@example.com",
  "expires_at": "2026-09-01T10:15:00Z"
}
```

---

### Complete Verification

Complete verification with code or callback.

```http
POST /users/verify/complete
```

**Request Body:**
```json
{
  "verification_id": "uuid",
  "code": "123456"
}
```

**Response:** `200 OK`
```json
{
  "verified": true,
  "verification_method": "email",
  "city": {
    "id": "uuid",
    "name": "San Marino"
  },
  "message": "Verification successful. You can now submit and vote on questions."
}
```

---

## Admin & Moderation

### Get Moderation Queue (Admin Only)

Retrieve items pending moderation.

```http
GET /admin/moderation/queue
```

**Headers:** `Authorization: Bearer <admin_jwt>`

**Query Parameters:**
- `type` (optional): Filter by type (question, answer, user_report)
- `status` (default: pending): pending, reviewed, approved, rejected
- `page`, `per_page`: Pagination

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": "uuid",
      "type": "question",
      "status": "pending",
      "content": {
        "question_text": "Why are you a corrupt politician?",
        "contest_title": "Mayor"
      },
      "flags": ["potential_harassment", "low_quality"],
      "flagged_by": "auto_moderation",
      "created_at": "2026-09-10T09:00:00Z"
    }
  ],
  "pagination": { ... }
}
```

---

### Moderate Item (Admin Only)

Approve or reject a moderation item.

```http
POST /admin/moderation/{item_id}/action
```

**Request Body:**
```json
{
  "action": "approve",
  "reason": "Question is substantive, not harassment",
  "notes": "Edited for clarity"
}
```

**Actions:** `approve`, `reject`, `merge` (questions only), `edit`

**Response:** `200 OK`

---

## Analytics

### Get Contest Analytics (Admin Only)

Retrieve engagement analytics for a contest.

```http
GET /admin/analytics/contests/{contest_id}
```

**Query Parameters:**
- `start_date`, `end_date`: Date range

**Response:** `200 OK`
```json
{
  "contest": {
    "id": "uuid",
    "title": "Mayor"
  },
  "metrics": {
    "questions": {
      "total": 127,
      "active": 115,
      "answered": 45,
      "top_10_coverage": 0.8
    },
    "engagement": {
      "unique_voters": 3421,
      "total_votes": 12456,
      "questions_submitted": 127,
      "videos_watched": 8765,
      "avg_watch_time": 98
    },
    "candidates": {
      "total": 3,
      "verified": 3,
      "active": 3,
      "avg_answers": 15,
      "top_10_answered": [2, 1, 0]
    },
    "timeline": [
      {
        "date": "2026-09-01",
        "votes": 234,
        "questions": 12,
        "videos_watched": 456
      }
    ]
  }
}
```

---

## Common Patterns

### Pagination

All list endpoints support pagination with consistent parameters:

**Query Parameters:**
- `page` (default: 1): Page number
- `per_page` (default: 20, max: 100): Items per page

**Response Format:**
```json
{
  "items": [...],
  "pagination": {
    "page": 2,
    "per_page": 20,
    "total": 127,
    "total_pages": 7,
    "has_next": true,
    "has_prev": true,
    "next_page": 3,
    "prev_page": 1
  }
}
```

---

### Error Responses

All errors follow a consistent format:

**Response:** `4xx` or `5xx`
```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Email or password is incorrect",
    "details": {
      "field": "password",
      "constraint": "authentication_failed"
    },
    "request_id": "uuid",
    "timestamp": "2026-09-01T12:00:00Z"
  }
}
```

**Common Error Codes:**
- `INVALID_CREDENTIALS`: Login failed
- `UNAUTHORIZED`: Missing or invalid JWT
- `FORBIDDEN`: User lacks required permissions
- `NOT_FOUND`: Resource not found
- `VALIDATION_ERROR`: Request body validation failed
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `CONFLICT`: Resource conflict (e.g., already voted)
- `INTERNAL_ERROR`: Server error

---

### Rate Limiting

Rate limits are applied per IP address or authenticated user:

**Limits:**
- Anonymous: 100 requests/hour
- Authenticated: 1000 requests/hour
- Question submission: 5/day (verified users)
- Question voting: 100/hour (verified users)
- Video upload: 10/day (candidates)

**Response Headers:**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1693497600
```

**Error Response:** `429 Too Many Requests`
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Try again in 15 minutes.",
    "retry_after": 900
  }
}
```

---

### Filtering and Sorting

Many list endpoints support filtering and sorting:

**Query Parameters:**
- `sort`: Field to sort by (e.g., `ranking`, `created_at`, `upvotes`)
- `order`: Sort order (`asc` or `desc`, default: `desc`)
- `filter[field]`: Filter by field value

**Example:**
```
GET /contests/uuid/questions?sort=upvotes&order=desc&filter[issue_tag]=housing
```

---

## OpenAPI Documentation

Interactive API documentation is available at:
- **Swagger UI:** `http://localhost:8000/docs` (development)
- **ReDoc:** `http://localhost:8000/redoc` (development)
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`

Production URLs will be updated when deployed.

---

## Webhooks (Planned)

Future versions will support webhooks for real-time notifications:

**Event Types:**
- `question.created`
- `question.answered`
- `answer.published`
- `moderation.required`
- `verification.completed`

---

## SDK and Client Libraries (Planned)

Official SDKs will be provided for:
- JavaScript/TypeScript (npm package)
- Python (PyPI package)
- Ruby (RubyGems)

---

**For implementation details, see:**
- [Architecture Documentation](ARCHITECTURE.md)
- [Database Schema](architecture/database-schema.md)
- [Authentication Guide](authentication.md) (TBD)

---

**Last Updated:** 2026-02-14
**Questions or issues?** Open a GitHub issue or contact the development team.
