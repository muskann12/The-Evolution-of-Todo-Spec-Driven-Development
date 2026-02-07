# Skill: End-to-End Testing

## Description
Write comprehensive E2E tests using Playwright to test the full user journey from frontend to backend.

## When to Use
- Testing complete user workflows
- Validating frontend-backend integration
- Before production deployment

## Workflow

### 1. Install Playwright
```bash
cd frontend
npm install -D @playwright/test
npx playwright install
```

### 2. Configure Playwright
```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  use: {
    baseURL: 'http://localhost:3000',
  },
  webServer: {
    command: 'npm run dev',
    port: 3000,
  },
});
```

### 3. Write E2E Tests
```typescript
// e2e/todos.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Todo App', () => {
  test('should create a new todo', async ({ page }) => {
    await page.goto('/');

    // Fill in the form
    await page.fill('input[placeholder="Todo title"]', 'Buy groceries');
    await page.fill('textarea[placeholder="Description"]', 'Milk, bread, eggs');

    // Submit
    await page.click('button:has-text("Add Todo")');

    // Verify todo appears
    await expect(page.locator('text=Buy groceries')).toBeVisible();
  });

  test('should mark todo as complete', async ({ page }) => {
    await page.goto('/');

    // Click checkbox
    const checkbox = page.locator('input[type="checkbox"]').first();
    await checkbox.click();

    // Verify completed state
    await expect(checkbox).toBeChecked();
  });

  test('should delete todo', async ({ page }) => {
    await page.goto('/');

    // Click delete button
    await page.click('button:has-text("Delete")').first();

    // Verify todo is removed
    await expect(page.locator('.todo-item')).toHaveCount(0);
  });
});
```

### 4. Run Tests
```bash
# Run tests
npx playwright test

# Run with UI
npx playwright test --ui

# Debug mode
npx playwright test --debug
```

## Checklist
- [ ] Playwright installed and configured
- [ ] E2E tests cover main workflows
- [ ] Tests run reliably
- [ ] CI/CD integration configured
- [ ] Test reports generated

## References
- [Playwright](https://playwright.dev/)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
