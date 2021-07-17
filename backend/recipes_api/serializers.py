from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import CustomUser


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = RecipeIngredient
        fields = ('recipe', 'ingredient', 'amount')


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients', 'name', 'image', 'text', 'cooking_time')


#

class CustomUserSerializer(serializers.ModelSerializer):
    recipes = RecipeSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ('first_name', 'recipes')
