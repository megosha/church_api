from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth-token/', obtain_auth_token),
    path('auth-api/', include('rest_framework.urls', namespace='rest_framework')),
    path('auth-social/', include('social_django.urls', namespace='social')),
    path('auth/', include('django.contrib.auth.urls')),
    path('api/', include('api.urls')),
    path("", include("front.urls")),
]
