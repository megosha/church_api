from django.urls import path, re_path

from front import views


urlpatterns = [
    path('', views.IndexView.as_view()),
    path('article-<int:pk>', views.ArticleView.as_view()),
    path('profile-<int:pk>', views.ProfileView.as_view()),
    path('news-<int:pk>', views.NewsSectionView.as_view()),
    path('writer/<int:pk>', views.WriterView.as_view()),
    re_path(r'^command/?$', views.CommandView.as_view()),
    re_path(r'^account/?$', views.AccountView.as_view()),
    re_path(r'^writer/?$', views.WriterView.as_view()),
    re_path(r'', views.StaticView.as_view()),
]
