from rest_framework import permissions

class IsDataEntryOrDataManagerAndApproved(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        return (
            user.is_authenticated and
            getattr(user, 'role', None) in ['dataentry', 'datamanager'] and
            getattr(user, 'is_approved', False)
        )