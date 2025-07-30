from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    UserRegistrationView,
    VerifyOTPView,
    UserViewSet,
    ResetPasswordAPIView,
    ResetPasswordConfirmAPIView,
    AdminUserRegistrationView,
)

app_name = 'user'

router = DefaultRouter()
router.register('register', UserRegistrationView, basename='user-register')
router.register('admin-register', AdminUserRegistrationView, basename='tenant-user-register')
router.register('account', UserViewSet, basename='user')
router.register('change-password', UserViewSet, basename='change-password')

urlpatterns = router.urls + [
    path('login/', TokenObtainPairView.as_view(), name='user-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('reset-password/', ResetPasswordAPIView.as_view(), name='reset-password'),
    path('reset-password-confirm/<uidb64>/<token>/', ResetPasswordConfirmAPIView.as_view(), name='reset-password-confirm'),
]
