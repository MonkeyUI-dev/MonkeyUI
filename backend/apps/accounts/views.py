import secrets
import string

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    UserAPIKeySerializer,
    CreateUserAPIKeySerializer,
)
from .models import UserAPIKey

User = get_user_model()


class EventRegisterThrottle(AnonRateThrottle):
    """Rate limiting for event registration: 10 requests per hour per IP."""
    rate = '10/hour'


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens for the new user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': _('User registered successfully'),
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    """
    API endpoint for user login.
    Extends TokenObtainPairView to add user data to response.
    """
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Call the parent class to get tokens
        response = super().post(request, *args, **kwargs)
        
        # Get user data
        try:
            user = User.objects.get(email=request.data['email'])
            response.data['user'] = UserSerializer(user).data
            response.data['message'] = _('Login successful')
        except User.DoesNotExist:
            pass
        
        return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    API endpoint for user logout.
    Blacklists the refresh token.
    """
    try:
        refresh_token = request.data.get("refresh_token")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return Response({
            'message': _('Logout successful')
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'message': _('Invalid token'),
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    """
    API endpoint to get current user data.
    """
    serializer = UserSerializer(request.user)
    return Response({
        'user': serializer.data
    }, status=status.HTTP_200_OK)


class ChangePasswordView(generics.UpdateAPIView):
    """
    API endpoint for changing user password.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer
    
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        
        # Check old password
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({
                'message': _('Old password is incorrect')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Set new password
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'message': _('Password changed successfully')
        }, status=status.HTTP_200_OK)


class UserAPIKeyListCreateView(generics.ListCreateAPIView):
    """
    API endpoint to list and create API keys for the authenticated user.
    """
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Disable pagination for API keys
    
    def get_queryset(self):
        return UserAPIKey.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateUserAPIKeySerializer
        return UserAPIKeySerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        # Check if user already has 10 API keys
        existing_count = UserAPIKey.objects.filter(user=request.user).count()
        if existing_count >= 10:
            return Response({
                'message': _('Maximum number of API keys (10) reached. Please delete an existing key first.')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(user=request.user)
        
        # Return full key only on creation
        return Response({
            'message': _('API key created successfully'),
            'api_key': {
                'id': str(instance.id),
                'name': instance.name,
                'key': instance.key,  # Full key shown only once
                'key_prefix': instance.key_prefix,
                'created_at': instance.created_at,
            }
        }, status=status.HTTP_201_CREATED)


class UserAPIKeyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update, or delete a specific API key.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserAPIKeySerializer
    
    def get_queryset(self):
        return UserAPIKey.objects.filter(user=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'message': _('API key deleted successfully')
        }, status=status.HTTP_200_OK)


def _generate_event_password():
    """Generate a random password that passes Django validators."""
    # 4 lowercase + 4 uppercase + 4 digits + 2 special chars = 14 chars
    chars = (
        secrets.choice(string.ascii_lowercase) for _ in range(4)
    )
    uppers = (
        secrets.choice(string.ascii_uppercase) for _ in range(4)
    )
    digits = (
        secrets.choice(string.digits) for _ in range(4)
    )
    specials = (
        secrets.choice('!@#$%&*') for _ in range(2)
    )
    password_chars = list(chars) + list(uppers) + list(digits) + list(specials)
    secrets.SystemRandom().shuffle(password_chars)
    return ''.join(password_chars)


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([EventRegisterThrottle])
def event_register_view(request):
    """
    Quick registration endpoint for the SheBuilds 20260308 event.
    Generates a random account with email, password, and an API key.
    No input required — one-click registration.
    """
    # Generate random credentials
    random_suffix = secrets.token_hex(4)
    email = f"shebuilds_{random_suffix}@monkeyui.app"
    password = _generate_event_password()
    name = f"SheBuilds User {random_suffix[:4]}"

    # Create user
    user = User.objects.create_user(
        email=email,
        password=password,
        name=name,
    )

    # Create an API key for the user
    api_key = UserAPIKey.objects.create(
        user=user,
        name='SheBuilds Event Key',
    )

    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)

    return Response({
        'message': _('Event registration successful'),
        'credentials': {
            'email': email,
            'password': password,
            'api_key': api_key.key,
        },
        'user': UserSerializer(user).data,
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    }, status=status.HTTP_201_CREATED)
