from django.urls import path, re_path

from front import views


urlpatterns = [
    re_path(r'', views.StaticView.as_view()),
]
