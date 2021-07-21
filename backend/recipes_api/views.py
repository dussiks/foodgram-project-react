from django.db import models

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import mixins, permissions, viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import (CustomUser, Favorite, Follow,
                     Ingredient, Recipe, ShoppingCart, Tag)
from .paginator import CustomPagination
from .permissions import IsOwner
from .serializers import (CustomUserSubscribeSerializer,
                          FavoriteAndShoppingRecipeSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
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
    search_fields = ['name', ]
    pagination_class = None


class RecipeListViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeListSerializer
    queryset = Recipe.objects.all()
    permission_classes = (permissions.AllowAny, )
    filterset_fields = ['author', ]

    def get_permissions(self):
        if self.action == 'create':
            return permissions.IsAuthenticated(),
        if self.action in ['destroy', 'partial_update', 'update']:
            return IsOwner(),
        return permissions.AllowAny(),

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeListSerializer
        return RecipeCreateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context


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
        except ObjectDoesNotExist:
            error_text = 'Choosen recipe is not in shopping cart.'
            return Response(error_text, status=status.HTTP_400_BAD_REQUEST)
        shopped_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionViewSet(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, pk=None):
        user = request.user
        recipe_author = get_object_or_404(CustomUser, pk=pk)
        if user == recipe_author:
            error_text = 'You can not subscribe yourself.'
            return Response(error_text, status=status.HTTP_400_BAD_REQUEST)

        if Follow.objects.filter(
                follower=user, following=recipe_author
        ).exists():
            error_text = 'You are already subscribed to this author.'
            return Response(error_text, status=status.HTTP_400_BAD_REQUEST)

        Follow.objects.create(follower=user, following=recipe_author)
        recipes_count = recipe_author.recipes.all().count()
        serializer = CustomUserSubscribeSerializer(
            recipe_author,
            context={'request': request, 'recipes_count': recipes_count}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk=None):
        follower = request.user
        recipe_author = get_object_or_404(CustomUser, pk=pk)
        try:
            subscription = follower.followers.get(following=recipe_author)
        except ObjectDoesNotExist:
            error_text = 'No subscription on given user found.'
            return Response(error_text,
                            status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, ])
def user_subscriptions(request):
    user = request.user
    subscripts = user.followers.select_related('following').all()

    if subscripts:
        recipe_authors = []
        for subscript in subscripts:
            recipe_authors.append(subscript.following)

        recipes_limit = request.query_params.get('recipes_limit')
        try:
            recipes_limit = int(recipes_limit)
        except (TypeError, ValueError):
            recipes_limit = None

        sub_recipes = Recipe.objects.filter(
            author__in=recipe_authors
        ).order_by('-id')[:recipes_limit]
        paginator = CustomPagination()
        page = paginator.paginate_queryset(sub_recipes, request)
        if page is not None:
            serializer = RecipeListSerializer(page, many=True,
                                              context={'request': request})
            return paginator.get_paginated_response(serializer.data)

    return Response(status=status.HTTP_200_OK)
