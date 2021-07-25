from rest_framework import permissions


class IsAuthorOrAdminOrDenied(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user == obj.author or request.user.is_admin


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_admin


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method == 'POST':
            return not request.user.is_anonymous

        return request.user == obj.author or request.user.is_admin
