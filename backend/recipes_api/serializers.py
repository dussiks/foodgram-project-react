from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Follow, Ingredient, Recipe, RecipeIngredient, Tag
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


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=CustomUser.objects.all(),
    )

    class Meta:
        model = Follow
        fields = ('user', 'following')
        validators = [UniqueTogetherValidator(
            queryset=Follow.objects.all(),
            fields=['user', 'following']
        )]

    def validate(self, data):
        request = self.context['request']
        if request.user == data.get('following'):
            raise serializers.ValidationError(
                'User can not follow himself.'
            )
        return data
