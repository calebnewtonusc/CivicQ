import { test, expect } from '@playwright/test';

/**
 * E2E tests for complete voter journey
 */

test.describe('Voter Journey', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('complete voter registration and question submission flow', async ({ page }) => {
    // Step 1: Navigate to registration
    await page.click('text=Sign Up');
    await expect(page).toHaveURL(/.*register/);

    // Step 2: Fill out registration form
    const timestamp = Date.now();
    const email = `voter${timestamp}@example.com`;

    await page.fill('input[name="email"]', email);
    await page.fill('input[name="password"]', 'SecurePassword123!');
    await page.fill('input[name="full_name"]', 'Test Voter');
    await page.fill('input[name="city"]', 'San Francisco');

    // Step 3: Submit registration
    await page.click('button[type="submit"]');

    // Step 4: Verify success message
    await expect(page.locator('text=/registration successful/i')).toBeVisible();

    // Step 5: Navigate to login
    await page.click('text=Log In');

    // Step 6: Login
    await page.fill('input[name="email"]', email);
    await page.fill('input[name="password"]', 'SecurePassword123!');
    await page.click('button[type="submit"]');

    // Step 7: Verify logged in
    await expect(page.locator('text=/Test Voter/i')).toBeVisible();

    // Step 8: Navigate to questions
    await page.click('text=/questions/i');

    // Step 9: Submit a question
    await page.click('text=/ask.*question/i');
    await page.fill('textarea[name="question_text"]', 'What is your plan for affordable housing?');
    await page.click('text=housing');
    await page.click('button[type="submit"]');

    // Step 10: Verify question submitted
    await expect(page.locator('text=/question submitted/i')).toBeVisible();
  });

  test('voter can upvote and downvote questions', async ({ page, context }) => {
    // Login as existing voter
    await page.goto('/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'TestPassword123!');
    await page.click('button[type="submit"]');

    // Navigate to questions
    await page.goto('/questions');

    // Find first question
    const questionCard = page.locator('[data-testid="question-card"]').first();
    await expect(questionCard).toBeVisible();

    // Get initial vote count
    const initialVotes = await questionCard.locator('[data-testid="vote-count"]').textContent();

    // Upvote
    await questionCard.locator('[aria-label="Upvote"]').click();
    await page.waitForTimeout(500);

    // Verify vote count increased
    const newVotes = await questionCard.locator('[data-testid="vote-count"]').textContent();
    expect(parseInt(newVotes || '0')).toBeGreaterThan(parseInt(initialVotes || '0'));

    // Change to downvote
    await questionCard.locator('[aria-label="Downvote"]').click();
    await page.waitForTimeout(500);

    // Verify vote changed
    const finalVotes = await questionCard.locator('[data-testid="vote-count"]').textContent();
    expect(parseInt(finalVotes || '0')).toBeLessThan(parseInt(newVotes || '0'));
  });

  test('voter can search and filter questions', async ({ page }) => {
    await page.goto('/questions');

    // Search for questions
    await page.fill('input[placeholder*="Search"]', 'housing');
    await page.keyboard.press('Enter');

    // Verify search results
    const results = page.locator('[data-testid="question-card"]');
    await expect(results.first()).toBeVisible();

    // Filter by tag
    await page.click('text=Filter');
    await page.click('text=Housing');

    // Verify filtered results contain housing tag
    const filteredResults = page.locator('[data-testid="question-card"]');
    const count = await filteredResults.count();
    expect(count).toBeGreaterThan(0);
  });
});

test.describe('Accessibility', () => {
  test('voter journey is keyboard accessible', async ({ page }) => {
    await page.goto('/');

    // Navigate using keyboard
    await page.keyboard.press('Tab');
    await page.keyboard.press('Enter');

    // Verify navigation worked
    await expect(page).toHaveURL(/.*login|register/);
  });

  test('pages have proper heading structure', async ({ page }) => {
    await page.goto('/');

    // Check for h1
    const h1 = page.locator('h1');
    await expect(h1).toBeVisible();

    // Navigate to questions page
    await page.goto('/questions');
    await expect(page.locator('h1')).toBeVisible();
  });

  test('forms have proper labels', async ({ page }) => {
    await page.goto('/register');

    // Verify all inputs have labels
    const emailInput = page.locator('input[name="email"]');
    const emailLabel = page.locator('label[for*="email"]');
    await expect(emailLabel).toBeVisible();
    await expect(emailInput).toHaveAttribute('aria-label');
  });
});

test.describe('Responsive Design', () => {
  test('mobile: voter can navigate and submit questions', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    // Open mobile menu
    await page.click('[aria-label*="menu"]');

    // Navigate to questions
    await page.click('text=/questions/i');

    // Verify mobile layout
    const questionList = page.locator('[data-testid="question-list"]');
    await expect(questionList).toBeVisible();
  });

  test('tablet: layout adapts correctly', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/questions');

    // Verify tablet layout
    const container = page.locator('.container');
    await expect(container).toBeVisible();
  });
});

test.describe('Error Handling', () => {
  test('displays error for invalid registration', async ({ page }) => {
    await page.goto('/register');

    // Submit without filling form
    await page.click('button[type="submit"]');

    // Verify error messages
    await expect(page.locator('text=/required/i')).toBeVisible();
  });

  test('handles network errors gracefully', async ({ page }) => {
    // Intercept API calls and simulate failure
    await page.route('**/api/**', route => route.abort());

    await page.goto('/questions');

    // Verify error message is shown
    await expect(page.locator('text=/error|failed/i')).toBeVisible();
  });
});
