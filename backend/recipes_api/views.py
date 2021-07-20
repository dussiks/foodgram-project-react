from django.core.exceptions import ObjectDoesNotExist
from rest_framework import mixins, permissions, viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import CustomUser, Follow, Ingredient, Recipe, Tag
from .serializers import (CustomUserSerializer, CustomUserSubscribeSerializer, IngredientSerializer,
                          RecipeListSerializer, TagSerializer)
from .permissions import IsOwner


PAGE_SIZE = api_settings.PAGE_SIZE


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
    search_fields = ['name', ]


class RecipeListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = RecipeListSerializer
    queryset = Recipe.objects.all()
    permission_classes = (permissions.AllowAny, )
    filterset_fields = ['author', ]


class SubscriptionViewSet(APIView):
    permission_classes = (permissions.IsAuthenticated, IsOwner, )

    def get(self, request, **kwargs):
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
        recipes_count = Recipe.objects.filter(author=recipe_author).count()
        serializer = CustomUserSubscribeSerializer(
            recipe_author,
            context={'request': request, 'recipes_count': recipes_count}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, **kwargs):
        follower = request.user
        recipe_author = get_object_or_404(CustomUser,
                                          pk=self.kwargs.get('id'))
        try:
            subscription = Follow.objects.get(
                follower=follower, following=recipe_author
            )
        except ObjectDoesNotExist:
            error_text = 'No subscription on given user found.'
            return Response(error_text,
                            status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsOwner])
def user_subscriptions(request):
    user = request.user
    subscripts = user.followers.select_related('following').all()

    if subscripts:
        recipe_authors = []
        for subscript in subscripts:
            recipe_authors.append(subscript.following)

        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes_limit = int(recipes_limit)
        sub_recipes = Recipe.objects.filter(
            author__in=recipe_authors
        ).order_by('-id')[:recipes_limit]

        paginator = LimitOffsetPagination()
        paginator.page_size = PAGE_SIZE
        page = paginator.paginate_queryset(sub_recipes, request)
        if page is not None:
            serializer = RecipeListSerializer(page, many=True,
                                              context={'request': request})
            return paginator.get_paginated_response(serializer.data)

    return Response(status=status.HTTP_200_OK)
