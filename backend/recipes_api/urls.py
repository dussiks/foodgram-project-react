from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (FavoriteViewSet, IngredientViewSet, RecipeViewSet,
                    ShoppingCartViewSet, SubscriptionViewSet,
                    user_subscriptions, TagViewSet)


router_v1 = DefaultRouter()
router_v1.register('ingredients', IngredientViewSet)
router_v1.register('tags', TagViewSet)
router_v1.register('recipes', RecipeViewSet)

urlpatterns = [
    path('recipes/<int:pk>/favorite/', FavoriteViewSet.as_view()),
    path('recipes/<int:pk>/shopping_cart/', ShoppingCartViewSet.as_view()),
    path('users/<int:pk>/subscribe/', SubscriptionViewSet.as_view()),
    path('users/subscriptions/', user_subscriptions),
    path('', include(router_v1.urls)),
]
