# CivicQ

**Turning campaigning into a standardized, verifiable public record of candidates answering the public's top questions, city by city, with integrity by design.**

## What is CivicQ?

CivicQ is a city-level "candidate Q&A + ballot info" platform that makes campaigning look like **answering the public's top questions, on record, in one place**, instead of spending money to grab attention.

It starts with **city council, mayor, school board, and local ballot measures** because:
- The pain is high (voters have no idea what anyone stands for)
- The adoption path is realistic
- Local elections desperately need better voter information

## Core Features

### For Voters
- **Your Ballot as Home Screen**: See all your local races and measures in one place
- **Ask Questions**: Submit questions verified residents want answered
- **Rank Questions**: Vote on which questions matter most to your community
- **Watch Answers**: Short, structured video answers from candidates (no editing, no spin)
- **Compare Candidates**: Side-by-side answers on issues you care about
- **Follow Issues**: Track answers across races on topics like housing, education, safety

### For Candidates
- **Fair Exposure**: Equal visibility for all candidates, no pay-to-win
- **Structured Format**: Clear prompts that reduce "gotcha" risk
- **Rebuttal Rights**: Respond to specific claims with context
- **Built-in Legitimacy**: Verified platform reduces need for expensive campaigning

### For Cities
- **Reduced Voter Confusion**: One official source of candidate information
- **Increased Legitimacy**: Transparent, verifiable public record
- **Low Administration**: Automated moderation with oversight
- **Comprehensive Reporting**: Track engagement and coverage metrics

## Anti-Polarization by Design

Unlike social media platforms that reward outrage, CivicQ is built to prevent polarization:

- **No Comments**: No performative dunking or flame wars
- **No Engagement Algorithms**: Not a feed, it's a library
- **Portfolio Ranking**: Questions represent the whole community, not just loud factions
- **Structured Rebuttals**: Responses must cite specific claims, not enable attacks
- **Viewpoint Clustering**: Prevents one faction from dominating the top questions

## Technical Architecture

### Stack
- **Frontend**: React + TypeScript (mobile-responsive web)
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL with pgvector for semantic search
- **Media Pipeline**: Video transcoding, captioning, and provenance tracking
- **Infrastructure**: Docker, cloud-agnostic design

### Core Components
1. **Voter Web App**: Ballot viewing, question submission, video watching
2. **Candidate Portal**: Identity verification, video recording, answer management
3. **Admin Console**: City staff dashboard, moderation queue, reporting
4. **API Backend**: CRUD operations, ranking algorithms, verification flows
5. **Media Pipeline**: Secure video capture → transcoding → captioning → CDN
6. **Verification System**: Modular identity verification (city-configurable)

## Project Structure

```
CivicQ/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── api/      # API routes
│   │   ├── core/     # Config, security, auth
│   │   ├── models/   # Database models
│   │   ├── services/ # Business logic
│   │   └── utils/    # Helpers
│   └── tests/
├── frontend/         # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── utils/
│   │   └── types/
│   └── public/
├── database/         # Schema and migrations
│   ├── migrations/
│   └── schemas/
├── docs/             # Documentation
│   ├── architecture/
│   ├── api/
│   └── deployment/
└── infrastructure/   # Docker, scripts, deployment
    ├── docker/
    └── scripts/
```

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Docker (optional but recommended)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CivicQ
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Database Setup**
   ```bash
   # Create database
   createdb civicq

   # Run migrations
   cd backend
   alembic upgrade head
   ```

5. **Run Development Servers**
   ```bash
   # Terminal 1 - Backend
   cd backend
   uvicorn app.main:app --reload

   # Terminal 2 - Frontend
   cd frontend
   npm start
   ```

## Development Roadmap

### Phase 1: MVP (Current)
- [ ] Core database schema
- [ ] User authentication and verification
- [ ] Ballot and contest management
- [ ] Question submission and ranking
- [ ] Basic candidate portal
- [ ] Video recording interface
- [ ] Admin moderation console

### Phase 2: Pilot Ready
- [ ] Advanced ranking algorithm with anti-manipulation
- [ ] Video transcoding and captioning pipeline
- [ ] Candidate identity verification
- [ ] Comprehensive admin reporting
- [ ] Mobile-responsive design polish
- [ ] Performance optimization

### Phase 3: Production Scale
- [ ] Multi-city support
- [ ] Advanced analytics dashboard
- [ ] Automated duplicate detection
- [ ] Issue clustering and viewpoint mapping
- [ ] Accessibility compliance (WCAG 2.1 AA)
- [ ] Security audit and penetration testing

## Key Principles

1. **No Pay-to-Win**: No ads, no boosting, no sponsored content
2. **No Editing**: All videos recorded in-app, time-boxed, standardized
3. **Everything On Record**: Questions versioned, answers permanent
4. **Representative Ranking**: Community-shaped, not faction-shaped
5. **Verification Required**: For ranking and submitting, not for watching
6. **Modular & City-Configurable**: Adapt to local needs and laws

## Documentation

- [Architecture Overview](docs/architecture/overview.md)
- [Database Schema](docs/architecture/database-schema.md)
- [API Documentation](docs/api/README.md)
- [Ranking Algorithm](docs/architecture/ranking-algorithm.md)
- [Verification System](docs/architecture/verification.md)
- [Video Pipeline](docs/architecture/video-pipeline.md)
- [Pilot Playbook](docs/deployment/pilot-playbook.md)

## Contributing

This project is in active development. Contribution guidelines coming soon.

## License

TBD

## Contact

For pilot city inquiries or partnership discussions, contact: [TBD]

---

**Built to make local democracy more transparent, accessible, and focused on what voters actually care about.**
