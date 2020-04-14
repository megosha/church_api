from django.urls import include, path
from rest_framework import routers

from api import views


router = routers.DefaultRouter()
router.register(r'profile', views.ProfileViewSet, basename='profile')
router.register(r'news', views.NewsViewSet, basename='news')

urlpatterns = [
    path('form/', views.FormViewSet.as_view()),
    path('robokassa/', views.RobokassaViewSet.as_view()),
    path('account/', views.AccountViewSet.as_view()),
    path('log/', views.LogViewSet.as_view()),
    path('', include(router.urls)),
]
