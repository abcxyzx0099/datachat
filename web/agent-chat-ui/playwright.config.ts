import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright E2E Test Configuration for DataChat
 *
 * This configuration sets up browser-based end-to-end testing for the
 * DataChat frontend UI, testing user journeys like file upload,
 * chat interactions, workflow progress, and output file downloads.
 *
 * Run tests:
 *   npx playwright test
 *
 * Run with UI:
 *   npx playwright test --ui
 *
 * Run in debug mode:
 *   npx playwright test --debug
 *
 * Run specific test file:
 *   npx playwright test e2e/tests/file-upload.spec.ts
 *
 * Run on specific browser:
 *   npx playwright test --project=chromium
 */
export default defineConfig({
  testDir: './e2e/tests',
  fullyParallel: false, // Run sequentially to avoid port conflicts
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1, // Single worker to avoid conflicts
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['list'],
  ],

  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 10000,
    navigationTimeout: 30000,
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },

    /* Test against mobile viewports */
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  /* Run your local dev server before starting the tests */
  webServer: {
    command: 'pnpm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
});
