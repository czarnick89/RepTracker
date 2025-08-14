from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    RegisterView,
    VerifyEmailView,
    ResendVerificationEmailView,
    LogoutView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    ChangePasswordView,
    UserProfileView,
    MyTokenObtainPairView,
    CookieTokenRefreshView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/<uidb64>/<token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('resend-verification/', ResendVerificationEmailView.as_view(), name='resend-verification'),
]