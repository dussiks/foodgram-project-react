from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeListViewSet, TagViewSet


router_v1 = DefaultRouter()
router_v1.register('ingredients', IngredientViewSet)
router_v1.register('tags', TagViewSet)
router_v1.register('recipes', RecipeListViewSet)


urlpatterns = [
    path('', include(router_v1.urls))
]
