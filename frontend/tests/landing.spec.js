import { test, expect } from '@playwright/test';

test('landing page loads', async ({ page }) => {
  await page.goto('/');

  // Check main heading
  await expect(page.locator('h1')).toContainText('Welcome to RepTracker');

  // Check subtitle
  await expect(page.locator('p')).toContainText('Track your workouts');

  // Check Get Started button
  const getStartedButton = page.locator('a').filter({ hasText: 'Get Started' });
  await expect(getStartedButton).toBeVisible();
  await expect(getStartedButton).toHaveAttribute('href', '/login');
});

test('get started button navigates to login', async ({ page }) => {
  await page.goto('/');

  // Click the Get Started button
  await page.locator('a').filter({ hasText: 'Get Started' }).click();

  // Should navigate to login page
  await expect(page).toHaveURL(/.*\/login/);
  await expect(page.locator('h2')).toContainText('Login');
});