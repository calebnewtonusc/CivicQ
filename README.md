# CivicQ

**Turning campaigning into a standardized, verifiable public record of candidates answering the public's top questions, city by city, with integrity by design.**

## Overview

CivicQ is a city-level platform that transforms local elections by creating a public, verifiable record of candidates answering questions that voters actually care about. Instead of campaigning through expensive ads and attention-grabbing tactics, candidates engage directly with their constituents through structured, on-the-record video answers.

Starting with city council, mayor, school board, and local ballot measures, CivicQ addresses the critical information gap in local democracy: voters rarely know what candidates actually stand for, and candidates struggle to reach voters without significant campaign spending.

## Mission

CivicQ exists to make local democracy more transparent, accessible, and focused on substance over spectacle. We believe that civic engagement should be built on clear information, verifiable facts, and genuine accountability—not on who can spend the most money or generate the most outrage.

---

## What is CivicQ?

CivicQ is a **civic infrastructure platform** for local elections that enables:

- **Voters** to see their personalized ballot, ask questions, vote on what matters most, and watch candidate video answers
- **Candidates** to answer community questions fairly with equal visibility for all, no pay-to-win
- **Cities** to provide transparent election information with reduced voter confusion and increased legitimacy

### Core Principles

1. **No Pay-to-Win:** No ads, no boosting, no sponsored content—equal visibility for all candidates
2. **Transparency First:** Everything on record, permanently; questions versioned, answers unedited
3. **Anti-Polarization by Design:** Structured to reduce outrage, not amplify it
4. **Representative Democracy:** Rankings reflect the whole community, not just the loudest faction
5. **Verification Without Barriers:** Protect integrity while keeping watching public and accessible

---

## Key Features

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

---

## Tech Stack

- **Frontend**: React 18 + TypeScript + Tailwind CSS
- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+ with pgvector for semantic search
- **Caching**: Redis
- **Media**: Video transcoding, captioning, CDN delivery
- **Infrastructure**: Docker, cloud-agnostic design

---

## Quick Start

Get up and running in 5 minutes:

```bash
# Clone the repository
git clone <repository-url>
cd CivicQ

# Start with Docker Compose (recommended)
docker-compose up -d

# Or use Make commands
make setup    # First time only
make dev      # Start all services
```

Then visit:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

For detailed instructions, see [QUICK_START.md](QUICK_START.md)

---

## Documentation

### Getting Started
- [Quick Start Guide](QUICK_START.md) - Get running in 5 minutes
- [Setup Guide](SETUP.md) - Detailed development environment setup
- [Testing Guide](TESTING.md) - Testing strategy and tools

### Project Overview
- [What is CivicQ?](CivicQ.md) - Original PRD and product philosophy
- [Project Status](STATUS.md) - Current development status
- [Roadmap](docs/ROADMAP.md) - 0-24 month execution plan

### Technical Documentation
- [Architecture Overview](docs/ARCHITECTURE.md) - System design and technical architecture
- [API Documentation](docs/API.md) - Complete API reference
- [Database Schema](docs/architecture/database-schema.md) - Data model details
- [AI Features](docs/AI_FEATURES.md) - Claude Sonnet 4.5 integration

### Product & Strategy
- [MVP Scope](docs/MVP-SCOPE.md) - What we're building first
- [Trust Model](docs/TRUST-MODEL.md) - How CivicQ builds and maintains trust
- [Privacy Framework](docs/PRIVACY.md) - Data handling and user privacy
- [UX Best Practices](docs/UX-BEST-PRACTICES.md) - Research-based UX recommendations
- [UX Summary](docs/UX-RECOMMENDATIONS-SUMMARY.md) - Quick reference guide

### Deployment & Operations
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment instructions
- [Security Policy](SECURITY.md) - Security practices and vulnerability reporting

### Contributing
- [Contributing Guide](CONTRIBUTING.md) - How to contribute to CivicQ
- [Code of Conduct](CODE_OF_CONDUCT.md) - Community guidelines
- [Changelog](CHANGELOG.md) - Version history and release notes

### Business & Legal
- [Business Model](docs/business/business-model.md) - Revenue and sustainability
- [Go-to-Market Strategy](docs/business/go-to-market.md) - Launch and growth plan
- [Legal Compliance](docs/legal/compliance-framework.md) - Election law and regulations

### Complete Documentation Index
See [docs/INDEX.md](docs/INDEX.md) for a comprehensive index of all documentation.

---

## Project Structure

