# CivicQ Testing Quick Reference

## Run Tests

### Backend
```bash
cd backend
pytest                           # All tests
pytest --cov=app                 # With coverage
pytest tests/unit                # Unit tests only
pytest -m "not slow"             # Skip slow tests
```

### Frontend
```bash
cd frontend
npm test                         # All tests
npm test -- --coverage           # With coverage
npm test -- --watch              # Watch mode
```

### E2E
```bash
cd e2e
npx playwright test              # All tests
npx playwright test --ui         # With UI
npx playwright test --debug      # Debug mode
```

### All Tests (via Makefile)
```bash
make -f Makefile.testing test                # All tests
make -f Makefile.testing test-backend        # Backend only
make -f Makefile.testing test-frontend       # Frontend only
make -f Makefile.testing test-e2e            # E2E only
make -f Makefile.testing coverage            # Generate coverage
```

## Write Tests

### Backend Unit Test
```python
def test_create_user(db_session):
    """Test user creation."""
    # Arrange
    user = UserFactory.create(db_session, email="test@example.com")

    # Act
    db_session.add(user)
    db_session.commit()

    # Assert
    assert user.id is not None
    assert user.email == "test@example.com"
```

### Backend API Test
```python
def test_register_endpoint(client, mock_email_service):
    """Test registration endpoint."""
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "new@example.com", "password": "SecurePass123!"}
    )

    assert response.status_code == 201
    assert response.json()["email"] == "new@example.com"
```

### Frontend Component Test
```typescript
import { render, screen, fireEvent } from '@testing-library/react';

test('button click triggers callback', () => {
  const onClick = jest.fn();
  render(<Button onClick={onClick}>Click Me</Button>);

  fireEvent.click(screen.getByText('Click Me'));
  expect(onClick).toHaveBeenCalled();
});
```

### E2E Test
```typescript
test('user can submit question', async ({ page }) => {
  await page.goto('/');
  await page.click('text=Ask Question');
  await page.fill('textarea', 'What is your plan?');
  await page.click('button:has-text("Submit")');
  await expect(page.locator('text=Success')).toBeVisible();
});
```

## Common Fixtures

### Backend
```python
db_session          # Database session
client              # FastAPI test client
test_user           # Pre-created user
test_admin          # Pre-created admin
auth_headers        # Auth headers for test_user
admin_headers       # Auth headers for admin
mock_email_service  # Mocked email service
```

### Factories
```python
UserFactory.create_voter(db_session)
UserFactory.create_candidate(db_session)
UserFactory.create_admin(db_session)
CityFactory.create(db_session)
QuestionFactory.create_approved(db_session, contest_id, author_id)
```

## Test Markers

```bash
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
pytest -m api               # API tests only
pytest -m "not slow"        # Skip slow tests
```

## Coverage Commands

### Generate Coverage
```bash
# Backend
cd backend && pytest --cov=app --cov-report=html

# Frontend
cd frontend && npm test -- --coverage
```

### View Coverage
```bash
# Backend
open backend/htmlcov/index.html

# Frontend
open frontend/coverage/lcov-report/index.html
```

## Test Organization

```
tests/
├── unit/           # Isolated component tests
├── api/            # API endpoint tests
├── integration/    # Multi-component tests
├── e2e/            # End-to-end browser tests
└── fixtures/       # Shared test data
```

## Best Practices

### DO ✅
- Test behavior, not implementation
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)
- Keep tests independent
- Mock external services
- Test error cases
- Test edge cases

### DON'T ❌
- Test implementation details
- Make tests dependent on order
- Skip error handling tests
- Hardcode test data
- Test third-party code
- Make tests slow without marking

## Quick Debugging

### Backend
```bash
pytest --pdb                 # Drop into debugger on failure
pytest -vv                   # Very verbose output
pytest -x                    # Stop on first failure
pytest --lf                  # Run last failed tests
```

### Frontend
```bash
npm test -- --no-coverage    # Faster without coverage
npm test ComponentName       # Run specific test file
```

### E2E
```bash
npx playwright test --debug  # Debug mode
npx playwright codegen       # Record test actions
```

## Coverage Targets

- Backend: >80%
- Frontend: >70%
- E2E: 100% critical paths

## CI/CD

Tests run automatically on:
- Push to main/develop
- Pull requests
- Manual trigger

View results: GitHub Actions tab

## Help

- 📖 Full Guide: `TESTING_GUIDE.md`
- 📋 Standards: `TESTING_STANDARDS.md`
- 🎯 Summary: `TESTING_INFRASTRUCTURE_COMPLETE.md`

## Common Issues

### Tests fail with DB errors
```bash
# Reset test database
dropdb civicq_test
createdb civicq_test
```

### Coverage not updating
```bash
# Clear coverage cache
rm -rf .coverage htmlcov/
```

### E2E tests timeout
```typescript
// Increase timeout
test.setTimeout(60000);
```

## Quick Examples

### Test authenticated endpoint
```python
def test_protected_endpoint(client, auth_headers):
    response = client.get("/api/v1/protected", headers=auth_headers)
    assert response.status_code == 200
```

### Test error case
```python
def test_invalid_input(client):
    response = client.post("/api/v1/endpoint", json={"invalid": "data"})
    assert response.status_code == 422
```

### Test accessibility
```typescript
import { axe } from 'jest-axe';

test('is accessible', async () => {
  const { container } = render(<Component />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

---

For more details, see `TESTING_GUIDE.md`
