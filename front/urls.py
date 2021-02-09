from django.urls import path, re_path

from front import views


urlpatterns = [
    re_path(r'^/?$', views.IndexView.as_view(), name='index'),
    re_path(r'^article-(?P<pk>\d+)/?$', views.ArticleView.as_view()),
    re_path(r'^profile-(?P<pk>\d+)/?$', views.ProfileView.as_view()),
    re_path(r'^news-(?P<pk>\d+)/?$', views.NewsSectionView.as_view()),
    re_path(r'^writer-(?P<pk>\d+)/?$', views.WriterView.as_view()),
    re_path(r'^command/?$', views.CommandView.as_view()),
    re_path(r'^account/?$', views.AccountView.as_view()),
    re_path(r'^writer/?$', views.WriterView.as_view()),
    re_path(r'^profile/?$', views.ProfileView.as_view()),
    re_path(r'^article-(?P<pk>\d+)/?$', views.ArticleView.as_view(), name='article'),
    re_path(r'^r-(?P<pk>\d+/?$)|(?P<yt>\w+/?$)', views.YTRedirectView.as_view()),
]
urlpatterns.append(re_path(r'', views.StaticView.as_view()))
