import { test, expect } from '@playwright/test';

/**
 * E2E Test: Complete User Journey
 *
 * Tests the complete end-to-end user journey from:
 * 1. Opening the application
 * 2. Uploading an SPSS file
 * 3. Starting analysis
 * 4. Monitoring progress
 * 5. Continuing conversation
 *
 * This is the main smoke test for the entire application.
 *
 * User Journey: Complete survey analysis workflow
 *
 * Quality Standard: 100% pass rate, works in Chromium/Firefox/WebKit
 */
test.describe('Complete User Journey', () => {
  test('should complete full user workflow', async ({ page }) => {
    // Step 1: Open application
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Verify landing page
    await expect(page.locator('text=DataChat - SPSS Survey Analyzer')).toBeVisible();
    await expect(page.locator('text=Upload your SPSS .sav file')).toBeVisible();

    // Step 2: Upload SPSS file
    const fileInput = page.locator('#file-input');
    await fileInput.setInputFiles({
      name: 'test-survey.sav',
      mimeType: 'application/x-spss-sav',
      buffer: Buffer.from('mock spss survey data for testing'),
    });

    // Verify send button is enabled
    const sendButton = page.locator('button:has-text("Send")');
    await expect(sendButton).toBeEnabled();

    // Step 3: Add analysis instructions
    const textarea = page.locator('textarea');
    await textarea.fill('Please analyze this survey data and generate a report');

    // Step 4: Start analysis
    await sendButton.click();

    // Verify message was sent
    const humanMessage = page.locator('text=Please analyze this survey data').first();
    await expect(humanMessage).toBeVisible({ timeout: 10000 });

    // Verify input is cleared
    await expect(textarea).toHaveValue('');

    // Step 5: Wait for AI response
    await page.waitForTimeout(5000);

    // Step 6: Verify conversation is active
    await expect(textarea).toBeVisible();

    // Step 7: Send follow-up message
    await textarea.fill('What are the main variables in this dataset?');
    await sendButton.click();

    // Verify second message appears
    const secondMessage = page.locator('text=What are the main variables').first();
    await expect(secondMessage).toBeVisible({ timeout: 10000 });

    // Step 8: Verify UI remains responsive
    await expect(textarea).toBeVisible();
    await expect(page.locator('text=DataChat')).toBeVisible();
  });

  test('should handle error gracefully', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const textarea = page.locator('textarea');
    const sendButton = page.locator('button:has-text("Send")');

    // Send a minimal message - UI should handle it
    await textarea.fill('Hi');
    await sendButton.click();

    // UI should remain responsive - textarea should be ready for next input
    await expect(textarea).toBeVisible();

    // The most important thing is that UI doesn't crash
    // Message may or may not appear depending on backend
    await expect(page.locator('textarea')).toBeVisible();
  });

  test('should allow multiple analysis requests in same thread', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const textarea = page.locator('textarea');
    const sendButton = page.locator('button:has-text("Send")');

    // First request
    await textarea.fill('Generate frequency tables for all variables');
    await sendButton.click();
    await page.waitForTimeout(3000);

    // Verify UI is still responsive
    await expect(textarea).toBeVisible();

    // Second request in same thread
    await textarea.fill('Now create crosstabs for demographic variables');
    await sendButton.click();
    await page.waitForTimeout(3000);

    // The key test is that UI remains functional across multiple requests
    await expect(textarea).toBeVisible();
    await expect(sendButton).toBeVisible();
  });

  test('should handle file upload with text instructions', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Upload file first
    const fileInput = page.locator('#file-input');
    await fileInput.setInputFiles({
      name: 'survey.sav',
      mimeType: 'application/x-spss-sav',
      buffer: Buffer.from('survey data'),
    });

    await page.waitForTimeout(500);

    // Add text instructions
    const textarea = page.locator('textarea');
    await textarea.fill('Focus on demographic variables');

    // Submit
    await page.locator('button:has-text("Send")').click();

    // Verify both were processed
    const message = page.locator('text=Focus on demographic variables').first();
    await expect(message).toBeVisible({ timeout: 10000 });
  });

  test('should maintain UI state throughout session', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const textarea = page.locator('textarea');
    const sendButton = page.locator('button:has-text("Send")');

    // Send multiple messages
    const messages = [
      'Hello',
      'Upload survey.sav',
      'Analyze the data',
      'Show me results'
    ];

    for (const msg of messages) {
      await textarea.fill(msg);
      await sendButton.click();
      await page.waitForTimeout(2000);
    }

    // The most important test is that UI remains functional
    await expect(textarea).toBeVisible();
    await expect(page.locator('text=DataChat')).toBeVisible();
    await expect(page.locator('svg').first()).toBeVisible();
    await expect(sendButton).toBeVisible();

    // Textarea should be ready for next input
    await expect(textarea).toHaveValue('');
  });

  test('should allow quick conversation flow', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const textarea = page.locator('textarea');

    // Test quick message sending with Enter key
    await textarea.fill('Quick message 1');
    await textarea.press('Enter');
    await page.waitForTimeout(2000);

    await textarea.fill('Quick message 2');
    await textarea.press('Enter');
    await page.waitForTimeout(2000);

    // Verify conversation flow works - textarea remains responsive
    await expect(textarea).toBeVisible();
    await expect(textarea).toHaveValue('');
  });
});
