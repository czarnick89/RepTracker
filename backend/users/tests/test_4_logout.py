import pytest
from django.urls import reverse
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_logout_success(api_client, verified_user, settings):
    # Disable throttling for this test
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['login'] = None

    # First, login to get JWT cookies set
    login_url = reverse('token_obtain_pair')
    login_data = {"email": verified_user.email, "password": "strongpassword123"}
    login_response = api_client.post(login_url, login_data)

    assert login_response.status_code == 200
    assert "access_token" in login_response.cookies
    assert "refresh_token" in login_response.cookies

    # Now test logout with the cookies set
    logout_url = reverse('logout')
    logout_response = api_client.post(logout_url)

    assert logout_response.status_code == 200
    assert logout_response.data["detail"] == "Logged out successfully."

    # Check that cookies are deleted/cleared
    # Django's delete_cookie sets the cookie to empty value
    assert logout_response.cookies.get('access_token', {}).get('value', '') == ''
    assert logout_response.cookies.get('refresh_token', {}).get('value', '') == ''

@pytest.mark.django_db
def test_logout_without_cookies(api_client):
    # Test logout without any cookies set
    url = reverse('logout')
    response = api_client.post(url)

    assert response.status_code == 200
    assert response.data["detail"] == "Logged out successfully."
