# Django imports
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

# Third-party imports
from rest_framework import status as s
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Local imports
from .serializers import (
    UserRegisterSerializer,
    UserProfileSerializer,
    MyTokenObtainPairSerializer,
)

# ---------------------------
# Model reference
# ---------------------------
User = get_user_model()

# ===========================
# User Registration and Email Verification
# ===========================
class RegisterView(APIView):
    """
    Registers a new user and sends an email verification link.
    
    POST data:
    - email
    - password
    - (other fields handled by UserRegisterSerializer)
    
    Side effects:
    - Creates inactive user in DB
    - Sends verification email with UID + token link
    """
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            link = f"{settings.BACKEND_URL}/api/v1/users/verify-email/{uid}/{token}/"
            send_mail(
                subject="Verify your email",
                message=f"Click the link to verify your account: {link}",
                from_email="noreply@reptracker.com",
                recipient_list=[user.email],
                fail_silently=False,
            )
            return Response({"detail": "Check your email to verify your account."}, status=s.HTTP_201_CREATED)
        return Response(serializer.errors, status=s.HTTP_400_BAD_REQUEST)
    
class VerifyEmailView(APIView):
    """
    Handles verification link clicks from the email.
    
    GET parameters:
    - uidb64: Base64-encoded user ID
    - token: email verification token
    
    Side effect:
    - Activates user account if token is valid
    - Redirects to frontend login page with query param
    """
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return redirect(f"{settings.FRONTEND_URL}/register/?verified=invalid")
        
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return redirect(f"{settings.FRONTEND_URL}/login/?verified=true")

        return redirect(f"{settings.FRONTEND_URL}/login/?verified=expired") 

# ===========================
# JWT Authentication (Login / Logout / Refresh)
# ===========================
class MyTokenObtainPairView(TokenObtainPairView):  
    """
    Handles user login and sets HttpOnly JWT cookies.
    """
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh = serializer.validated_data['refresh']
        access = serializer.validated_data['access']

        user = serializer.user  
        user.last_login = timezone.now()  
        user.save(update_fields=['last_login']) 

        response = Response({"detail": "Login successful"}, status=s.HTTP_200_OK)

        response.set_cookie(
            key='access_token',
            value=access,
            httponly=True,
            secure=True,    
            samesite='None',    
            max_age=15 * 60,
            path='/',
        )

        response.set_cookie(
            key='refresh_token',
            value=refresh,
            httponly=True,
            secure=True,       
            samesite='None',   
            max_age=24 * 60 * 60,
            path='/api/v1/users/',
        )

        return response
    
class LogoutView(APIView):
    """
    Logs out a user by blacklisting refresh token and deleting cookies.
    """
    permission_classes = [AllowAny]  

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass  

        response = Response({"detail": "Logged out successfully."}, status=s.HTTP_200_OK)
        response.delete_cookie("access_token", path='/')
        response.delete_cookie("refresh_token", path='/api/v1/users/')
        return response

class CookieTokenRefreshView(TokenRefreshView):
    """
    Refresh JWT access token using HttpOnly refresh token cookie.
    """
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token is None:
            return Response({"error": "No refresh token cookie found."}, status=s.HTTP_401_UNAUTHORIZED)

        data = {'refresh': refresh_token}
        serializer = self.get_serializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response({"error": "Invalid refresh token."}, status=s.HTTP_401_UNAUTHORIZED)

        access_token = serializer.validated_data['access']
        new_refresh_token = serializer.validated_data.get('refresh', None) 

        response = Response({"detail": "Token refreshed successfully."}, status=s.HTTP_200_OK)

        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=True,  
            samesite='None',  
            max_age=15 * 60,  # 15 minutes
            path='/',
        )

        # Rotate refresh token cookie if provided
        if new_refresh_token:
            response.set_cookie(
                key='refresh_token',
                value=new_refresh_token,
                httponly=True,
                secure=True,  
                samesite='None',
                max_age=24 * 60 * 60,  # 1 day
                path='/api/v1/users/',
            )

        return response

# ===========================
# Password Reset / Change
# ===========================
class PasswordResetRequestView(APIView):
    """
    Sends a password reset email if the user exists.
    """
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required."}, status=s.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                return Response({"error": "Inactive account."}, status=s.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            # To prevent enumeration, still return 200
            return Response({"detail": "If that email is registered, a reset link has been sent."})

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/" 

        send_mail(
            subject="Reset your RepTracker password",
            message=f"Use the following link to reset your password:\n\n{reset_link}",
            from_email="noreply@reptracker.com",
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response({"detail": "If that email is registered, a reset link has been sent."})
    
class PasswordResetConfirmView(APIView):
    """
    Confirms password reset using token, validates new password, and sets it.
    """
    def post(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError): 
            return Response({"error": "Invalid link."}, status=s.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token."}, status=s.HTTP_400_BAD_REQUEST)

        new_password = request.data.get("password")
        if not new_password:
            return Response({"error": "Password is required."}, status=s.HTTP_400_BAD_REQUEST)

        try:
            validate_password(new_password, user=user)
        except ValidationError as e:
            return Response({"error": e.messages}, status=s.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"detail": "Password has been reset successfully."}, status=s.HTTP_200_OK)
    
class ChangePasswordView(APIView):
    """
    Authenticated user can change password by providing old and new passwords.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not user.check_password(old_password):
            return Response({"error": "Old password is incorrect."}, status=s.HTTP_400_BAD_REQUEST)
        
        if not new_password:
            return Response({"error": "New password is required."}, status=s.HTTP_400_BAD_REQUEST)

        try:
            validate_password(new_password, user=user)
        except ValidationError as e:
            return Response({"error": e.messages}, status=s.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"detail": "Password changed successfully."}, status=s.HTTP_200_OK)

# ===========================
# User Profile
# ===========================    
class UserProfileView(APIView):
    """
    Retrieve or update authenticated user's profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=s.HTTP_400_BAD_REQUEST)

# ===========================
# Resend Verification Email - CURRENTLY UNUSED?
# ===========================
class ResendVerificationEmailView(APIView):
    """
    Resends email verification link to inactive users.
    """
    def post(self, request):
        email = request.data.get("email", "").strip()
        if not email:
            return Response({"email": "Email is required."}, status=s.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({"email": "User with this email does not exist."}, status=s.HTTP_404_NOT_FOUND)

        if user.is_active:
            return Response({"detail": "This account is already verified."}, status=s.HTTP_400_BAD_REQUEST)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        link = f"{settings.BACKEND_URL}/api/v1/users/verify-email/{uid}/{token}/"

        send_mail(
            subject="Verify your email",
            message=f"Click the link to verify your account: {link}",
            from_email="noreply@reptracker.com",
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response({"detail": "Verification email resent. Check your inbox."}, status=s.HTTP_200_OK)
    


