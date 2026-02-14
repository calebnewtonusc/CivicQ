# CivicQ Testing Standards

## Overview

This document outlines the testing standards and best practices for the CivicQ project. All contributors must follow these standards to maintain code quality and test coverage.

## Test Coverage Requirements

### Minimum Coverage Targets

- **Backend**: 80% overall, 90% for critical paths
- **Frontend**: 70% overall, 80% for core components
- **API Endpoints**: 100% coverage
- **Critical User Flows**: 100% E2E coverage

### What to Test

#### Must Test
- All API endpoints
- Authentication and authorization
- Data validation and sanitization
- Database operations (CRUD)
- Business logic in services
- Error handling
- Security features
- Critical user workflows

#### Should Test
- Edge cases
- Input validation
- State management
- UI components
- User interactions
- Form submissions
- Navigation

#### Can Skip
- Third-party library code
- Simple getters/setters
- Boilerplate code
- Auto-generated code

## Test Organization

### File Structure

```
tests/
├── unit/              # Unit tests (isolated)
├── integration/       # Integration tests (multiple components)
├── api/               # API endpoint tests
├── e2e/               # End-to-end tests
├── fixtures/          # Test data and factories
└── conftest.py        # Shared configuration
```

### Naming Conventions

#### Test Files
- Backend: `test_<module_name>.py`
- Frontend: `<ComponentName>.test.tsx`
- E2E: `<feature-name>.spec.ts`

#### Test Functions
```python
# Good
def test_user_can_create_question_with_valid_data():
    pass

def test_user_cannot_create_question_without_authentication():
    pass

# Bad
def test_question():
    pass

def test_create():
    pass
```

#### Test Classes
```python
# Group related tests
class TestQuestionCreation:
    def test_with_valid_data(self):
        pass

    def test_without_authentication(self):
        pass

    def test_with_invalid_contest(self):
        pass
```

## Test Quality Standards

### 1. Independence

Tests must be independent and not rely on execution order.

```python
# Good
def test_create_user(db_session):
    user = UserFactory.create(db_session)
    assert user.id is not None

# Bad
def test_create_user():
    # Relies on database state from previous test
    user = db.query(User).first()
    assert user is not None
```

### 2. Clarity

Tests should be clear and easy to understand.

```python
# Good
def test_approved_questions_appear_in_public_feed(db_session):
    """Approved questions should be visible to all users."""
    approved_question = QuestionFactory.create_approved(db_session)
    response = client.get("/api/v1/questions")
    questions = response.json()["items"]

    assert any(q["id"] == approved_question.id for q in questions)

# Bad
def test_questions(db_session):
    q = QuestionFactory.create(db_session, status="approved")
    r = client.get("/api/v1/questions")
    assert q.id in [x["id"] for x in r.json()["items"]]
```

### 3. Completeness

Test success cases, error cases, and edge cases.

```python
class TestPasswordReset:
    def test_reset_with_valid_token(self):
        """Success case"""
        pass

    def test_reset_with_expired_token(self):
        """Error case"""
        pass

    def test_reset_with_invalid_token(self):
        """Error case"""
        pass

    def test_reset_with_already_used_token(self):
        """Edge case"""
        pass
```

### 4. Speed

- Unit tests: < 100ms each
- Integration tests: < 1s each
- E2E tests: < 30s each

Use mocks to speed up tests:

```python
# Good - Fast
def test_send_email(mock_email_service):
    send_welcome_email(user)
    mock_email_service.send.assert_called_once()

# Bad - Slow
def test_send_email():
    send_welcome_email(user)  # Actually sends email
    # Wait and check email was sent
```

## Testing Patterns

### AAA Pattern (Arrange, Act, Assert)

```python
def test_user_can_upvote_question():
    # Arrange
    user = UserFactory.create_voter(db_session)
    question = QuestionFactory.create_approved(db_session)

    # Act
    vote = VoteFactory.create(
        db_session,
        user_id=user.id,
        question_id=question.id,
        value=1
    )

    # Assert
    assert vote.value == 1
    db_session.refresh(question)
    assert question.upvotes == 1
```

### Given-When-Then (BDD Style)

