# CivicQ API Endpoints Quick Reference

Base URL: `http://localhost:8000`

## Authentication Endpoints

### User Registration & Login
```
POST   /api/auth/signup              Create new user account
POST   /api/auth/login               Authenticate user
GET    /api/auth/me                  Get current user profile
```

### Verification
```
POST   /api/auth/verify/start        Start identity verification
POST   /api/auth/verify/complete     Complete verification with code
```

## Ballot Discovery

### Cities & Elections
```
GET    /api/cities                   List all cities with elections
GET    /api/elections?city={city}    Get elections for a city
```

### Ballots
```
GET    /api/ballot?city={city}&election_date={date}&address={addr}
                                     Get personalized ballot
GET    /api/ballot/{ballot_id}      Get ballot by ID
```

## Contests

```
GET    /api/contests/?ballot_id={id}           List contests for ballot
GET    /api/contests/{contest_id}              Get contest details
GET    /api/contests/{contest_id}/candidates   Get candidates in contest
```

## Questions

### Question Management
```
POST   /api/contest/{contest_id}/questions     Submit new question
GET    /api/contest/{contest_id}/questions     List questions
       ?sort={top|new|controversial}
       &issue={tag}
       &page={num}
       &page_size={size}

GET    /api/questions/{question_id}            Get question details
POST   /api/questions/{question_id}/edit       Edit question (creates version)
DELETE /api/questions/{question_id}            Delete question (soft)
```

### Question Versions
```
GET    /api/questions/{question_id}/versions   Get version history
```

### Voting
```
POST   /api/questions/{question_id}/vote       Vote on question
       Body: {"value": 1}   # +1 upvote, -1 downvote, 0 remove
```

## Candidates

### Profile & Answers
```
GET    /api/candidates/{candidate_id}          Get candidate profile
GET    /api/candidates/{candidate_id}/answers  List candidate's answers
POST   /api/candidates/{candidate_id}/answers  Submit video answer
```

### Rebuttals
```
GET    /api/candidates/{candidate_id}/rebuttals    List rebuttals
POST   /api/candidates/{candidate_id}/rebuttals    Submit rebuttal
```

## Request Examples

### Signup
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "voter@example.com",
    "password": "securepass123",
    "full_name": "Jane Voter",
    "city": "San Francisco"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "voter@example.com",
    "password": "securepass123"
  }'
```

### Submit Question
```bash
curl -X POST http://localhost:8000/api/contest/1/questions \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "contest_id": 1,
    "question_text": "What is your plan to address homelessness?",
    "context": "I work with local nonprofits",
    "issue_tags": ["housing", "social-services"]
  }'
```

### Vote on Question
```bash
curl -X POST http://localhost:8000/api/questions/1/vote \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"value": 1}'
```

### Get Questions (with filters)
```bash
curl "http://localhost:8000/api/contest/1/questions?sort=top&issue=housing&page=1&page_size=20"
```

### Submit Video Answer (Candidate)
```bash
curl -X POST http://localhost:8000/api/candidates/1/answers \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "question_id": 1,
    "video_url": "https://cdn.example.com/video123.mp4",
    "duration": 90,
    "transcript": "My plan for addressing homelessness...",
    "sources": [
      {
        "url": "https://sf.gov/housing-report",
        "title": "SF Housing Report 2024"
      }
    ]
  }'
```

### Submit Rebuttal
```bash
curl -X POST http://localhost:8000/api/candidates/2/rebuttals \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "answer_id": 1,
    "claim_reference": "I disagree with the budget allocation mentioned",
    "video_url": "https://cdn.example.com/rebuttal456.mp4",
    "duration": 60,
    "transcript": "The actual budget numbers are..."
  }'
```

## Authentication

Most write endpoints require authentication. Include the JWT token in the Authorization header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Permissions

- **Public (no auth required)**:
  - All GET endpoints for reading ballots, contests, questions, candidates
  
- **Authenticated users**:
  - Submit questions
  - Edit questions
  
- **Verified users only**:
  - Vote on questions
  
- **Candidates only**:
  - Submit video answers
  - Submit rebuttals

## Response Formats

### Success Response
```json
{
  "id": 1,
  "question_text": "What is your plan?",
  "status": "approved",
  "upvotes": 42,
  "downvotes": 3
}
```

### Error Response
```json
{
  "detail": "Question not found"
}
```

### Token Response
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "voter@example.com",
    "full_name": "Jane Voter",
    "role": "voter",
    "verification_status": "verified"
  }
}
```

## Status Codes

- `200 OK` - Successful GET request
- `201 Created` - Successful POST (resource created)
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Validation error or invalid input
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Authenticated but lacking permissions
- `404 Not Found` - Resource doesn't exist
- `500 Internal Server Error` - Server error

## Interactive Documentation

When running in development mode:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

These provide interactive API exploration and testing.
