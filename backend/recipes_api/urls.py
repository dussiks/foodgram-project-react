from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router_v1 = DefaultRouter()
router_v1.register('ingredients', views.IngredientViewSet)
router_v1.register('tags', views.TagViewSet)
router_v1.register('recipes', views.RecipeViewSet)

urlpatterns = [
    path('recipes/<int:pk>/favorite/', views.FavoriteViewSet.as_view()),
    path('recipes/<int:pk>/shopping_cart/',
         views.ShoppingCartViewSet.as_view()),
    path('users/<int:pk>/subscribe/', views.SubscriptionViewSet.as_view()),
    path('users/subscriptions/', views.user_subscriptions),
    path('', include(router_v1.urls)),
]
