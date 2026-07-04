import { test, expect } from '@playwright/test';

// Regression test for the password-reset redirect bug.
//
// A user who forgot their password is logged out. On any page load the app's
// AuthContext probes GET /profile/ to see if someone is authenticated. For a
// logged-out visitor that returns 401, and the axios interceptor used to react
// by attempting a token refresh (also 401) and then force-navigating to /login.
// The result: the visitor reached /reset-password and was immediately bounced
// to /login, unable to set a new password.
//
// These mocks reproduce the exact backend responses an unauthenticated visitor
// gets, so the test fails if the auto-redirect behavior ever comes back.
test.describe('password reset page', () => {
  test.beforeEach(async ({ page }) => {
    // Unauthenticated backend: the auth probe and the refresh both 401.
    await page.route('**/api/v1/users/profile/', (route) =>
      route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Authentication credentials were not provided.' }),
      })
    );
    await page.route('**/api/v1/users/token/refresh/', (route) =>
      route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'No refresh token cookie found.' }),
      })
    );
  });

  test('logged-out visitor is not redirected away from the reset link', async ({ page }) => {
    await page.goto('/reset-password/testuid/testtoken');

    // The reset form renders...
    await expect(page.locator('h2')).toContainText('Reset Password');
    await expect(page.locator('input#password')).toBeVisible();

    // ...and it stays put after the async auth bootstrap has had time to run.
    // Before the fix, the interceptor would force window.location -> /login here.
    await page.waitForTimeout(1500);
    await expect(page).toHaveURL(/\/reset-password\//);
    await expect(page.locator('input#password')).toBeVisible();
  });
});
