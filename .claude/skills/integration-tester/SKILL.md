---
name: integration-tester
description: |
  End-to-end integration testing that validates complete user flows from frontend UI through backend API to database.
---

# Integration Tester

End-to-end integration testing that validates complete user flows from frontend UI through backend API to database.

## When to Use This Skill
- User needs to test complete user flows
- User mentions "test signup flow" or "test checkout"
- User wants to catch integration bugs before production
- User needs automated testing across services

## Procedure
1. **Choose testing framework**: Playwright, Cypress, or Selenium
2. **Setup test environment**: Isolated database, test API
3. **Write flow tests**: Complete user journeys (signup → login → action)
4. **Mock external services**: Payment gateways, email, etc.
5. **Run in CI/CD**: Automate on every PR

## Output Format
**Test Suite**:
- E2E test files for key flows
- Test environment configuration
- Helper functions and fixtures
- CI/CD integration

## Quality Criteria
- Tests represent real user behavior
- Isolated test data (no shared state)
- Fast execution (parallel where possible)
- Clear failure messages
- Test both happy path and error cases
- Cleanup after each test

## Example
**Input**: "Create integration tests for user signup and login flow"

**Output**:

**Playwright Setup** (`playwright.config.ts`):
```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,

  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure'
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    }
  ],

  webServer: [
    {
      command: 'cd apps/backend && python -m uvicorn main:app --port 8000',
      port: 8000,
      reuseExistingServer: !process.env.CI
    },
    {
      command: 'cd apps/frontend && npm run dev',
      port: 3000,
      reuseExistingServer: !process.env.CI
    }
  ]
});
```

**Auth Flow Test** (`tests/e2e/auth.spec.ts`):
```typescript
import { test, expect } from '@playwright/test';
import { setupTestDB, clearTestDB } from './helpers/database';
import { generateTestEmail } from './helpers/utils';

test.describe('Authentication Flow', () => {
  test.beforeEach(async () => {
    // Setup isolated test database
    await setupTestDB();
  });

  test.afterEach(async () => {
    // Cleanup test data
    await clearTestDB();
  });

  test('complete signup → email verification → login flow', async ({ page }) => {
    const email = generateTestEmail();
    const password = 'TestPass123!';
    const name = 'Test User';

    // 1. Navigate to signup page
    await page.goto('/signup');
    await expect(page).toHaveTitle(/Sign Up/);

    // 2. Fill signup form
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill(password);
    await page.getByLabel('Name').fill(name);
    await page.getByRole('button', { name: 'Sign Up' }).click();

    // 3. Verify success message
    await expect(page.getByText('Check your email for verification link')).toBeVisible();

    // 4. Simulate email verification (bypass email service)
    const verificationToken = await getVerificationToken(email);
    await page.goto(`/verify-email?token=${verificationToken}`);
    await expect(page.getByText('Email verified successfully')).toBeVisible();

    // 5. Login with new account
    await page.goto('/login');
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill(password);
    await page.getByRole('button', { name: 'Login' }).click();

    // 6. Verify logged in state
    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByText(`Welcome, ${name}`)).toBeVisible();

    // 7. Check auth token is set
    const cookies = await page.context().cookies();
    const refreshToken = cookies.find(c => c.name === 'refresh_token');
    expect(refreshToken).toBeDefined();
  });

  test('signup with existing email shows error', async ({ page }) => {
    const email = 'existing@example.com';

    // Pre-create user
    await createTestUser({ email, password: 'Pass123!', name: 'Existing' });

    await page.goto('/signup');
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill('NewPass123!');
    await page.getByLabel('Name').fill('New User');
    await page.getByRole('button', { name: 'Sign Up' }).click();

    // Verify error message
    await expect(page.getByText('Email already registered')).toBeVisible();
    await expect(page).toHaveURL('/signup');
  });

  test('login with wrong password shows error', async ({ page }) => {
    const email = 'user@example.com';
    await createTestUser({ email, password: 'CorrectPass123!', name: 'User' });

    await page.goto('/login');
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill('WrongPassword');
    await page.getByRole('button', { name: 'Login' }).click();

    await expect(page.getByText('Email or password is incorrect')).toBeVisible();
    await expect(page).toHaveURL('/login');
  });

  test('session persists after page reload', async ({ page }) => {
    // Login
    const { email, password } = await createTestUser({
      email: generateTestEmail(),
      password: 'Pass123!',
      name: 'Test User'
    });

    await page.goto('/login');
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill(password);
    await page.getByRole('button', { name: 'Login' }).click();
    await expect(page).toHaveURL('/dashboard');

    // Reload page
    await page.reload();

    // Should still be logged in
    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByText('Welcome')).toBeVisible();
  });
});
```

