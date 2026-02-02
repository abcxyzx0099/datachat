import { test as base } from '@playwright/test';

/**
 * E2E Test Fixtures for DataChat
 *
 * Provides custom fixtures for common testing scenarios like
 * authenticated sessions, file uploads, and test data.
 */

export interface DataChatFixtures {
  mockHomePage: () => Promise<void>;
  uploadTestFile: (fileName: string) => Promise<void>;
  waitForAnalysisComplete: () => Promise<void>;
}

export const test = base.extend<DataChatFixtures>({
  mockHomePage: async ({ page }, use) => {
    const mockFn = async () => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');
    };
    await use(mockFn);
  },

  uploadTestFile: async ({ page }, use) => {
    const uploadFn = async (fileName: string) => {
      const fileInput = page.locator('#file-input');
      await fileInput.setInputFiles({
        name: fileName,
        mimeType: 'application/x-spss-sav',
        buffer: Buffer.from('mock spss file content for testing'),
      });
      // Wait a moment for file to be processed
      await page.waitForTimeout(500);
    };
    await use(uploadFn);
  },

  waitForAnalysisComplete: async ({ page }, use) => {
    const waitFn = async () => {
      // Wait for workflow progress to complete
      await page.waitForTimeout(3000);
    };
    await use(waitFn);
  },
});

export { expect } from '@playwright/test';
