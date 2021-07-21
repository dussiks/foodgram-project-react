from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .models import (CustomUser, Favorite, Ingredient, Recipe,
                     RecipeIngredient, ShoppingCart, Tag)
from users.serializers import CustomUserSerializer


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class FavoriteAndShoppingRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class RecipeListSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(many=False, required=True)
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(many=True,
                                             source='recipe_ingredients')
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time')

    def get_is_favorited(self, recipe):
        current_user = self.context.get('request').user
        if current_user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=current_user, recipe=recipe
        ).exists()

    def get_is_in_shopping_cart(self, recipe):
        current_user = self.context.get('request').user
        if current_user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=current_user, recipe=recipe
        ).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time', )






class CustomUserSubscribeSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = CustomUserSerializer.Meta.fields + ('recipes',
                                                     'recipes_count', )

    def get_recipes_count(self, **kwargs):
        recipes_count = self.context.get('recipes_count')
        return recipes_count

    def get_recipes(self, author):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        try:
            recipes_limit = int(recipes_limit)
        except (TypeError, ValueError):
            recipes_limit = None
        recipes = author.recipes.all()[:recipes_limit]
        serializer = RecipeListSerializer(recipes, many=True,
                                          context={'request': request})
        return serializer.data
