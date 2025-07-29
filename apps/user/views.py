import random
import requests
import os
import logging

from datetime import timedelta

from django.utils import timezone
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.db.models import Count, Q

from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.throttling import UserRateThrottle

from apps.core.views import generate_otp, send_otp_sms
from apps.user.models import User, UserOTP
from apps.user.serializers import (
    UserRegistrationSerializer, OTPVerifySerializer, 
    ChangePasswordSerializer, UserSerializer
)
from apps.user.tasks import send_email_task

logger = logging.getLogger('django')

class UserRegistrationView(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return User.objects.none()

    def create(self, request, *args, **kwargs):
        logger.info(f"User registration initiated with data: {request.data}")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        logger.info(f"User created with ID: {user.id}")

        otp_code = generate_otp()
        UserOTP.objects.create(user=user, otp=otp_code, is_verified=False)
        send_otp_sms(user.phone, otp_code) if user.phone else None
        logger.info(f"OTP entry created for user ID: {user.id}")

        phone = getattr(user, 'phone', None)
        if phone:
            send_otp_sms(phone, otp_code)
            logger.info(f"OTP sent to phone: {phone}")

        return Response({
            "message": "User registered successfully. OTP sent to your phone.",
            "user": self.get_serializer(user).data
        }, status=status.HTTP_201_CREATED)

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logger.info(f"OTP verification requested with data: {request.data}")
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data['user_id']
        otp = serializer.validated_data['otp']
        cutoff_time = timezone.now() - timedelta(minutes=5)
        otp_qs = UserOTP.objects.filter(
            user_id=user_id,
            otp=otp,
            is_verified=False,
            created_at__gte=cutoff_time
        ).order_by('-created_at')

        if not otp_qs.exists():
            logger.warning(f"Invalid or expired OTP for user ID: {user_id}")
            return Response({"detail": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

        otp_entry = otp_qs.first()
        otp_entry.is_verified = True
        otp_entry.save()
        logger.info(f"OTP verified for user ID: {user_id}")

        user = otp_entry.user
        user.is_active = True
        user.save()
        logger.info(f"User activated: {user_id}")

        return Response({"detail": "OTP verified successfully."}, status=status.HTTP_200_OK)

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = User.objects.all()
        params = self.request.query_params
        logger.info(f"Filtering users with params: {params}")

        if (user_type := params.get('user_type')):
            queryset = queryset.filter(user_type=user_type)
        if (email := params.get('email')):
            queryset = queryset.filter(email=email)
        if (status_param := params.get('status')):
            queryset = queryset.filter(status=status_param)
        if (is_verified := params.get('is_verified')):
            queryset = queryset.filter(is_verified=is_verified.lower() == 'true')
        if (search := params.get('search')):
            queryset = queryset.filter(Q(email__icontains=search) | Q(name__icontains=search))
        if (sort_by := params.get('sort_by')):
            queryset = queryset.order_by(sort_by)

        logger.info(f"Final user queryset count: {queryset.count()}")
        return queryset

    @action(detail=False, methods=['post'], url_path='change-password', throttle_classes=[UserRateThrottle])
    def change_password(self, request):
        logger.info(f"Password change requested for user ID: {request.user.id}")
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            logger.info(f"Password changed for user ID: {request.user.id}")
            return Response({'detail': 'Password changed successfully'}, status=status.HTTP_200_OK)
        logger.warning(f"Password change failed for user ID: {request.user.id}, errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='deactivate', throttle_classes=[UserRateThrottle])
    def deactivate(self, request):
        user = request.user
        logger.info(f"Account deactivation requested for user ID: {user.id}")
        user.is_active = False
        user.status = 'deactivated'
        user.save()
        logger.info(f"User deactivated: {user.id}")
        return Response({'detail': 'Account deactivated (soft deleted) successfully.'}, status=status.HTTP_200_OK)

token_generator = PasswordResetTokenGenerator()

class ResetPasswordAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [UserRateThrottle]

    def post(self, request):
        email = request.data.get("email")
        logger.info(f"Password reset requested for email: {email}")

        if not email:
            return Response({"error": "Email is required"}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            logger.warning(f"No user found with email: {email}")
            return Response({"error": "No user found with this email"}, status=404)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)
        relative_url = f"/api/user/reset-password-confirm/{uid}/{token}/"
        reset_link = request.build_absolute_uri(relative_url)

        send_email_task.delay(
            subject="Reset your password",
            message=f"Click the link to reset your password:\n{reset_link}",
            from_email=None,
            recipient_list=[email],
        )
        logger.info(f"Password reset email sent to: {email}")
        return Response({"message": "Password reset email sent"}, status=200)

class ResetPasswordConfirmAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [UserRateThrottle]

    def get(self, request, uidb64, token):
        logger.info(f"Password reset confirm GET called with UID: {uidb64}")

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError) as e:
            logger.error(f"Invalid user ID in reset link: {e}")
            return Response({"error": "Invalid user ID"}, status=400)

        if not token_generator.check_token(user, token):
            logger.warning(f"Invalid or expired reset token for user ID: {uid}")
            return Response({"error": "Invalid or expired token"}, status=400)

        password = request.data.get("password")
        if not password:
            return Response({"error": "Password is required."}, status=400)

        user.set_password(password)
        user.save()
        logger.info(f"Password reset successful for user ID: {uid}")

        return Response({"message": "Password has been reset successfully"}, status=200)