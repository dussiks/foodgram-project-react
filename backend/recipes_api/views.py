from django.db import models

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import mixins, permissions, viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (CustomUser, Favorite, Follow, Ingredient,
                     Recipe, RecipeIngredient, ShoppingCart, Tag)
from .paginator import CustomPagination
from .permissions import IsOwnerOrAdmin
from .serializers import (CustomUserSubscribeSerializer,
                          FavoriteAndShoppingRecipeSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeListSerializer, TagSerializer)


def create_shop_ingredients(user_id: int) -> dict:
    """
    Prepares data about ingredients from recipes that are added to
    shopping_cart for further transaction to pdf creating view.
    :param user_id - id of the user owner of shopping_cart.
    """
    user = CustomUser.objects.get(id=user_id)
    shopping_cart = user.shopping_carts.select_related('recipe').all()

    shop_ingredients = {}
    for item in shopping_cart:
        recipe = item.recipe
        ingredients = RecipeIngredient.objects.filter(recipe=recipe)

        for ingredient in ingredients:
            name = ingredient.ingredient.name
            unit = ingredient.ingredient.measurement_unit
            amount = ingredient.amount

            if name not in shop_ingredients:
                shop_ingredients[name] = {
                    'amount': amount,
                    'unit': unit
                }
            else:
                shop_ingredients[name]['amount'] = (
                        shop_ingredients[name]['amount'] + amount
                )

    return shop_ingredients


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return permissions.AllowAny(),
        return permissions.IsAdminUser(),


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    search_fields = ['name', ]
    pagination_class = None

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return permissions.AllowAny(),
        return permissions.IsAdminUser(),


class RecipeListViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeListSerializer
    queryset = Recipe.objects.all()
    filterset_fields = ['author', ]

    def get_permissions(self):
        if self.action == 'create':
            return permissions.IsAuthenticated(),
        if self.action in ['destroy', 'partial_update', 'update']:
            return IsOwnerOrAdmin(),
        return permissions.AllowAny(),

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeListSerializer
        return RecipeCreateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    @action(detail=False, permission_classes=[IsOwnerOrAdmin])
    def download_shopping_cart(self, request):
        current_user = request.user
        buying_list = create_shop_ingredients(user_id=current_user.id)
        context = {'buying_list': buying_list}
        return Response(context)


class FavoriteViewSet(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk=None):
        current_user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if recipe.favorites.filter(user=current_user).exists():
            error_text = "Recipe already in user's favorites."
            return Response(error_text, status=status.HTTP_400_BAD_REQUEST)
        Favorite.objects.create(user=current_user, recipe=recipe)
        serializer = FavoriteAndShoppingRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk=None):
        current_user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        try:
            fav_recipe = recipe.favorites.get(user=current_user)
        except models.Recipe.DoesNotExist:
            error_text = 'Choosen recipe is not in favorites.'
            return Response(error_text, status=status.HTTP_400_BAD_REQUEST)
        fav_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk=None):
        current_user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if recipe.shopping_carts.filter(user=current_user).exists():
            error_text = 'Recipe already in shopping cart.'
            return Response(error_text, status=status.HTTP_400_BAD_REQUEST)
        ShoppingCart.objects.create(user=current_user, recipe=recipe)
        serializer = FavoriteAndShoppingRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk=None):
        current_user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        try:
            shopped_recipe = recipe.shopping_carts.get(user=current_user)
        except models.Recipe.DoesNotExist:
            error_text = 'Choosen recipe is not in shopping cart.'
            return Response(error_text, status=status.HTTP_400_BAD_REQUEST)
        shopped_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionViewSet(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, pk=None):
        recipes_limit = request.query_params.get('recipes_limit')
        try:
            recipes_limit = int(recipes_limit)
        except (TypeError, ValueError):
            recipes_limit = None

        user = request.user
        recipe_author = get_object_or_404(CustomUser, pk=pk)
        if user == recipe_author:
            error_text = 'You can not subscribe yourself.'
            return Response(error_text, status=status.HTTP_400_BAD_REQUEST)

        if Follow.objects.filter(user=user, author=recipe_author).exists():
            error_text = 'You are already subscribed to this author.'
            return Response(error_text, status=status.HTTP_400_BAD_REQUEST)

        Follow.objects.create(user=user, author=recipe_author)
        serializer = CustomUserSubscribeSerializer(
            recipe_author,
            context={'request': request, 'recipes_limit': recipes_limit}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk=None):
        follower = request.user
        recipe_author = get_object_or_404(CustomUser, pk=pk)
        try:
            subscription = follower.followers.get(author=recipe_author)
        except ObjectDoesNotExist:
            error_text = 'No subscription on given user found.'
            return Response(error_text,
                            status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, ])
def user_subscriptions(request):
    recipes_limit = request.query_params.get('recipes_limit')
    try:
        recipes_limit = int(recipes_limit)
    except (TypeError, ValueError):
        recipes_limit = None

    user = request.user
    recipe_authors = CustomUser.objects.filter(followings__user=user)
    paginator = CustomPagination()
    page = paginator.paginate_queryset(recipe_authors, request)
    if page is not None:
        serializer = CustomUserSubscribeSerializer(
            page,
            many=True,
            context={'request': request, 'recipes_limit': recipes_limit}
        )
        return paginator.get_paginated_response(serializer.data)

    return Response(status=status.HTTP_200_OK)
