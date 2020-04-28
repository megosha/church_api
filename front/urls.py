from django.urls import path, re_path

from front import views


urlpatterns = [
    path('', views.IndexView.as_view()),
    path('article-<int:pk>', views.ArticleView.as_view()),
    path('news-<int:pk>', views.NewsSectionView.as_view()),
    path('command', views.CommandView.as_view()),
    path('account', views.AccountView.as_view()),
    re_path(r'', views.StaticView.as_view()),
]
