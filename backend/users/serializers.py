# Django imports
from django.contrib.auth import get_user_model
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _

# Third-party imports
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings

User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['email', 'password']

    def validate_password(self, value):
        try:
            validate_password(value, user=self.instance)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(_("A user with that email already exists."))
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False
        )
        return user

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def validate(self, attrs):
        data = super().validate(attrs)

        if not self.user.is_active:
            raise serializers.ValidationError("Account not verified.")

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data 
    
class UserProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(allow_blank=False)
    last_name = serializers.CharField(allow_blank=False)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name'] 
        read_only_fields = ['id', 'email']