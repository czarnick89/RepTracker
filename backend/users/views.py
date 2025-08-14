from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as s
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserRegisterSerializer, UserProfileSerializer, MyTokenObtainPairSerializer
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.utils import timezone

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
            link = f"https://{domain}/api/v1/users/verify-email/{uid}/{token}/"
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
    
    def get(self, request, uidb64, token):
        print(f"UID64: {uidb64}")
        print(f"Token: {token}")
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            print(f"Decoded UID: {uid}")
            user = User.objects.get(pk=uid)
        except Exception as e:
            print(f"Error decoding or finding user: {e}")
            return redirect("https://localhost:5173/register/?verified=invalid")

        print(f"User before verification: {user}, is_active={user.is_active}")
        
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            print(f"User after save: is_active={user.is_active}")
            return redirect("https://localhost:5173/login/?verified=true")

        return redirect("https://localhost:5173/login/?verified=expired") # need to change to resend verification?

class MyTokenObtainPairView(TokenObtainPairView):  # login
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

        # Set HttpOnly access token cookie
        response.set_cookie(
            key='access_token',
            value=access,
            httponly=True,
            secure=True,        # <-- must be True for HTTPS
            samesite='None',    # <-- None is required for cross-site cookies with Secure flag
            max_age=15 * 60,
            path='/',
        )

        response.set_cookie(
            key='refresh_token',
            value=refresh,
            httponly=True,
            secure=True,        # <-- must be True for HTTPS
            samesite='None',    # <-- None required for cross-site with Secure
            max_age=24 * 60 * 60,
            path='/api/v1/users/',
        )

        return response
    
class LogoutView(APIView):
    permission_classes = [AllowAny]  # Allow access without authentication

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass  # Optionally log here

        response = Response({"detail": "Logged out successfully."}, status=s.HTTP_200_OK)
        response.delete_cookie("access_token", path='/')
        response.delete_cookie("refresh_token", path='/api/v1/users/')
        return response
    
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
        reset_link = f"https://localhost:5173/reset-password/{uid}/{token}/"  # Frontend link

        send_mail(
            subject="Reset your RepTracker password",
            message=f"Use the following link to reset your password:\n\n{reset_link}",
            from_email="noreply@reptracker.com",
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
        print(f"Profile requested by: {request.user}")
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=s.HTTP_400_BAD_REQUEST)
    
class ResendVerificationEmailView(APIView):
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

        # Generate token and send email again
        from django.contrib.auth.tokens import default_token_generator

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        domain = get_current_site(request).domain
        link = f"https://{domain}/api/v1/users/verify-email/{uid}/{token}/"

        send_mail(
            subject="Verify your email",
            message=f"Click the link to verify your account: {link}",
            from_email="noreply@reptracker.com",
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response({"detail": "Verification email resent. Check your inbox."}, status=s.HTTP_200_OK)
    
class CookieTokenRefreshView(TokenRefreshView):

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
        new_refresh_token = serializer.validated_data.get('refresh', None)  # may be present if rotation enabled

        response = Response({"detail": "Token refreshed successfully."}, status=s.HTTP_200_OK)

        # Set new access token cookie
        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=True,  # Change to True in production with HTTPS
            samesite='None',  # Allow cross-site cookie for frontend CORS
            max_age=15 * 60,  # 15 minutes
            path='/',
        )

        # Rotate refresh token cookie if provided
        if new_refresh_token:
            response.set_cookie(
                key='refresh_token',
                value=new_refresh_token,
                httponly=True,
                secure=True,  # Change to True in production with HTTPS
                samesite='None',
                max_age=24 * 60 * 60,  # 1 day
                path='/api/v1/users/',
            )

        return response

