from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as s
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from .serializers import UserRegisterSerializer
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model, authenticate

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