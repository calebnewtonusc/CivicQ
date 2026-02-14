# CivicQ

**Turning campaigning into a standardized, verifiable public record of candidates answering the public's top questions, city by city, with integrity by design.**

## Overview

CivicQ is a city-level platform that transforms local elections by creating a public, verifiable record of candidates answering questions that voters actually care about. Instead of campaigning through expensive ads and attention-grabbing tactics, candidates engage directly with their constituents through structured, on-the-record video answers.

Starting with city council, mayor, school board, and local ballot measures, CivicQ addresses the critical information gap in local democracy: voters rarely know what candidates actually stand for, and candidates struggle to reach voters without significant campaign spending.

## Mission

CivicQ exists to make local democracy more transparent, accessible, and focused on substance over spectacle. We believe that civic engagement should be built on clear information, verifiable facts, and genuine accountability—not on who can spend the most money or generate the most outrage.

## Strategic Positioning

- **What CivicQ Is:** A civic infrastructure platform for transparent local elections, starting with city-level races
- **What CivicQ Is NOT:** A social media platform, a voting system, or a replacement for campaign finance law
- **Market Wedge:** City-level elections where voter information gaps are highest and adoption is most tractable
- **Long-term Vision:** The standard platform for local civic engagement, expanding to all levels of government

## Core Principles

1. **No Pay-to-Win:** No ads, no boosting, no sponsored content—equal visibility for all candidates
2. **Transparency First:** Everything on record, permanently; questions versioned, answers unedited
3. **Anti-Polarization by Design:** Structured to reduce outrage, not amplify it
4. **Representative Democracy:** Rankings reflect the whole community, not just the loudest faction
5. **Verification Without Barriers:** Protect integrity while keeping watching public and accessible

## Quick Links

### Product & Vision
- [Trust Model](docs/TRUST-MODEL.md) - How CivicQ builds and maintains trust
- [Privacy Framework](docs/PRIVACY.md) - Data handling and user privacy
- [MVP Scope](docs/MVP-SCOPE.md) - What we're building first
- [Product Philosophy](#core-principles) - Mission and operational principles

### Technical
- [Architecture Overview](docs/ARCHITECTURE.md) - System design and technical architecture
- [API Documentation](docs/API.md) - Complete API reference
- [Database Schema](docs/architecture/database-schema.md) - Data model details
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment instructions

### Development
- [Quick Start](QUICKSTART.md) - 5-minute local setup
- [Setup Guide](SETUP.md) - Detailed development environment setup
- [Testing Guide](TESTING.md) - Testing strategy and tools
- [Contributing](CONTRIBUTING.md) - How to contribute to CivicQ

### Execution
- [Development Roadmap](docs/ROADMAP.md) - 0-24 month execution plan
- [Project Status](STATUS.md) - Current status and next milestones

## Current Status

**Phase:** MVP Development
**Version:** v0.1.0-alpha (Pre-release)
**Next Milestone:** Core infrastructure and pilot city deployment

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

## Key Differentiators

1. **Anti-Polarization Design:** Portfolio ranking prevents faction dominance; no comments or engagement algorithms
2. **Verified Provenance:** Videos recorded in-app with cryptographic signing—no editing, no deepfakes
3. **Representative Ranking:** Questions represent the whole community through viewpoint clustering and issue balancing
4. **Modular Verification:** City-configurable identity verification that balances integrity with accessibility
5. **Public Accountability:** Everything on permanent record with full transparency and auditability

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

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed technical documentation.

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

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (with pgvector extension)
- Docker (optional but recommended)

### Quick Start (5 minutes)

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd CivicQ
   ```

2. **Backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend**
   ```bash
   cd frontend
   npm install
   ```

4. **Database**
   ```bash
   createdb civicq
   cd backend
   alembic upgrade head
   ```

5. **Run**
   ```bash
   # Terminal 1 - Backend
   cd backend && uvicorn app.main:app --reload

   # Terminal 2 - Frontend
   cd frontend && npm start
   ```

See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions.

### Deploy to Production

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for production deployment guide including:
- Vercel deployment (frontend)
- Railway/Render deployment (backend)
- Database and Redis setup
- Environment configuration
- Security considerations

## 30-Day Value Promise

Within 30 days of a city deploying CivicQ, voters will:
- Know what every candidate stands for on the top 10 community-identified issues
- Have watched candidate answers to questions they helped rank
- Trust that the platform is fair, transparent, and represents their community's concerns

**Examples:**
- Reduced "I didn't know who to vote for" responses
- Increased voter confidence in local election information
- Higher candidate participation in structured Q&A vs traditional forums
- Measurable reduction in negative campaigning spend

## Key Metrics

- **Voter Clarity Score:** % of voters who "understand candidate positions" before election day
- **Candidate Coverage:** % of candidates who answer top 10 community questions
- **Trust Score:** % of voters who "trust platform information accuracy"
- **Question Diversity:** Issue distribution across top-ranked questions (portfolio balance)

See [MVP-SCOPE.md](docs/MVP-SCOPE.md) for V1 feature scope and success criteria.

## Technology Stack

- **Voice Provenance:** In-app recording with cryptographic signing and tamper detection
- **Ranking Engine:** Portfolio-based ranking with viewpoint clustering and anomaly detection
- **Semantic Search:** pgvector for duplicate detection and question clustering
- **Video Pipeline:** Transcoding, captioning, and CDN delivery
- **Verification:** Modular identity verification adapters (city-configurable)

## Contributing

We welcome contributions from developers, civic technologists, and democracy advocates. See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup and workflow
- Code standards and testing requirements
- Pull request process
- Community guidelines

## Development Setup

See [SETUP.md](SETUP.md) for comprehensive development environment setup instructions.

## License

[To be determined - likely a combination of open-source software with proprietary components for city partnerships]

## Contact & Support

For pilot city inquiries, partnership discussions, or general questions:
- GitHub Issues: Technical questions and bug reports
- Email: [Contact information to be added]

## Acknowledgments

Built with insights from:
- Civic technology organizations and election administrators
- Democracy reform advocates and political scientists
- Open-source deliberation tools (Polis, vTaiwan)
- Voter information platforms (VOTE411, BallotReady)
- Content authenticity initiatives (Truepic, C2PA)

---

**Note:** This is an ambitious civic infrastructure project. We are building thoughtfully and ethically. Transparency, accessibility, and anti-polarization design are non-negotiable core values.

**Built to make local democracy more transparent, accessible, and focused on what voters actually care about.**
