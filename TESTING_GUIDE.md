# CivicQ Testing Guide

## Overview

This guide covers all testing practices, tools, and procedures for the CivicQ project. We maintain comprehensive test coverage across all layers of the application.

## Test Coverage Goals

- **Backend**: >80% code coverage
- **Frontend**: >70% code coverage
- **E2E**: All critical user journeys

## Table of Contents

1. [Backend Testing](#backend-testing)
2. [Frontend Testing](#frontend-testing)
3. [E2E Testing](#e2e-testing)
4. [Running Tests](#running-tests)
5. [Writing Tests](#writing-tests)
6. [CI/CD Integration](#cicd-integration)
7. [Troubleshooting](#troubleshooting)

---

## Backend Testing

### Technology Stack

- **Framework**: pytest
- **Coverage**: pytest-cov
- **Database**: SQLite (unit tests), PostgreSQL (integration tests)
- **Mocking**: unittest.mock

### Test Structure

```
backend/tests/
├── conftest.py                 # Shared fixtures and configuration
├── fixtures/
│   └── factories.py            # Test data factories
├── unit/
│   ├── test_models_user.py     # User model tests
│   ├── test_models_question.py # Question model tests
│   ├── test_models_city.py     # City model tests
│   └── test_service_auth.py    # Auth service tests
├── api/
│   ├── test_api_auth.py        # Auth endpoint tests
│   ├── test_api_questions.py   # Question endpoint tests
│   └── test_api_cities.py      # City endpoint tests
└── integration/
    └── test_workflow_voter_journey.py  # Full workflow tests
```

### Running Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest tests/unit          # Unit tests only
pytest tests/api           # API tests only
pytest tests/integration   # Integration tests only

# Run specific test file
pytest tests/unit/test_models_user.py

# Run specific test
pytest tests/unit/test_models_user.py::TestUserModel::test_create_user

# Run with markers
pytest -m "not slow"       # Skip slow tests
pytest -m integration      # Only integration tests
pytest -m api              # Only API tests

# Watch mode (requires pytest-watch)
ptw
```

### Test Fixtures

The `conftest.py` provides these fixtures:

- `db_session`: Fresh database session for each test
- `client`: FastAPI test client
- `test_user`: Pre-created voter user
- `test_admin`: Pre-created admin user
- `test_candidate`: Pre-created candidate user
- `test_city`: Pre-created city
- `test_contest`: Pre-created contest
- `auth_headers`: Authentication headers for test_user
- `admin_headers`: Authentication headers for test_admin
- `mock_email_service`: Mocked email service
- `mock_storage_service`: Mocked storage service
- `mock_redis`: Mocked Redis cache

### Test Factories

Use factories to create test data:

```python
from tests.fixtures.factories import UserFactory, QuestionFactory, CityFactory

def test_example(db_session):
    # Create a voter
    voter = UserFactory.create_voter(db_session, city_id="test-city")

    # Create a city with staff
    city, owner = CityFactory.create_with_staff(db_session)

    # Create an approved question
    question = QuestionFactory.create_approved(
        db_session,
        contest_id=contest.id,
        author_id=voter.id
    )

    # Build complex scenarios
    scenario = ScenarioBuilder.build_city_with_election(db_session)
    # Returns: city, contests, candidates, voters, questions
```

### Writing Backend Tests

#### Model Tests

```python
from app.models.user import User, UserRole

def test_create_user(db_session):
    """Test creating a new user."""
    user = User(
        email="test@example.com",
        hashed_password="hashed",
        role=UserRole.VOTER
    )
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.role == UserRole.VOTER
```

#### Service Tests

```python
from unittest.mock import patch
from app.services.auth_service import AuthService

def test_create_user_service(db_session):
    """Test user creation service."""
    with patch('app.services.email_service.send_verification'):
        user = AuthService.create_user(db_session, user_data)

    assert user.email == user_data.email
    assert user.email_verified is False
```

#### API Tests

```python
def test_register_endpoint(client, mock_email_service):
    """Test user registration endpoint."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "new@example.com",
            "password": "SecurePass123!",
            "full_name": "New User",
            "city": "San Francisco"
        }
    )

    assert response.status_code == 201
    assert response.json()["email"] == "new@example.com"
```

#### Integration Tests

```python
def test_complete_workflow(client, db_session, test_city):
    """Test complete user workflow."""
    # 1. Register
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201

    # 2. Login
    response = client.post("/api/v1/auth/login", data=credentials)
    token = response.json()["access_token"]

    # 3. Submit question
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/questions", headers=headers, json=question_data)
    assert response.status_code == 201
```

### Mocking External Services

```python
from unittest.mock import patch, MagicMock

def test_with_email_mock(mock_email_service):
    """Email service is automatically mocked via fixture."""
    # Your test code
    pass

def test_with_custom_mock():
    """Create custom mocks as needed."""
    with patch('app.services.ballot_data_service.fetch_data') as mock_fetch:
        mock_fetch.return_value = {"contests": []}
        # Your test code
```

---

## Frontend Testing

### Technology Stack

- **Framework**: Jest + React Testing Library
- **E2E**: Playwright
- **Accessibility**: jest-axe
- **Coverage**: Jest built-in

### Test Structure

```
frontend/src/
├── components/
│   ├── Navbar.tsx
│   └── __tests__/
│       └── Navbar.test.tsx
├── pages/
│   ├── Home.tsx
│   └── __tests__/
│       └── Home.test.tsx
└── setupTests.ts
```

### Running Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch

# Run specific test file
npm test Navbar.test

# Update snapshots
npm test -- -u
```

### Writing Frontend Tests

#### Component Tests

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { axe } from 'jest-axe';
import Navbar from '../Navbar';

describe('Navbar', () => {
  it('renders navigation links', () => {
    render(<Navbar />);
    expect(screen.getByText(/CivicQ/i)).toBeInTheDocument();
  });

  it('is accessible', async () => {
    const { container } = render(<Navbar />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('handles user interactions', async () => {
    const onLogout = jest.fn();
    render(<Navbar onLogout={onLogout} />);

    fireEvent.click(screen.getByText(/log out/i));
    expect(onLogout).toHaveBeenCalled();
  });
});
```

#### Testing with Context

```typescript
import { render } from '@testing-library/react';
import { AuthProvider } from '../../contexts/AuthContext';

const renderWithAuth = (component, authValue = {}) => {
  return render(
    <AuthProvider value={authValue}>
      {component}
    </AuthProvider>
  );
};

test('shows user menu when authenticated', () => {
  renderWithAuth(<Navbar />, { user: { name: 'Test' } });
  expect(screen.getByText(/Test/)).toBeInTheDocument();
});
```

#### Testing API Calls

```typescript
import { rest } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  rest.get('/api/v1/questions', (req, res, ctx) => {
    return res(ctx.json({ items: [] }));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test('fetches and displays questions', async () => {
  render(<QuestionList />);
  await waitFor(() => {
    expect(screen.getByText(/loading/i)).not.toBeInTheDocument();
  });
});
```

---

## E2E Testing

### Technology Stack

- **Framework**: Playwright
- **Browsers**: Chromium, Firefox, WebKit
- **Mobile**: iOS Safari, Android Chrome

### Running E2E Tests

```bash
cd e2e

# Install dependencies
npm install
npx playwright install

# Run all E2E tests
npx playwright test

# Run with UI
npx playwright test --ui

# Run specific test
npx playwright test voter-journey

# Run on specific browser
npx playwright test --project=chromium

# Debug mode
npx playwright test --debug

# Generate report
npx playwright show-report
```

### Writing E2E Tests

```typescript
import { test, expect } from '@playwright/test';

test('voter can submit question', async ({ page }) => {
  // Navigate to app
  await page.goto('/');

  // Login
  await page.click('text=Log In');
  await page.fill('input[name="email"]', 'voter@example.com');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');

  // Submit question
  await page.click('text=Ask Question');
  await page.fill('textarea', 'What is your housing plan?');
  await page.click('button:has-text("Submit")');

  // Verify success
  await expect(page.locator('text=Question submitted')).toBeVisible();
});
```

---

## Running Tests

### Quick Commands

```bash
# Backend
cd backend && pytest --cov=app

# Frontend
cd frontend && npm test -- --coverage

# E2E
cd e2e && npx playwright test

# All tests
make test  # If using Makefile
```

### Coverage Reports

```bash
# Backend coverage
cd backend
pytest --cov=app --cov-report=html
open htmlcov/index.html

# Frontend coverage
cd frontend
npm test -- --coverage
open coverage/lcov-report/index.html
```

---

## CI/CD Integration

Tests run automatically on:
- Push to `main` or `develop` branches
- Pull requests
- Manual workflow dispatch

### GitHub Actions Workflow

See `.github/workflows/tests.yml` for the complete CI/CD pipeline.

**Pipeline Stages:**
1. Backend unit tests
2. Backend API tests
3. Backend integration tests
4. Frontend unit tests
5. E2E tests
6. Security scanning
7. Coverage reporting

### Coverage Thresholds

CI fails if coverage drops below:
- Backend: 80%
- Frontend: 70%

---

## Test Best Practices

### General Guidelines

1. **Test Behavior, Not Implementation**
   - Test what users see and do
   - Avoid testing internal state

2. **Use Descriptive Test Names**
   ```python
   # Good
   def test_user_cannot_vote_on_own_question():

   # Bad
   def test_vote():
   ```

3. **Follow AAA Pattern**
   ```python
   def test_example():
       # Arrange
       user = create_user()

       # Act
       result = user.do_something()

       # Assert
       assert result == expected
   ```

4. **Keep Tests Independent**
   - Each test should run in isolation
   - Don't depend on test order

5. **Use Factories Over Fixtures**
   - Factories are more flexible
   - Create only what you need

### Backend Specific

- Use in-memory SQLite for fast unit tests
- Use PostgreSQL for integration tests
- Mock external APIs (email, storage, etc.)
- Test edge cases and error handling

### Frontend Specific

- Test accessibility with jest-axe
- Use Testing Library queries (`getByRole`, etc.)
- Test user interactions, not implementation
- Mock API calls with MSW

### E2E Specific

- Test critical user paths only
- Use data-testid for stable selectors
- Handle loading states and animations
- Test on multiple browsers

---

## Troubleshooting

### Common Issues

#### Backend Tests Fail with Database Errors

```bash
# Drop and recreate test database
dropdb civicq_test
createdb civicq_test
```

#### Frontend Tests Timeout

```typescript
// Increase timeout for slow tests
jest.setTimeout(10000);
```

#### E2E Tests Fail Randomly

```typescript
// Add wait for network idle
await page.waitForLoadState('networkidle');

// Wait for specific element
await page.waitForSelector('[data-testid="loaded"]');
```

#### Coverage Not Updating

```bash
# Clear coverage cache
rm -rf .coverage htmlcov/
pytest --cov=app --cov-report=html
```

### Getting Help

- Check test logs for detailed error messages
- Run tests in verbose mode: `pytest -v` or `npm test -- --verbose`
- Use debugger: `pytest --pdb` or add `debugger;` in JS
- Review CI/CD logs in GitHub Actions

---

## Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [React Testing Library](https://testing-library.com/react)
- [Playwright documentation](https://playwright.dev/)
- [jest-axe accessibility testing](https://github.com/nickcolley/jest-axe)

---

## Test Checklist for New Features

When adding a new feature, ensure:

- [ ] Unit tests for models
- [ ] Unit tests for services
- [ ] API endpoint tests
- [ ] Frontend component tests
- [ ] Integration tests for workflows
- [ ] E2E test for critical path
- [ ] Accessibility tests
- [ ] Error handling tests
- [ ] Edge case tests
- [ ] Documentation updated

---

Last Updated: 2024-02-14
