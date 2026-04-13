from rest_framework import generics, status, permissions
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema, inline_serializer
import pyotp

from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    LoginSerializer,
    RefreshTokenSerializer,
    LogoutSerializer,
    TwoFactorSetupSerializer,
    TwoFactorVerifySerializer,
    TwoFactorDisableSerializer,
)


token_pair_serializer = inline_serializer(
    name='TokenPair',
    fields={
        'refresh': serializers.CharField(),
        'access': serializers.CharField(),
    },
)

auth_response_serializer = inline_serializer(
    name='AuthResponse',
    fields={
        'user': UserProfileSerializer(),
        'tokens': token_pair_serializer,
    },
)

message_response_serializer = inline_serializer(
    name='MessageResponse',
    fields={
        'detail': serializers.CharField(),
    },
)

refresh_response_serializer = inline_serializer(
    name='RefreshTokenResponse',
    fields={
        'access': serializers.CharField(),
        'refresh': serializers.CharField(required=False),
    },
)

two_factor_setup_response_serializer = inline_serializer(
    name='TwoFactorSetupResponse',
    fields={
        'secret': serializers.CharField(),
        'otp_auth_url': serializers.CharField(),
        'manual_entry_key': serializers.CharField(),
    },
)

two_factor_status_response_serializer = inline_serializer(
    name='TwoFactorStatusResponse',
    fields={
        'detail': serializers.CharField(),
        'is_2fa_enabled': serializers.BooleanField(),
    },
)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=['Authentication'],
        summary='Register a new user',
        description='Creates a new attendee, organizer, or admin account and returns JWT tokens.',
        request=UserRegistrationSerializer,
        responses={
            201: auth_response_serializer,
            400: OpenApiResponse(description='Validation error'),
        },
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token_serializer = LoginSerializer(data={
            User.USERNAME_FIELD: request.data.get(User.USERNAME_FIELD),
            'password': request.data.get('password'),
        })
        token_serializer.is_valid(raise_exception=True)
        return Response({
            **token_serializer.validated_data,
            'user': UserProfileSerializer(user).data,
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    @extend_schema(
        tags=['Authentication'],
        summary='Log in',
        description='Authenticates a user with email and password and returns a JWT token pair. If 2FA is enabled, a valid OTP code is also required.',
        request=LoginSerializer,
        responses={
            200: auth_response_serializer,
            401: OpenApiResponse(response=message_response_serializer, description='Invalid credentials'),
            403: OpenApiResponse(response=message_response_serializer, description='Account is disabled'),
        },
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class RefreshTokenView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RefreshTokenSerializer

    @extend_schema(
        tags=['Authentication'],
        summary='Refresh an access token',
        description='Uses a valid refresh token to issue a new access token. When rotation is enabled, a new refresh token is returned and the previous token is blacklisted.',
        request=RefreshTokenSerializer,
        responses={
            200: refresh_response_serializer,
            401: OpenApiResponse(response=message_response_serializer, description='Refresh token is invalid or expired'),
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class LogoutView(APIView):
    serializer_class = LogoutSerializer

    @extend_schema(
        tags=['Authentication'],
        summary='Log out',
        description='Blacklists the provided refresh token.',
        request=LogoutSerializer,
        responses={
            200: message_response_serializer,
            400: OpenApiResponse(response=message_response_serializer, description='Invalid token'),
        },
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            serializer.save()
        except Exception:
            return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'detail': 'Logged out successfully.'})

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user

class ChangePasswordView(APIView):
    @extend_schema(
        tags=['Authentication'],
        summary='Change password',
        description='Changes the password for the currently authenticated user.',
        request=ChangePasswordSerializer,
        responses={
            200: message_response_serializer,
            400: OpenApiResponse(response=message_response_serializer, description='Password validation failed'),
        },
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user

        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'detail': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()

        outstanding_tokens = OutstandingToken.objects.filter(user=user)
        for outstanding_token in outstanding_tokens:
            BlacklistedToken.objects.get_or_create(token=outstanding_token)

        return Response({'detail': 'Password changed successfully.'})


class TwoFactorSetupView(APIView):
    serializer_class = TwoFactorSetupSerializer

    @extend_schema(
        tags=['Authentication'],
        summary='Start 2FA setup',
        description='Generates a new TOTP secret and provisioning URI for the authenticated user.',
        request=TwoFactorSetupSerializer,
        responses={
            200: two_factor_setup_response_serializer,
            400: OpenApiResponse(response=message_response_serializer, description='Password is incorrect'),
        },
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not request.user.check_password(serializer.validated_data['password']):
            return Response({'detail': 'Password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

        secret = pyotp.random_base32()
        issuer = 'Planova'
        otp_auth_url = pyotp.TOTP(secret).provisioning_uri(
            name=request.user.email,
            issuer_name=issuer,
        )

        return Response({
            'secret': secret,
            'otp_auth_url': otp_auth_url,
            'manual_entry_key': secret,
        })


class TwoFactorVerifyView(APIView):
    serializer_class = TwoFactorVerifySerializer

    @extend_schema(
        tags=['Authentication'],
        summary='Verify and enable 2FA',
        description='Verifies a TOTP code for the provided secret and enables 2FA on the authenticated account.',
        request=TwoFactorVerifySerializer,
        responses={
            200: two_factor_status_response_serializer,
            400: OpenApiResponse(response=message_response_serializer, description='Invalid secret or OTP code'),
        },
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        secret = serializer.validated_data['secret']
        otp_code = serializer.validated_data['otp_code']
        totp = pyotp.TOTP(secret)

        if not totp.verify(otp_code, valid_window=1):
            return Response({'detail': 'Invalid authentication code.'}, status=status.HTTP_400_BAD_REQUEST)

        request.user.enable_two_factor(secret)

        outstanding_tokens = OutstandingToken.objects.filter(user=request.user)
        for outstanding_token in outstanding_tokens:
            BlacklistedToken.objects.get_or_create(token=outstanding_token)

        return Response({
            'detail': 'Two-factor authentication enabled successfully.',
            'is_2fa_enabled': True,
        })


class TwoFactorDisableView(APIView):
    serializer_class = TwoFactorDisableSerializer

    @extend_schema(
        tags=['Authentication'],
        summary='Disable 2FA',
        description='Disables TOTP-based 2FA after confirming the password and current OTP code.',
        request=TwoFactorDisableSerializer,
        responses={
            200: two_factor_status_response_serializer,
            400: OpenApiResponse(response=message_response_serializer, description='Password or OTP code is invalid'),
        },
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not request.user.check_password(serializer.validated_data['password']):
            return Response({'detail': 'Password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_2fa_enabled or not request.user.two_factor_secret:
            return Response({'detail': 'Two-factor authentication is not enabled.'}, status=status.HTTP_400_BAD_REQUEST)

        totp = pyotp.TOTP(request.user.two_factor_secret)
        if not totp.verify(serializer.validated_data['otp_code'], valid_window=1):
            return Response({'detail': 'Invalid authentication code.'}, status=status.HTTP_400_BAD_REQUEST)

        request.user.disable_two_factor()

        outstanding_tokens = OutstandingToken.objects.filter(user=request.user)
        for outstanding_token in outstanding_tokens:
            BlacklistedToken.objects.get_or_create(token=outstanding_token)

        return Response({
            'detail': 'Two-factor authentication disabled successfully.',
            'is_2fa_enabled': False,
        })
