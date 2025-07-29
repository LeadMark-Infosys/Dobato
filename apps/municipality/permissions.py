from rest_framework.permissions import SAFE_METHODS, BasePermission

class IsSuperUser(BasePermission):
    """
    Only admins can POST, PUT, PATCH, DELETE.
    Everyone can GET (read).
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_superuser