```python
def test_voter_journey():
    # Given a registered voter
    voter = UserFactory.create_voter(db_session)
    token = create_access_token(voter)

    # When they submit a question
    response = client.post(
        "/api/v1/questions",
        headers={"Authorization": f"Bearer {token}"},
        json=question_data
    )

    # Then the question is created
    assert response.status_code == 201
    assert response.json()["question_text"] == question_data["question_text"]
```

### Factory Pattern

Use factories instead of fixtures for dynamic test data:

```python
# Good
def test_multiple_users(db_session):
    users = [UserFactory.create(db_session) for _ in range(5)]
    assert len(users) == 5

# Less flexible
@pytest.fixture
def five_users(db_session):
    return [create_user(db_session) for _ in range(5)]
```

## Mocking Guidelines

### When to Mock

Mock external dependencies:
- Email services
- SMS services
- Storage services (S3)
- Payment processors
- Third-party APIs
- Time-sensitive operations

```python
from unittest.mock import patch
from datetime import datetime

def test_token_expiration():
    fixed_time = datetime(2024, 1, 1, 12, 0, 0)
    with patch('app.utils.datetime') as mock_datetime:
        mock_datetime.utcnow.return_value = fixed_time
        token = create_token(expires_in=3600)
        assert token.expires_at == datetime(2024, 1, 1, 13, 0, 0)
```

### When Not to Mock

Don't mock:
- Database operations (use test database)
- Your own code (test real behavior)
- Simple utilities
- Data structures

```python
# Good - Test real database interaction
def test_user_creation(db_session):
    user = User(email="test@example.com")
    db_session.add(user)
    db_session.commit()
    assert user.id is not None

# Bad - Mocking what we're testing
def test_user_creation():
    with patch('app.models.User') as MockUser:
        user = MockUser()
        # This doesn't test anything real
```

## Frontend Testing Standards

### Component Testing

```typescript
describe('QuestionCard', () => {
  it('renders question text', () => {
    render(<QuestionCard question={mockQuestion} />);
    expect(screen.getByText(mockQuestion.text)).toBeInTheDocument();
  });

  it('handles upvote click', async () => {
    const onVote = jest.fn();
    render(<QuestionCard question={mockQuestion} onVote={onVote} />);

    await userEvent.click(screen.getByLabelText('Upvote'));
    expect(onVote).toHaveBeenCalledWith(mockQuestion.id, 1);
  });

  it('is accessible', async () => {
    const { container } = render(<QuestionCard question={mockQuestion} />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

### Query Priority

Use Testing Library queries in this order:

1. `getByRole` - Best for accessibility
2. `getByLabelText` - Good for form fields
3. `getByPlaceholderText` - For inputs without labels
4. `getByText` - For non-interactive elements
5. `getByTestId` - Last resort

```typescript
// Good
const button = screen.getByRole('button', { name: /submit/i });
const input = screen.getByLabelText('Email');

// Avoid
const button = screen.getByTestId('submit-button');
```

## E2E Testing Standards

### Test Structure

```typescript
test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    // Setup common to all tests
    await page.goto('/');
  });

  test('specific user flow', async ({ page }) => {
    // Test one specific flow
  });
});
```

### Selectors

Use stable selectors:

```typescript
// Good
await page.click('[data-testid="submit-button"]');
await page.click('button:has-text("Submit")');
await page.click('button[aria-label="Submit"]');

// Avoid
await page.click('.btn-primary.submit');  // CSS classes change
await page.click('button:nth-child(2)');  // Position changes
```

### Waiting

Always wait for elements:

```typescript
// Good
await page.waitForSelector('[data-testid="success-message"]');
await expect(page.locator('text=Success')).toBeVisible();

