import { test, expect } from '@playwright/test';

test('has title', async ({ page }) => {
  await page.goto('/');

  // Expect a title "to contain" a substring.
  await expect(page).toHaveTitle(/RepTracker/);
});

test('register page loads', async ({ page }) => {
  await page.goto('/register');

  // Wait for the page to load and check URL
  await expect(page).toHaveURL(/.*\/register/);

  // Check if the register form is present
  await expect(page.locator('h2')).toContainText('RepTracker Register');
  await expect(page.locator('input#email')).toBeVisible();
  await expect(page.locator('input#password')).toBeVisible();
  await expect(page.locator('input#confirmPassword')).toBeVisible();
});

test('password validation indicators', async ({ page }) => {
  await page.goto('/register');

  const passwordInput = page.locator('input#password');

  // Initially, indicators should show neutral circles
  await expect(page.locator('text=○ At least 8 characters')).toBeVisible();
  await expect(page.locator('text=○ Not entirely numeric')).toBeVisible();

  // Type a short password
  await passwordInput.fill('123');
  await expect(page.locator('text=✗ At least 8 characters')).toBeVisible();
  await expect(page.locator('text=✗ Not entirely numeric')).toBeVisible();

  // Type a valid password
  await passwordInput.fill('password123');
  await expect(page.locator('text=✓ At least 8 characters')).toBeVisible();
  await expect(page.locator('text=✓ Not entirely numeric')).toBeVisible();

  // Clear and type entirely numeric - make sure we don't submit
  await passwordInput.clear();
  await passwordInput.fill('123456789');
  // Wait a bit for validation to update
  await page.waitForTimeout(100);
  await expect(page.locator('text=✓ At least 8 characters')).toBeVisible();
  await expect(page.locator('text=✗ Not entirely numeric')).toBeVisible();
});

test('password visibility toggle', async ({ page }) => {
  await page.goto('/register');

  const passwordInput = page.locator('input#password');
  // Target the button inside the password input's parent div
  const toggleButton = page.locator('input#password').locator('xpath=ancestor::div[1]//button');

  // Initially password is hidden
  await expect(passwordInput).toHaveAttribute('type', 'password');

  // Click show
  await toggleButton.click();
  await expect(passwordInput).toHaveAttribute('type', 'text');

  // Click hide
  await toggleButton.click();
  await expect(passwordInput).toHaveAttribute('type', 'password');
});

test('password match indicator', async ({ page }) => {
  await page.goto('/register');

  const passwordInput = page.locator('input#password');
  const confirmInput = page.locator('input#confirmPassword');

  // Type password first
  await passwordInput.fill('password123');
  await confirmInput.fill('password123');

  // Should show match
  await expect(page.locator('text=✓ Passwords match')).toBeVisible();

  // Type mismatch
  await confirmInput.fill('different');
  await expect(page.locator('text=✓ Passwords match')).not.toBeVisible();
});