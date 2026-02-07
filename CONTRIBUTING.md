# Contributing to CivicQ

Thank you for your interest in contributing to CivicQ! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/CivicQ.git`
3. Follow the [Setup Guide](SETUP.md) to get your development environment running
4. Create a new branch: `git checkout -b feature/your-feature-name`

## Development Principles

CivicQ is built on these core principles:

1. **Integrity First** - All features must maintain data integrity and authenticity
2. **Anti-Polarization** - Design choices should reduce polarization, not amplify it
3. **Transparency** - Actions and algorithms should be transparent and auditable
4. **Accessibility** - The platform must be accessible to all users
5. **Privacy** - Minimize data collection and protect user privacy

## Code Style

### Backend (Python)
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use meaningful variable names
- Add docstrings to all functions and classes

Run linters before committing:
```bash
black backend/
flake8 backend/
mypy backend/
```

### Frontend (TypeScript/React)
- Use TypeScript for type safety
- Follow React best practices
- Use functional components with hooks
- Prefer composition over inheritance
- Maximum line length: 100 characters

Run linters before committing:
```bash
npm run lint
npm run format
```

## Commit Messages

Use clear, descriptive commit messages:

```
feat: Add question deduplication algorithm
fix: Resolve video upload timeout issue
docs: Update API documentation
test: Add tests for ranking algorithm
refactor: Simplify authentication middleware
```

Prefixes:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `test:` - Tests
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md (if applicable)
5. Request review from maintainers
6. Address review feedback
7. Squash commits if requested

## Testing

### Backend Tests
```bash
cd backend
pytest
pytest --cov=app tests/  # With coverage
```

### Frontend Tests
```bash
cd frontend
npm test
npm test -- --coverage
```

## Areas Needing Help

### High Priority
- [ ] Database migrations setup (Alembic)
- [ ] Authentication implementation
- [ ] Question ranking algorithm
- [ ] Video recording interface
- [ ] Moderation queue

### Medium Priority
- [ ] Comprehensive test coverage
- [ ] Accessibility improvements
- [ ] Performance optimization
- [ ] Documentation expansion

### Low Priority
- [ ] Internationalization (i18n)
- [ ] Dark mode
- [ ] Mobile app (React Native)

## Questions?

- Open an issue for discussion
- Join our community (TBD)
- Review existing documentation in `docs/`

## Code of Conduct

Be respectful, inclusive, and professional. We're building a civic tool that should set a high standard.

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (TBD).
