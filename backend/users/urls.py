from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomUserModelViewSet

v1_router = DefaultRouter()
v1_router.register('users', CustomUserModelViewSet)

urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
