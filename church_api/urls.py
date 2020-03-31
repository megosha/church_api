from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from api import views


router = routers.DefaultRouter()
router.register(r'profile', views.ProfileViewSet)

urlpatterns = [
    path('form/', views.FormViewSet.as_view()),
    path('robokassa/', views.RobokassaViewSet.as_view()),
    path('', include(router.urls)),
    path('auth/', obtain_auth_token),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
