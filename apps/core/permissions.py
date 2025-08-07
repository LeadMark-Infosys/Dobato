from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS, BasePermission

class IsSuperAdmin(BasePermission):
    """
    Only admins can POST, PUT, PATCH, DELETE.
    Everyone can GET (read).
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_superuser

class IsSupportUser(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and getattr(user, 'user_type', None) == 'support_user'

class IsMunicipalityAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == "municipality_admin"

class IsDepartmentManager(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == "department_manager"

class IsDataEntryUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == "data_entry_user"

class IsPublicUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == "public"
    
class IsDataEntryOrDataManagerAndApproved(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        return (
            user.is_authenticated and
            getattr(user, 'user_type', None) in ['data_entry_user', 'datamanager'] and
            user.is_active is True
        )
    