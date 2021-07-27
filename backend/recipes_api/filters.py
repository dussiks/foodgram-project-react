from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework.response import Response

from .models import Ingredient, Recipe, Tag


class RecipeFilter(filters.FilterSet):
    tags = filters.CharFilter(method='filter_tags')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous:
            return Recipe.objects.none()
        if value:
            return queryset.filter(favorites__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous:
            return Recipe.objects.none()
        if value:
            return queryset.filter(shopping_carts__user=user)
        return queryset

    def filter_tags(self, queryset, name, value):
        try:
            tags_list = self.request.query_params.getlist('tags')
        except AttributeError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        tags = Tag.objects.filter(slug__in=tags_list).values_list('id',
                                                                  flat=True)
        if tags is not None:
            return queryset.filter(tags__id__in=tags).distinct()
        return queryset


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='contains')

    class Meta:
        model = Ingredient
        fields = ('name', )
