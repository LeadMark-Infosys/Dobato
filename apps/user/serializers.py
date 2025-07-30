import re
import logging
from rest_framework import serializers
from apps.user.models import User, AdminUser
from django.contrib.auth.hashers import make_password

logger = logging.getLogger('api_log')

def password_validator(value):
    if len(value) < 8:
        raise serializers.ValidationError("Password must be at least 8 characters long.")
    if not re.search(r'\d', value):
        raise serializers.ValidationError("Password must contain at least one digit.")
    if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', value):
        raise serializers.ValidationError("Password must contain at least one special character.")

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

class AdminUserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[password_validator])

    class Meta:
        model = AdminUser
        fields = ['id', 'name', 'email', 'phone', 'password', 'is_staff', 'is_superuser']

    def create(self, validated_data):
        password = validated_data.pop('password')
        is_superuser = validated_data.get('is_superuser', False)
        is_staff = validated_data.get('is_staff', False)

        if is_superuser and is_staff:
            user_type = 'super_admin'
        elif is_staff and not is_superuser:
            user_type = 'support_user'
        else:
            raise serializers.ValidationError("Invalid combination for TenantUser")

        tenant_user = AdminUser(**validated_data, user_type=user_type)
        tenant_user.password = make_password(password)
        tenant_user.save()
        return tenant_user


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[password_validator])

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'phone', 'password', 'user_type', 'is_staff', 'is_active', 'is_superuser']

    def create(self, validated_data):
        logger.info(f"Registering new User with data: {validated_data}")
        password = validated_data.pop('password')
        user_type = validated_data.pop('user_type', 'public')

        user = User(**validated_data)
        user.user_type = user_type
        user.set_password(password)
        user.save()
        return user

class PasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)

class OTPVerifySerializer(serializers.Serializer):
    user_id = serializers.CharField()
    otp = serializers.CharField(max_length=6)

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[password_validator])

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            logger.warning(f"Incorrect current password attempt for user {user}")
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        logger.info(f"Changing password for user {user}")
        user.set_password(validated_data['new_password'])
        user.save()
        return user