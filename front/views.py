from django.template.loader import render_to_string
from django.views import View
from django.shortcuts import render, redirect

from api import models


class IndexView(View):
    def get(self, request):
        news = render_to_string('include/news.html', {'news': models.News.objects.all()[:10]})
        context = {
            'news': news,
        }
        return render(request, 'index.html', context)


class StaticView(View):
    def get(self, request):
        path = request.path[1:] + '.html'
        try:
            return render(request, path)
        except:
            return redirect('/')
