from django.template.loader import render_to_string
from django.views import View
from django.shortcuts import render, redirect

from api import models
from front import forms


class IndexView(View):
    def get(self, request):
        news = render_to_string('include/news.html', {
            'news': models.News.objects.filter(active=True)[:10]
        })
        context = {
            'news': news,
            'main': models.Main.get_solo(),
            'title': models.Main.get_solo().title
        }
        return render(request, 'index.html', context)


class AccountView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/auth/login/')
        profile, created = models.Profile.objects.get_or_create(user=request.user)
        account = render_to_string('include/account.html', {
            'item': profile
        }, request)
        context = {
            'account': account,
        }
        return render(request, 'account.html', context)

    def post(self, request):
        profile = request.user.profile
        form = forms.ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
        return redirect('/account')


class CommandView(View):
    def get(self, request):
        command = render_to_string('include/command.html', {
            'command': models.Profile.objects.filter(position__gt=0, active=True).order_by('position')
        })
        context = {
            'command': command,
        }
        return render(request, 'command.html', context)


class NewsSectionView(View):
    def get(self, request, pk):
        news_section = models.NewsSection.objects.filter(pk=pk).first()
        if not news_section:
            news_section = models.NewsSection.objects.first()
        try:
            newssection = render_to_string('include/newssection.html', {
                'newssection': news_section,
                'newssection_all': models.NewsSection.objects.filter(active=True, news__active=True).distinct()
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
            article = models.News.objects.get(pk=pk)
            article_html = render_to_string('include/article.html', {
                'article': article,
                'newssection_all': models.NewsSection.objects.filter(active=True, news__active=True).distinct()
            })
        except Exception as Ex:
            print(Ex)
            return redirect('/')
        context = {
            'article': article_html,
            'title': article.title
        }
        return render(request, 'article.html', context)


class StaticView(View):
    def get(self, request):
        path = request.path[1:] + '.html'
        context = {
            'main': models.Main.get_solo(),
            'title': models.Main.get_solo().title
        }
        try:
            return render(request, path, context)
        except Exception as Ex:
            print(Ex)
            return redirect('/')
