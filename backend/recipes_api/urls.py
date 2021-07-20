from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeListViewSet, user_subscriptions,
                    SubscriptionViewSet, TagViewSet)


router_v1 = DefaultRouter()
router_v1.register('ingredients', IngredientViewSet)
router_v1.register('tags', TagViewSet)
router_v1.register('recipes', RecipeListViewSet)

urlpatterns = [
    path('users/<int:id>/subscribe/', SubscriptionViewSet.as_view()),
    path('users/subscriptions/', user_subscriptions),
    path('', include(router_v1.urls)),
]
