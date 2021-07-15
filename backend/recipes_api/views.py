from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .models import Follow, Ingredient, Recipe, RecipeIngredient, Tag
from .serializers import (FollowSerializer, IngredientSerializer,
                          RecipeSerializer, TagSerializer)


class CreateListViewSet(mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    pass


class FollowViewSet(CreateListViewSet):
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Follow.objects.all()
        return user.following.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TagViewSet(ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()


class RecipeViewSet(ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