**Post Creation Flow** (`tests/e2e/posts.spec.ts`):
```typescript
import { test, expect } from '@playwright/test';
import { setupAuthenticatedUser } from './helpers/auth';

test.describe('Post Creation Flow', () => {
  test('create → edit → delete post', async ({ page }) => {
    // Setup: Login as test user
    const { token } = await setupAuthenticatedUser(page);

    // Navigate to create post page
    await page.goto('/posts/new');

    // Fill post form
    const title = 'Integration Test Post';
    const content = 'This is a test post content created by E2E test.';

    await page.getByLabel('Title').fill(title);
    await page.getByLabel('Content').fill(content);
    await page.getByRole('button', { name: 'Publish' }).click();

    // Verify post created
    await expect(page).toHaveURL(/\/posts\/\w+/);
    await expect(page.getByRole('heading', { name: title })).toBeVisible();
    await expect(page.getByText(content)).toBeVisible();

    // Edit post
    await page.getByRole('button', { name: 'Edit' }).click();
    const updatedTitle = 'Updated Test Post';
    await page.getByLabel('Title').fill(updatedTitle);
    await page.getByRole('button', { name: 'Save' }).click();

    // Verify updated
    await expect(page.getByRole('heading', { name: updatedTitle })).toBeVisible();

    // Delete post
    await page.getByRole('button', { name: 'Delete' }).click();
    await page.getByRole('button', { name: 'Confirm' }).click();

    // Verify redirected and post gone
    await expect(page).toHaveURL('/posts');
    await expect(page.getByText(updatedTitle)).not.toBeVisible();
  });

  test('unauthorized user cannot create post', async ({ page }) => {
    // Don't login
    await page.goto('/posts/new');

    // Should redirect to login
    await expect(page).toHaveURL('/login');
  });
});
```

**Test Helpers** (`tests/e2e/helpers/database.ts`):
```typescript
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient({
  datasources: {
    db: {
      url: process.env.TEST_DATABASE_URL
    }
  }
});

export async function setupTestDB() {
  // Run migrations
  await prisma.$executeRaw`
    CREATE SCHEMA IF NOT EXISTS test;
  `;
}

export async function clearTestDB() {
  // Clean all test data
  await prisma.post.deleteMany();
  await prisma.user.deleteMany();
}

export async function createTestUser(data: {
  email: string;
  password: string;
  name: string;
}) {
  const hashedPassword = await hash(data.password);

  return prisma.user.create({
    data: {
      email: data.email,
      password_hash: hashedPassword,
      name: data.name,
      email_verified: true
    }
  });
}

export async function getVerificationToken(email: string): Promise<string> {
  // Fetch verification token from test DB
  const token = await prisma.verificationToken.findFirst({
    where: { email },
    orderBy: { created_at: 'desc' }
  });

  return token?.token || '';
}
```

**Test Helpers** (`tests/e2e/helpers/auth.ts`):
```typescript
import { Page } from '@playwright/test';
import { createTestUser } from './database';
import { generateTestEmail } from './utils';

export async function setupAuthenticatedUser(page: Page) {
  const email = generateTestEmail();
  const password = 'TestPass123!';
  const name = 'Test User';

  // Create user
  await createTestUser({ email, password, name });

  // Login via API to speed up test
  const response = await page.request.post('http://localhost:8000/api/auth/login', {
    data: { email, password }
  });

  const { access_token } = await response.json();

  // Set auth state
  await page.context().addCookies([
    {
      name: 'refresh_token',
      value: 'test-refresh-token',
      domain: 'localhost',
      path: '/',
      httpOnly: true,
      secure: false
    }
  ]);

  // Set access token in localStorage
  await page.addInitScript((token) => {
    localStorage.setItem('access_token', token);
  }, access_token);

  return { email, token: access_token };
}
```

**Utils** (`tests/e2e/helpers/utils.ts`):
```typescript
export function generateTestEmail(): string {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(7);
  return `test-${timestamp}-${random}@example.com`;
}

export async function waitForAPI(url: string, maxAttempts = 30) {
  for (let i = 0; i < maxAttempts; i++) {
    try {
      const response = await fetch(url);
      if (response.ok) return;
    } catch {}
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  throw new Error(`API not ready at ${url}`);
}
```

**CI/CD Integration** (`.github/workflows/e2e.yml`):
```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  e2e:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          npm ci
          cd apps/backend && pip install -r requirements.txt

      - name: Install Playwright browsers
        run: npx playwright install --with-deps

      - name: Setup test database
        run: |
          cd apps/backend
          python -m pip install pytest pytest-asyncio
          python -c "from database import init_db; init_db('test_db')"

      - name: Run E2E tests
        run: npx playwright test
        env:
          TEST_DATABASE_URL: postgresql://postgres:test@localhost:5432/test_db
          API_BASE_URL: http://localhost:8000

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 30
```

## Alternative Testing Frameworks

### Cypress Setup
```json
// cypress.config.ts
import { defineConfig } from 'cypress';

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    setupNodeEvents(on, config) {
      // Setup test database
      on('task', {
        async setupTestDB() {
          await setupTestDB();
          return null;
        },
        async clearTestDB() {
          await clearTestDB();
          return null;
        }
      });
    }
  }
});
```

