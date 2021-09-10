from django.urls import include, path
from rest_framework import routers

from api import views

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'profile', views.ProfileViewSet, basename='profile')
router.register(r'news', views.NewsViewSet, basename='news')

urlpatterns = [
    path('form/', views.FormView.as_view()),
    path('robokassa/', views.RobokassaView.as_view()),
    path('account/', views.AccountView.as_view()),
    path('log/', views.LogView.as_view()),
    path('task/', views.TaskView.as_view(), name='task'),
    path('', include(router.urls)),
]
