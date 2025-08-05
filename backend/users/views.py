from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as s
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from .serializers import UserRegisterSerializer, UserProfileSerializer
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.views import exception_handler
from rest_framework.throttling import ScopedRateThrottle
from .throttles import LoginThrottle

User = get_user_model()

# Create your views here.
class RegisterView(APIView):
    
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            domain = get_current_site(request).domain
            link = f"http://{domain}/verify-email/{uid}/{token}/"
            send_mail(
                subject="Verify your email",
                message=f"Click the link to verify your account: {link}",
                from_email="noreply@reptrack.com",
                recipient_list=[user.email],
                fail_silently=False,
            )
            return Response({"detail": "Check your email to verify your account."}, status=s.HTTP_201_CREATED)
        return Response(serializer.errors, status=s.HTTP_400_BAD_REQUEST)
    
class VerifyEmailView(APIView):
    
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response({"error": "Invalid link"}, status=s.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"detail": "Email verified. You can now log in."}, status=s.HTTP_200_OK)
        return Response({"error": "Invalid or expired token"}, status=s.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    
    throttle_classes = [LoginThrottle]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, username=email, password=password)
        if user is not None:
            if user.is_active:
                token, created = Token.objects.get_or_create(user=user)
                return Response({"token": token.key}, status=s.HTTP_200_OK)
            else:
                return Response({"error": "Account not verified."}, status=s.HTTP_403_FORBIDDEN)
        return Response({"error": "Invalid credentials."}, status=s.HTTP_401_UNAUTHORIZED)
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()  # deletes the token
        return Response({"detail": "Logged out successfully."}, status=s.HTTP_200_OK)
    
class PasswordResetRequestView(APIView):

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
        reset_link = f"http://localhost:5173/reset-password/{uid}/{token}/"  # Frontend link

        send_mail(
            subject="Reset your RepTrack password",
            message=f"Use the following link to reset your password:\n\n{reset_link}",
            from_email="noreply@reptrack.com",
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response({"detail": "If that email is registered, a reset link has been sent."})
    
class PasswordResetConfirmView(APIView):

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
    
class UserProfileView(APIView):

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
    
