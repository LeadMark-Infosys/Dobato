from rest_framework import permissions

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