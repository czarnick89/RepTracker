import pytest
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from django.urls import reverse

@pytest.mark.django_db
def test_logout(authenticated_client, verified_user):
    # Ensure token exists for the verified user
    token, created = Token.objects.get_or_create(user=verified_user)
    token_key = token.key  # Save the token key before logout

    url = reverse('logout')  # Adjust if your logout route name differs
    response = authenticated_client.post(url)

    assert response.status_code == 200
    assert response.data.get("detail", "").lower() == "logged out successfully."

    # Assert the token was deleted
    assert not Token.objects.filter(key=token_key).exists()

    # Try to use the old token to access a protected endpoint; should fail
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + token_key)
    protected_url = reverse('logout')  # Or replace with another protected route
    resp2 = client.get(protected_url)
    assert resp2.status_code == 401
