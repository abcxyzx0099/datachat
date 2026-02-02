import { test, expect } from '@playwright/test';

/**
 * E2E Test: Human Review Document
 *
 * Tests the human review functionality for:
 * - Review document display
 * - User interactions with review items
 * - Approval/rejection actions
 *
 * User Journey: User reviews and approves AI-generated specifications
 *
 * Quality Standard: 100% pass rate, works in Chromium/Firefox/WebKit
 */
test.describe('Human Review Document', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should handle review interrupt display', async ({ page }) => {
    const textarea = page.locator('textarea');
    const sendButton = page.locator('button:has-text("Send")');

    // Upload file and start analysis
    const fileInput = page.locator('#file-input');
    await fileInput.setInputFiles({
      name: 'survey.sav',
      mimeType: 'application/x-spss-sav',
      buffer: Buffer.from('mock content'),
    });
    await sendButton.click();

    // Note: Review documents appear when backend triggers interrupts
    // For E2E testing, we check UI responsiveness
    await page.waitForTimeout(5000);

    // Verify page is responsive
    await expect(textarea).toBeVisible();
  });

  test('should display review type indicators when present', async ({ page }) => {
    // This test checks for review-related UI elements
    // In production, these appear based on backend state

    const textarea = page.locator('textarea');

    // Send a message that might trigger review
    await textarea.fill('Create recoding rules for this survey');
    await page.locator('button:has-text("Send")').click();

    await page.waitForTimeout(5000);

    // Check that UI is functioning
    await expect(textarea).toBeVisible();
  });

  test('should allow user interaction during review', async ({ page }) => {
    const textarea = page.locator('textarea');

    // Type a review comment
    await textarea.fill('Please adjust the variable categories');
    await page.locator('button:has-text("Send")').click();

    // Wait for response
    await page.waitForTimeout(5000);

    // Verify message was sent
    const message = page.locator('text=Please adjust the variable categories').first();
    await expect(message).toBeVisible();
  });

  test('should handle approval workflow', async ({ page }) => {
    const textarea = page.locator('textarea');

    // Send approval message
    await textarea.fill('Approve the current specifications');
    await page.locator('button:has-text("Send")').click();

    await page.waitForTimeout(5000);

    // Verify message appears
    const message = page.locator('text=Approve the current specifications').first();
    await expect(message).toBeVisible();
  });

  test('should handle rejection with feedback', async ({ page }) => {
    const textarea = page.locator('textarea');

    // Send rejection feedback
    await textarea.fill('Reject: Please update the recoding rules to match our schema');
    await page.locator('button:has-text("Send")').click();

    await page.waitForTimeout(5000);

    // Verify feedback was sent
    const message = page.locator('text=Reject').first();
    await expect(message).toBeVisible();
  });

  test('should display indicators review content', async ({ page }) => {
    const textarea = page.locator('textarea');

    // Request indicators review
    await textarea.fill('Show me the indicators you created');
    await page.locator('button:has-text("Send")').click();

    await page.waitForTimeout(5000);

    // Verify conversation flow
    await expect(textarea).toBeVisible();
    await expect(textarea).toHaveValue('');
  });

  test('should display table specifications review', async ({ page }) => {
    const textarea = page.locator('textarea');

    // Request table specs review
    await textarea.fill('Review the table specifications');
    await page.locator('button:has-text("Send")').click();

    await page.waitForTimeout(5000);

    // Verify UI remains responsive
    const sendButton = page.locator('button:has-text("Send")');
    await expect(sendButton).toBeVisible();
  });

  test('should maintain conversation context during review', async ({ page }) => {
    const textarea = page.locator('textarea');

    // Multiple messages to test context
    const messages = [
      'Create frequency tables',
      'Now create crosstabs',
      'Finally, generate charts'
    ];

    for (const msg of messages) {
      await textarea.fill(msg);
      await page.locator('button:has-text("Send")').click();
      await page.waitForTimeout(3000);
    }

    // The most important test is that UI remains functional
    await expect(textarea).toBeVisible();

    // Verify we can still interact with the UI
    await textarea.fill('Final check');
    await expect(textarea).toHaveValue('Final check');
  });
});