```typescript
// cypress/e2e/auth.cy.ts
describe('Authentication Flow', () => {
  beforeEach(() => {
    cy.task('setupTestDB');
  });

  afterEach(() => {
    cy.task('clearTestDB');
  });

  it('should complete signup flow', () => {
    const email = `test-${Date.now()}@example.com`;
    const password = 'TestPass123!';

    cy.visit('/signup');
    cy.get('[data-testid="email"]').type(email);
    cy.get('[data-testid="password"]').type(password);
    cy.get('[data-testid="signup-button"]').click();

    cy.contains('Check your email for verification link').should('be.visible');
  });
});
```

## Mocking External Services

### Mock Server Setup
```typescript
// tests/e2e/mocks.ts
import { MockServer } from 'jest-mock-server';

export const mockServer = new MockServer({
  port: 9000
});

export const setupMocks = () => {
  // Mock payment gateway
  mockServer.http
    .post('/api/payment/process')
    .reply(200, { success: true, transaction_id: 'txn_123' });

  // Mock email service
  mockServer.http
    .post('/api/email/send')
    .reply(200, { success: true });

  // Mock external API
  mockServer.http
    .get('/api/external/data')
    .reply(200, { data: 'mocked' });
};
```

## Database Testing Patterns

### Test Data Factories
```typescript
// tests/factories/user.factory.ts
import { User } from '@prisma/client';

interface UserAttributes {
  email?: string;
  name?: string;
  password?: string;
}

export class UserFactory {
  static build(attributes: UserAttributes = {}): User {
    return {
      id: `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      email: attributes.email || `user_${Date.now()}@example.com`,
      name: attributes.name || 'Test User',
      password_hash: attributes.password || 'hashed_password',
      email_verified: false,
      created_at: new Date(),
      updated_at: new Date(),
      ...attributes
    };
  }

  static async create(attributes: UserAttributes = {}) {
    const userData = this.build(attributes);
    return await prisma.user.create({ data: userData });
  }
}
```

### Test Database Management
```typescript
// tests/database.setup.ts
import { execSync } from 'child_process';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export const setupTestDatabase = async () => {
  // Create test database
  execSync('npx prisma migrate reset --force', {
    env: { ...process.env, DATABASE_URL: process.env.TEST_DATABASE_URL }
  });

  // Run seeds if needed
  await execSync('node scripts/seed-test-db.js');
};

export const teardownTestDatabase = async () => {
  await prisma.$disconnect();
};
```

## Performance Optimization

### Parallel Test Execution
```typescript
// playwright.performance.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  workers: '50%', // Use half of available CPU cores
  fullyParallel: true,
  projects: [
    {
      name: 'chrome',
      use: { browserName: 'chromium' }
    },
    {
      name: 'firefox',
      use: { browserName: 'firefox' }
    },
    {
      name: 'webkit',
      use: { browserName: 'webkit' }
    }
  ]
});
```

### Test Isolation Strategies
```typescript
// tests/isolation.ts
export class TestIsolation {
  private static testId: string;

  static setup() {
    this.testId = `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    return this.testId;
  }

  static getIsolatedEmail(baseEmail: string) {
    const [username, domain] = baseEmail.split('@');
    return `${username}+${this.testId}@${domain}`;
  }

  static cleanup() {
    // Cleanup data specific to this test run
    return this.testId;
  }
}
```

## Reporting and Analytics

### Test Result Processing
```typescript
// scripts/process-test-results.ts
import fs from 'fs';
import path from 'path';

export const processTestResults = () => {
  const resultsPath = path.join(process.cwd(), 'test-results.json');
  const results = JSON.parse(fs.readFileSync(resultsPath, 'utf8'));

  const summary = {
    totalTests: results.tests.length,
    passedTests: results.tests.filter((t: any) => t.status === 'passed').length,
    failedTests: results.tests.filter((t: any) => t.status === 'failed').length,
    duration: results.stats.duration,
    timestamp: new Date().toISOString()
  };

  // Write summary for CI/CD
  fs.writeFileSync('test-summary.json', JSON.stringify(summary, null, 2));
};
```

## Best Practices
1. **Real user flows**: Test actual user journeys, not just individual components
2. **Isolated data**: Each test should have its own data scope
3. **Fast execution**: Optimize for speed with parallel execution
4. **Reliable tests**: Handle async operations properly
5. **Clear failures**: Provide helpful error messages
6. **External service mocking**: Don't rely on third-party services
7. **Database cleanup**: Clean up after each test run
8. **Visual regression**: Include visual testing for UI changes

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Current testing setup, UI framework, API structure, database schema |
| **Conversation** | User's specific testing requirements, key user flows, deployment setup |
| **Skill References** | E2E testing best practices, framework comparisons, CI/CD integration |
| **User Guidelines** | Project-specific testing policies, performance requirements, security needs |