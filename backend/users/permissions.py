from rest_framework import permissions


class IsOwnerOrAuthenticatedOrCreateOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        return not request.user.is_anonymous

    def has_object_permission(self, request, view, obj):
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user == obj or request.user.is_admin
        return True
