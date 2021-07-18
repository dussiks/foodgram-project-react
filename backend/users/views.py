from django.core.exceptions import ObjectDoesNotExist
import djoser.views
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import CustomUser, Follow
from .serializers import CustomUserSerializer, CustomUserCreateSerializer, FollowSerializer


class CustomUserModelViewSet(DjoserUserViewSet):
    serializer_class = CustomUserSerializer
    permission_classes = (permissions.IsAuthenticated, )

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, **kwargs):
        """Subscribe  to recipe's author."""
        follower = request.user
        recipe_author = get_object_or_404(CustomUser, pk=self.kwargs.get('id'))
        if request.method == 'POST':
            subscription = Follow.objects.get_or_create(
                follower=follower, following=recipe_author
            )
            serializer = CustomUserSerializer(follower)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False)
    def subscriptions(self, request):
        user = request.user
        subscriptions = user.followers.all()
        if subscriptions:
            followings = []
            for subscription in subscriptions:
                followings.append(subscription.following)
            serializer = CustomUserSerializer(followings, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = CustomUserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FollowViewSet(ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        user = self.request.user
        return user.followers.all()

    def perform_create(self, serializer):
        serializer.save(follower=self.request.user)
