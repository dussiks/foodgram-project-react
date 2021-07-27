from django_filters import rest_framework as filters

from .models import Ingredient, Recipe


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
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
            return Recipe.objects.filter(favorites__user=user)
        return Recipe.objects.all()

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous:
            return Recipe.objects.none()
        if value:
            return Recipe.objects.filter(shopping_carts__user=user)
        return Recipe.objects.all()


class IngredientFilter(filters.FilterSet):

    class Meta:
        model = Ingredient
        fields = {
            'name': ['contains'],
        }
