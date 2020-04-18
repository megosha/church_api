from django.urls import path, re_path

from front import views


urlpatterns = [
    path('', views.IndexView.as_view()),
    re_path(r'', views.StaticView.as_view()),
]