// Bad
await page.click('button');
expect(page.locator('text=Success')).toBeVisible();  // Might not be visible yet
```

## Error Testing

Test error scenarios thoroughly:

```python
class TestErrorHandling:
    def test_404_for_nonexistent_resource(self, client):
        response = client.get("/api/v1/questions/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_401_for_unauthenticated_request(self, client):
        response = client.post("/api/v1/questions", json={})
        assert response.status_code == 401

    def test_422_for_invalid_input(self, client, auth_headers):
        response = client.post(
            "/api/v1/questions",
            headers=auth_headers,
            json={"question_text": ""}  # Empty text
        )
        assert response.status_code == 422
```

## Security Testing

### Authentication Tests

```python
def test_protected_endpoint_requires_auth(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

def test_invalid_token_rejected(client):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid"}
    )
    assert response.status_code == 401
```

### Authorization Tests

```python
def test_voter_cannot_access_admin_endpoint(client, auth_headers):
    response = client.get("/api/v1/admin/users", headers=auth_headers)
    assert response.status_code == 403

def test_user_cannot_modify_other_users_data(client, db_session):
    user1 = UserFactory.create(db_session)
    user2 = UserFactory.create(db_session)

    token1 = create_access_token(user1)
    headers1 = {"Authorization": f"Bearer {token1}"}

    response = client.patch(
        f"/api/v1/users/{user2.id}",
        headers=headers1,
        json={"full_name": "Hacked"}
    )
    assert response.status_code == 403
```

### Input Validation Tests

```python
def test_sql_injection_prevented(client, auth_headers):
    response = client.get(
        "/api/v1/questions?search='; DROP TABLE users; --",
        headers=auth_headers
    )
    # Should not crash, should sanitize input
    assert response.status_code in [200, 400]

def test_xss_prevented(client, auth_headers, test_contest):
    response = client.post(
        "/api/v1/questions",
        headers=auth_headers,
        json={
            "contest_id": test_contest.id,
            "question_text": "<script>alert('XSS')</script>"
        }
    )
    # Should either reject or sanitize
    if response.status_code == 201:
        question = response.json()
        assert "<script>" not in question["question_text"]
```

## Performance Testing

```python
import time

def test_api_response_time(client):
    start = time.time()
    response = client.get("/api/v1/questions")
    duration = time.time() - start

    assert response.status_code == 200
    assert duration < 0.5  # Should respond in under 500ms
```

## Accessibility Testing

```typescript
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

describe('Accessibility', () => {
  it('has no violations', async () => {
    const { container } = render(<App />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('is keyboard navigable', () => {
    render(<Form />);
    const input = screen.getByLabelText('Email');

    input.focus();
    expect(document.activeElement).toBe(input);
  });

  it('has proper ARIA labels', () => {
    render(<Button icon="save" />);
    expect(screen.getByLabelText('Save')).toBeInTheDocument();
  });
});
```

## Code Review Checklist

Before approving a PR, verify:

- [ ] All tests pass
- [ ] Coverage meets minimum thresholds
- [ ] Tests follow AAA pattern
- [ ] Error cases are tested
- [ ] Edge cases are covered
- [ ] Mocks are used appropriately
- [ ] Tests are independent
- [ ] Test names are descriptive
- [ ] No hardcoded values
- [ ] Accessibility tests included
- [ ] Security considerations tested

## Common Anti-Patterns

### ❌ Avoid

```python
# Testing implementation details
def test_user_model():
    user = User()
    assert hasattr(user, '_hashed_password')  # Implementation detail

# Fragile tests
def test_get_users():
    response = client.get("/users")
    assert len(response.json()) == 5  # Breaks when data changes

# Not testing error cases
def test_login():
    # Only tests success case
    response = client.post("/login", json=valid_credentials)
    assert response.status_code == 200
```

### ✅ Do

```python
# Testing behavior
def test_user_password_is_hashed():
    user = User(password="plain")
    assert user.verify_password("plain")  # Test behavior, not implementation

# Flexible tests
def test_get_users():
    response = client.get("/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Test all scenarios
def test_login_scenarios():
    # Test success
    response = client.post("/login", json=valid_credentials)
    assert response.status_code == 200

    # Test failure
    response = client.post("/login", json=invalid_credentials)
    assert response.status_code == 401
```

---

## Continuous Improvement

- Review and update test standards quarterly
- Track and improve coverage metrics
- Share testing best practices in team meetings
- Learn from test failures and near-misses
- Refactor tests as code evolves

---

Last Updated: 2024-02-14
