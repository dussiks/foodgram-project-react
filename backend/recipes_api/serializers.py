import base64
import six
import uuid
from django.core.files.base import ContentFile
from rest_framework import serializers

from .models import (CustomUser, Favorite, Ingredient, Recipe,
                     RecipeIngredient, ShoppingCart, Tag)
from users.serializers import CustomUserSerializer


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        if isinstance(data, six.string_types):
            if 'data:' in data and ';base64,' in data:
                header, data = data.split(';base64,')

            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            file_name = str(uuid.uuid4())[:20]
            file_extension = self.get_file_extension(file_name, decoded_file)
            complete_file_name = "%s.%s" % (file_name, file_extension, )
            data = ContentFile(decoded_file, name=complete_file_name)
        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = 'jpg' if extension == 'jpeg' else extension
        return extension


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
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
    author = CustomUserSerializer(many=False, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(many=True,
                                             source='recipe_ingredients')
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

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


class IngredientWithAmountSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    def validate(self, data):
        if not Ingredient.objects.filter(id=data['id']).exists():
            raise serializers.ValidationError('No ingredient with such id.')

        if not isinstance(data['amount'], int):
            raise serializers.ValidationError(
                f'Amount for id = {data["id"]} should be integer.'
            )

        if data['amount'] <= 0:
            raise serializers.ValidationError(
                f'Amount for id = {data["id"]} should be bigger than 0.'
            )
        return data


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = IngredientWithAmountSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')

    def create(self, validated_data):
        request = self.context.get('request')
        author = request.user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.save()
        recipe.tags.set(tags)

        for item in ingredients:
            ingredient = Ingredient.objects.get(id=item.get('id'))
            amount = item.get('amount')
            recipe_ingredient = RecipeIngredient.objects.create(
                ingredient=ingredient,
                recipe=recipe,
                amount=amount
            )
            recipe_ingredient.save()
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        RecipeIngredient.objects.filter(recipe=recipe).delete()
        for item in ingredients:
            ingredient = Ingredient.objects.get(id=item.get('id'))
            amount = item.get('amount')
            recipe_ingredient = RecipeIngredient.objects.create(
                ingredient=ingredient,
                recipe=recipe,
                amount=amount
            )
            recipe_ingredient.save()

        recipe.cooking_time = validated_data.pop('cooking_time')
        recipe.name = validated_data.pop('name')
        recipe.text = validated_data.pop('text')
        if validated_data.get('image') is not None:
            recipe.image = validated_data.pop('image')
        recipe.save()
        recipe.tags.set(tags)
        return recipe

    def to_representation(self, instance):
        return RecipeListSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        ).data


class CustomUserSubscribeSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = CustomUserSerializer.Meta.fields + ('recipes',
                                                     'recipes_count', )

    def get_recipes_count(self, author):
        return author.recipes.all().count()

    def get_recipes(self, author):
        request = self.context.get('request')
        recipes_limit = self.context.get('recipes_limit')
        recipes = author.recipes.all()[:recipes_limit]
        serializer = FavoriteAndShoppingRecipeSerializer(
            recipes, many=True, context={'request': request}
        )
        return serializer.data
