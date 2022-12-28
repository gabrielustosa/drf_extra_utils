from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Allow access to admin user or read only."""

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_staff
            or request.method in permissions.SAFE_METHODS
        )


class IsCreator(permissions.BasePermission):
    """Allow access only for the creator of the object."""

    def has_object_permission(self, request, view, obj):
        return bool(
            obj.creator == request.user
            or request.method in permissions.SAFE_METHODS
        )
