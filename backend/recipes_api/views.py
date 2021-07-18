from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .models import Ingredient, Recipe, RecipeIngredient, Tag
from .serializers import (IngredientSerializer,
                          RecipeListSerializer, TagSerializer)


class TagViewSet(ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (permissions.AllowAny, )
    pagination_class = None
    search_fields = ['name', ]


class RecipeListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = RecipeListSerializer
    queryset = Recipe.objects.all()
    permission_classes = (permissions.AllowAny, )
