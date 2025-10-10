import { test, expect } from '@playwright/test';

test('login page loads', async ({ page }) => {
  await page.goto('/login');

  // Check main heading
  await expect(page.locator('h2')).toContainText('RepTracker Login');

  // Check form elements
  await expect(page.locator('input#email')).toBeVisible();
  await expect(page.locator('input#password')).toBeVisible();
  await expect(page.locator('button[type="submit"]')).toContainText('Log In');
});

test('login form interaction', async ({ page }) => {
  await page.goto('/login');

  // Fill form fields
  await page.locator('input#email').fill('test@example.com');
  await page.locator('input#password').fill('password123');

  // Verify values
  await expect(page.locator('input#email')).toHaveValue('test@example.com');
  await expect(page.locator('input#password')).toHaveValue('password123');
});

test('navigation links', async ({ page }) => {
  await page.goto('/login');

  // Check forgot password link
  const forgotLink = page.locator('a').filter({ hasText: 'Forgot Password?' });
  await expect(forgotLink).toHaveAttribute('href', '/forgot-password');

  // Check register link
  const registerLink = page.locator('a').filter({ hasText: 'Create Account' });
  await expect(registerLink).toHaveAttribute('href', '/register');
});

test('register link navigation', async ({ page }) => {
  await page.goto('/login');

  // Click register link
  await page.locator('a').filter({ hasText: 'Create Account' }).click();

  // Wait for the heading to change (SPA navigation)
  await expect(page.locator('h2')).toContainText('RepTracker Register');
});