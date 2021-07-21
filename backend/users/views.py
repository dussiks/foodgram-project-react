from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import CustomUser
from .serializers import CustomUserSerializer, CustomUserCreateSerializer


class CustomUserModelViewSet(viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer
    permission_classes = (permissions.IsAuthenticated, )
    queryset = CustomUser.objects.all()

    def get_permissions(self):
        if self.action == 'create':
            return permissions.AllowAny(),
        return permissions.IsAuthenticated(),

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        return CustomUserSerializer

    @action(detail=False, methods=['GET', 'PUT'],
            permission_classes=(permissions.IsAuthenticated,))
    def me(self, request):
        user = self.request.user
        serializer = self.get_serializer(
            user, data=request.data, partial=True,
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
