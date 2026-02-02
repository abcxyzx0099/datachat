import { test, expect } from '@playwright/test';

/**
 * E2E Test: Initial Page Load
 *
 * Tests that the DataChat application loads correctly and displays
 * the initial landing page with all expected elements.
 *
 * User Journey: User opens the application for the first time
 *
 * Quality Standard: 100% pass rate, works in Chromium/Firefox/WebKit
 */
test.describe('Initial Page Load', () => {
  test('should display landing page with title and upload prompt', async ({ page }) => {
    // Navigate to the application
    await page.goto('/');

    // Wait for page to load
    await page.waitForLoadState('networkidle');

    // Verify the main title is visible
    await expect(page.locator('text=DataChat - SPSS Survey Analyzer')).toBeVisible();

    // Verify the upload prompt is visible
    await expect(
      page.locator('text=Upload your SPSS .sav file to automatically generate analysis reports')
    ).toBeVisible();

    // Verify the chat input area is visible
    await expect(page.locator('textarea')).toBeVisible();

    // Verify the file upload button is visible
    await expect(page.locator('text=Upload SPSS .sav file')).toBeVisible();

    // Verify the send button is disabled (no input)
    const sendButton = page.locator('button:has-text("Send")');
    await expect(sendButton).toBeDisabled();
  });

  test('should display DataChat branding', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Verify LangGraph/DataChat logo (svg element)
    const logo = page.locator('svg').first();
    await expect(logo).toBeVisible();
  });

  test('should have GitHub link', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Verify GitHub link exists
    const githubLink = page.locator('a[href*="github"]').first();
    await expect(githubLink).toBeVisible();
  });

  test('should have hide tool calls toggle', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Verify the hide tool calls switch exists
    const hideToolCallsLabel = page.locator('text=Hide Tool Calls');
    await expect(hideToolCallsLabel).toBeVisible();
  });

  test('should have new thread button available', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Initially, new thread button is not visible (no chat started)
    // Check for button with text "New thread" - should not exist initially
    const newThreadButton = page.locator('button:has-text("New thread")');
    const isVisible = await newThreadButton.count() > 0;
    expect(isVisible).toBeFalsy();
  });
});
