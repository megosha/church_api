from django.template.loader import render_to_string
from django.views import View
from django.shortcuts import render, redirect

from api import models

# TODO news section
class IndexView(View):
    def get(self, request):
        news = render_to_string('include/news.html', {'news': models.News.objects.all()})
        context = {
            'news': news,
        }
        return render(request, 'index.html', context)


class NewsSectionView(View):
    def get(self, request, pk):
        try:
            newssection = render_to_string('include/newssection.html', {
                'newssection': models.NewsSection.objects.get(pk=pk),
                'newssection_all': models.NewsSection.objects.filter(active=True)
            })
        except Exception as Ex:
            print(Ex)
            return redirect('/')
        context = {
            'newssection': newssection,
        }
        return render(request, 'newssection.html', context)


class ArticleView(View):
    def get(self, request, pk):
        try:
            article = render_to_string('include/article.html', {'article': models.News.objects.get(pk=pk)})
        except Exception as Ex:
            print(Ex)
            return redirect('/')
        context = {
            'article': article
        }
        return render(request, 'article.html', context)


class StaticView(View):
    def get(self, request):
        path = request.path[1:] + '.html'
        try:
            return render(request, path)
        except Exception as Ex:
            print(Ex)
            return redirect('/')
