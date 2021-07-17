from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .models import CustomUser, Follow
from .serializers import CustomUserCreateSerializer, FollowSerializer


class CustomUserModelViewSet(UserViewSet):
    queryset = CustomUser.objects.all()

    def create(self):
        serializer = CustomUserCreateSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FollowViewSet(ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        user = self.request.user
        return user.following.all()

    def perform_create(self, serializer):
        serializer.save(follower=self.request.user)
