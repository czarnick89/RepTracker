import pytest
from django.contrib.auth import get_user_model
from users.serializers import UserRegisterSerializer, UserProfileSerializer

User = get_user_model()

@pytest.mark.django_db
def test_password_too_short():
    """Test password validation - too short."""
    serializer = UserRegisterSerializer(data={
        'email': 'test@example.com',
        'password': '12345'  # Too short
    })
    assert not serializer.is_valid()
    assert 'password' in serializer.errors
    assert 'at least 8 characters' in str(serializer.errors['password']).lower()

@pytest.mark.django_db
def test_password_too_weak():
    """Test password validation - too weak (common password)."""
    serializer = UserRegisterSerializer(data={
        'email': 'test@example.com',
        'password': 'password123'  # Common password
    })
    assert not serializer.is_valid()
    assert 'password' in serializer.errors

@pytest.mark.django_db
def test_duplicate_email_case_insensitive():
    """Test duplicate email validation (case insensitive)."""
    # Create existing user
    User.objects.create_user(email='existing@example.com', password='test123')

    # Try to register with same email in different case
    serializer = UserRegisterSerializer(data={
        'email': 'EXISTING@EXAMPLE.COM',
        'password': 'validpass123'
    })
    assert not serializer.is_valid()
    assert 'email' in serializer.errors
    assert 'already exists' in str(serializer.errors['email']).lower()

@pytest.mark.django_db
def test_invalid_email_format():
    """Test invalid email format validation."""
    serializer = UserRegisterSerializer(data={
        'email': 'invalid-email',
        'password': 'validpass123'
    })
    assert not serializer.is_valid()
    assert 'email' in serializer.errors

@pytest.mark.django_db
def test_valid_registration():
    """Test valid registration data."""
    serializer = UserRegisterSerializer(data={
        'email': 'valid@example.com',
        'password': 'StrongPass123!'
    })
    assert serializer.is_valid()
    user = serializer.save()
    assert user.email == 'valid@example.com'
    assert not user.is_active  # Should be inactive until email verification

@pytest.mark.django_db
def test_blank_first_name():
    """Test blank first name validation."""
    user = User.objects.create_user(email='test@example.com', password='test123')
    serializer = UserProfileSerializer(user, data={
        'first_name': '',
        'last_name': 'Doe'
    })
    assert not serializer.is_valid()
    assert 'first_name' in serializer.errors

@pytest.mark.django_db
def test_blank_last_name():
    """Test blank last name validation."""
    user = User.objects.create_user(email='test@example.com', password='test123')
    serializer = UserProfileSerializer(user, data={
        'first_name': 'John',
        'last_name': ''
    })
    assert not serializer.is_valid()
    assert 'last_name' in serializer.errors

@pytest.mark.django_db
def test_valid_profile_update():
    """Test valid profile update."""
    user = User.objects.create_user(email='test@example.com', password='test123')
    serializer = UserProfileSerializer(user, data={
        'first_name': 'John',
        'last_name': 'Doe'
    })
    assert serializer.is_valid()
    updated_user = serializer.save()
    assert updated_user.first_name == 'John'
    assert updated_user.last_name == 'Doe'

@pytest.mark.django_db
def test_read_only_fields():
    """Test that email and id are read-only."""
    user = User.objects.create_user(email='test@example.com', password='test123')
    serializer = UserProfileSerializer(user, data={
        'email': 'newemail@example.com',
        'id': 999,
        'first_name': 'John',
        'last_name': 'Doe'
    })
    assert serializer.is_valid()
    # Email should not be in validated_data since it's read-only
    assert 'email' not in serializer.validated_data
    assert 'id' not in serializer.validated_data
    # But the instance should still have the original email
    assert serializer.instance.email == 'test@example.com'