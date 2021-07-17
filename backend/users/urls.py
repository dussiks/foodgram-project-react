from django.urls import include, path

urlpatterns = [
    path('', include('djoser.urls')),
    path('users/subscriptions/', ),
    path('auth/', include('djoser.urls.authtoken')),
]