```
CivicQ/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── api/      # API routes
│   │   ├── core/     # Config, security, auth
│   │   ├── models/   # Database models
│   │   ├── services/ # Business logic (LLM, auth, questions, etc.)
│   │   └── utils/    # Helpers
│   └── tests/        # Backend tests
├── frontend/         # React frontend
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API clients
│   │   ├── utils/       # Utilities
│   │   └── types/       # TypeScript types
│   └── public/       # Static assets
├── database/         # Schema and migrations
│   ├── migrations/   # Alembic migrations
│   └── schemas/      # SQL schema files
├── docs/             # Documentation
│   ├── architecture/ # Technical architecture
│   ├── business/     # Business strategy
│   ├── legal/        # Legal compliance
│   └── product/      # Product vision
├── infrastructure/   # Docker, scripts, deployment
│   ├── docker/       # Dockerfiles
│   └── scripts/      # Utility scripts
└── scripts/          # Development and deployment scripts
```

---

## Current Status

**Phase:** MVP Development
**Version:** v0.1.0-alpha (Pre-release)
**Next Milestone:** Core infrastructure and pilot city deployment

### What's Complete
- Complete backend API (35+ endpoints)
- Full-featured React frontend with TypeScript
- PostgreSQL database with pgvector extension
- JWT authentication and authorization
- Question submission and voting system
- Candidate portal and video management
- AI-powered question assistance (Claude Sonnet 4.5)
- Comprehensive documentation (~147KB)
- CI/CD pipelines and testing infrastructure

### What's Next
- Video recording interface (browser-based)
- Video transcoding pipeline
- Question deduplication with vector similarity
- Admin moderation console UI
- First pilot city deployment

See [STATUS.md](STATUS.md) for detailed status.

---

## Anti-Polarization by Design

Unlike social media platforms that reward outrage, CivicQ is built to prevent polarization:

- **No Comments**: No performative dunking or flame wars
- **No Engagement Algorithms**: Not a feed, it's a library
- **Portfolio Ranking**: Questions represent the whole community, not just loud factions
- **Structured Rebuttals**: Responses must cite specific claims, not enable attacks
- **Viewpoint Clustering**: Prevents one faction from dominating the top questions

---

## Key Differentiators

1. **Anti-Polarization Design:** Portfolio ranking prevents faction dominance; no comments or engagement algorithms
2. **Verified Provenance:** Videos recorded in-app with cryptographic signing—no editing, no deepfakes
3. **Representative Ranking:** Questions represent the whole community through viewpoint clustering and issue balancing
4. **Modular Verification:** City-configurable identity verification that balances integrity with accessibility
5. **Public Accountability:** Everything on permanent record with full transparency and auditability

---

## AI-Powered Features

CivicQ integrates **Claude Sonnet 4.5** for intelligent assistance:

- **Smart Question Composer**: Real-time quality scoring, categorization, and suggestions
- **Duplicate Detection**: Semantic similarity to prevent redundant questions
- **Suggested Questions**: AI-generated starter questions specific to each contest
- **Quality Analysis**: Evaluates clarity, specificity, and relevance (0-100 score)

See [docs/AI_FEATURES.md](docs/AI_FEATURES.md) for details.

---

## Contributing

We welcome contributions from developers, civic technologists, and democracy advocates!

**To contribute:**

1. Read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines
2. Check [STATUS.md](STATUS.md) for current priorities
3. Review the [Roadmap](docs/ROADMAP.md) for upcoming features
4. Submit a pull request following our code standards

**Areas we need help:**
- Frontend UX improvements
- Backend performance optimization
- Documentation and examples
- Testing and QA
- Security audits

---

## Deployment

CivicQ is production-ready and can be deployed to:

- **Frontend**: Vercel, Netlify, or any static hosting
- **Backend**: Railway, Render, AWS ECS, or any Docker host
- **Database**: Neon, AWS RDS, Google Cloud SQL, or self-hosted PostgreSQL

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for complete deployment guide.

---

## Security

We take security seriously. CivicQ includes:

- JWT authentication with bcrypt password hashing
- HTTPS-only with TLS 1.3
- CORS and CSRF protection
- Rate limiting and DDoS protection
- Encryption at rest and in transit
- Comprehensive audit logging

Report security vulnerabilities to our security team (see [SECURITY.md](SECURITY.md)).

---

## License

[To be determined - likely a combination of open-source software with proprietary components for city partnerships]

---

## Support & Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/CivicQ/issues)
- **Documentation**: [docs/INDEX.md](docs/INDEX.md)
- **Email**: [Contact information to be added]

---

## Acknowledgments

Built with insights from:
- Civic technology organizations and election administrators
- Democracy reform advocates and political scientists
- Open-source deliberation tools (Polis, vTaiwan)
- Voter information platforms (VOTE411, BallotReady)
- Content authenticity initiatives (Truepic, C2PA)

Powered by:
- Claude Sonnet 4.5 for AI features
- Modern web technologies (React, FastAPI, PostgreSQL)
- Open-source community contributions

---

**Built to make local democracy more transparent, accessible, and focused on what voters actually care about.**

**CivicQ: Democracy through clarity, not chaos.**
