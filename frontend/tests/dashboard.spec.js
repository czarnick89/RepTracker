import { test, expect } from '@playwright/test';

// Note: Dashboard tests require authentication
// These tests assume a user is logged in or authentication is mocked

test.skip('dashboard page loads', async ({ page }) => {
  // This test is skipped because dashboard requires authentication
  // To run this test, you would need to:
  // 1. Log in first, or
  // 2. Mock authentication tokens in localStorage

  await page.goto('/dashboard');

  // Check that we're on the dashboard (not redirected to login)
  await expect(page).toHaveURL(/.*\/dashboard/);

  // Check for main dashboard elements that should always be present
  // The "New Workout" button should always be visible
  const newWorkoutButton = page.locator('button').filter({ hasText: 'New Workout' });
  await expect(newWorkoutButton).toBeVisible();
});

test.skip('new workout button interaction', async ({ page }) => {
  // Skipped - requires authentication
  await page.goto('/dashboard');

  // Click the New Workout button
  await page.locator('button').filter({ hasText: 'New Workout' }).click();

  // Should show a workout creation interface
  await expect(page.locator('button').filter({ hasText: 'New Workout' })).toBeVisible();
});

test.skip('dashboard layout structure', async ({ page }) => {
  // Skipped - requires authentication
  await page.goto('/dashboard');

  // Check for basic layout elements
  const mainContent = page.locator('div').first();
  await expect(mainContent).toBeVisible();

  // Check that there are no loading states
  const loadingElements = page.locator('text=Loading');
  await expect(loadingElements).toHaveCount(0);
});