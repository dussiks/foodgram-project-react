from djoser.views import UserViewSet
from rest_framework import permissions

from .models import CustomUser
from .serializers import CustomUserSerializer
from .permissions import IsCurrentUserOrAdmin


class CustomUserModelViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return permissions.AllowAny(),
        elif self.action in ['destroy', 'partial_update', 'update']:
            return IsCurrentUserOrAdmin(),
        return permissions.IsAuthenticated(),
