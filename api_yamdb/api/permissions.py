from rest_framework import permissions


class AdminOrSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return (request.user.is_admin
                    or request.user.is_superuser)
        return False


class AccessToReview(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return (request.user.is_admin
                    or request.user.is_moderator
                    or request.user.is_superuser
                    or request.user == obj.author)
        return False
