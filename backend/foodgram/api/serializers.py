from rest_framework.serializers import ModelSerializer

from .models import Ingredient, Recipe, RecipeIngredient, Tag


class TagSerializer(ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(ModelSerializer):

    class Meta:
        model = RecipeIngredient
        fields = ('recipe', 'ingredient', 'amount')


class RecipeSerializer(ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients', 'name', 'image', 'text', 'cooking_time')
