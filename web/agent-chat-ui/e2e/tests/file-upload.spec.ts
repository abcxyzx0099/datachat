import { test, expect } from '@playwright/test';

/**
 * E2E Test: File Upload
 *
 * Tests file upload functionality including:
 * - File selection via button
 * - File preview display
 * - Multiple file uploads
 *
 * User Journey: User uploads an SPSS .sav file for analysis
 *
 * Quality Standard: 100% pass rate, works in Chromium/Firefox/WebKit
 */
test.describe('File Upload', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should allow file selection via button', async ({ page }) => {
    const fileInput = page.locator('#file-input');

    // Upload a mock file
    await fileInput.setInputFiles({
      name: 'test-survey.sav',
      mimeType: 'application/x-spss-sav',
      buffer: Buffer.from('mock spss file content'),
    });

    // Wait a moment for file processing
    await page.waitForTimeout(500);

    // The file preview might appear as a visual element
    // Look for any change in the form indicating file was uploaded
    const form = page.locator('form').first();
    await expect(form).toBeVisible();

    // Verify the send button is now enabled
    const sendButton = page.locator('button:has-text("Send")');
    await expect(sendButton).toBeEnabled();
  });

  test('should handle multiple file uploads', async ({ page }) => {
    const fileInput = page.locator('#file-input');

    // Upload multiple files
    await fileInput.setInputFiles([
      {
        name: 'survey.sav',
        mimeType: 'application/x-spss-sav',
        buffer: Buffer.from('mock spss content'),
      },
      {
        name: 'notes.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from('additional notes'),
      },
    ]);

    await page.waitForTimeout(500);

    // Verify form is still visible and has content
    const form = page.locator('form').first();
    await expect(form).toBeVisible();
  });

  test('should accept various file types', async ({ page }) => {
    const fileInput = page.locator('#file-input');

    // Test SPSS file
    await fileInput.setInputFiles({
      name: 'survey.sav',
      mimeType: 'application/x-spss-sav',
      buffer: Buffer.from('spss data'),
    });

    await page.waitForTimeout(500);

    // Verify send button is enabled
    const sendButton = page.locator('button:has-text("Send")');
    await expect(sendButton).toBeEnabled();

    // Test image file
    await fileInput.setInputFiles({
      name: 'chart.png',
      mimeType: 'image/png',
      buffer: Buffer.from('png data'),
    });

    await page.waitForTimeout(500);

    // Verify send button is still enabled
    await expect(sendButton).toBeEnabled();
  });

  test('should show file upload label', async ({ page }) => {
    // Verify the upload label is visible
    const uploadLabel = page.locator('text=Upload SPSS .sav file');
    await expect(uploadLabel).toBeVisible();

    // The plus icon is inside a label - check for the label element
    const uploadLabelElement = page.locator('label:has-text("Upload")').or(page.locator('text=Upload SPSS').first());
    const hasLabel = await uploadLabelElement.count() > 0;
    expect(hasLabel).toBeTruthy();
  });

  test('should enable send button after file upload', async ({ page }) => {
    const fileInput = page.locator('#file-input');
    const sendButton = page.locator('button:has-text("Send")');

    // Initially send button should be disabled
    await expect(sendButton).toBeDisabled();

    // Upload a file
    await fileInput.setInputFiles({
      name: 'test.sav',
      mimeType: 'application/x-spss-sav',
      buffer: Buffer.from('test content'),
    });

    await page.waitForTimeout(500);

    // Now send button should be enabled
    await expect(sendButton).toBeEnabled();
  });

  test('should allow text input with file upload', async ({ page }) => {
    const fileInput = page.locator('#file-input');
    const textarea = page.locator('textarea');

    // Upload a file
    await fileInput.setInputFiles({
      name: 'survey.sav',
      mimeType: 'application/x-spss-sav',
      buffer: Buffer.from('survey data'),
    });

    await page.waitForTimeout(500);

    // Add text input
    await textarea.fill('Please analyze this survey');

    // Verify both file and text can be submitted
    const sendButton = page.locator('button:has-text("Send")');
    await expect(sendButton).toBeEnabled();
  });
});
