from django.core.exceptions import ObjectDoesNotExist
from rest_framework import mixins, permissions, viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import (CustomUser, Favorite, Follow,
                     Ingredient, Recipe, ShoppingCart, Tag)
from .paginator import CustomPagination
from .permissions import IsOwnerOrAdmin
from .serializers import (CustomUserSerializer, CustomUserSubscribeSerializer,
                          FavoriteAndShoppingRecipeSerializer,
                          IngredientSerializer, RecipeListSerializer,
                          TagSerializer)


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


class RecipeListViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    serializer_class = RecipeListSerializer
    queryset = Recipe.objects.all()
    permission_classes = (permissions.AllowAny, )
    filterset_fields = ['author', ]

    @action(detail=True, methods=['get', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        current_user = request.user
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('pk'))

        if request.method == 'GET':
            if recipe.favorite_recipes.filter(user=current_user).exists():
                error_text = "Recipe already in user's favorites."
                return Response(error_text,
                                status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.create(user=current_user, recipe=recipe)
            serializer = FavoriteAndShoppingRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            try:
                fav_recipe = recipe.favorite_recipes.get(user=current_user)
            except ObjectDoesNotExist:
                error_text = 'Choosen recipe is not in favorites.'
                return Response(error_text,
                                status=status.HTTP_400_BAD_REQUEST)
            fav_recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionViewSet(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request):
        user = request.user
        recipe_author = get_object_or_404(CustomUser,
                                          pk=self.kwargs.get('id'))
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

    def delete(self, request):
        follower = request.user
        recipe_author = get_object_or_404(CustomUser,
                                          pk=self.kwargs.get('id'))
        try:
            subscription = follower.followers.get(following=recipe_author)
        except ObjectDoesNotExist:
            error_text = 'No subscription on given user found.'
            return Response(error_text,
                            status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsOwnerOrAdmin])
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
