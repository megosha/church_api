from django.template.loader import render_to_string
from django.views import View
from django.shortcuts import render, redirect

from api import models
from front import forms, methods


class WriterView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            request.session['message'] = 'Вы должны войти, чтобы редактировать статью'
            return redirect('/auth/login/')
        if 'id' in request.GET:
            try:
                article = models.News.objects.get(pk=request.GET['id'])
            except Exception as Ex:
                print(Ex)
                return redirect('/')
        else:
            article = models.News()
        context = {
            'article': article,
            'section_list': models.NewsSection.objects.filter(active=True)
        }
        return render(request, 'writer.html', context)

    def post(self, request):
        profile = request.user.profile
        form = forms.ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
        return redirect('/account')


class ProfileView(View):
    def get(self, request, pk):
        if not request.user.is_authenticated:
            request.session['message'] = 'Вы должны войти, чтобы увидеть профиль пользователя'
            return redirect('/auth/login/')
        profile = models.Profile.objects.filter(pk=pk).first()
        if not profile:
            request.session['message'] = 'Пользователь не найден'
            # TODO нет вывода сообщения
            return redirect('/')
        profile_html = render_to_string('include/profile.html', {
            'item': profile
        }, request)
        context = {
            'profile_html': profile_html,
            'profile': profile
        }
        return render(request, 'profile.html', context)


class IndexView(View):
    def get(self, request):
        context = {
            'news': models.News.objects.filter(active=True)[:10],
            'main': models.Main.get_solo(),
            'title': models.Main.get_solo().title
        }
        if 'message' in request.session:
            del request.session['message']
        return render(request, 'index.html', context)


class AccountView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/auth/login/')
        profile, created = models.Profile.objects.get_or_create(user=request.user)
        if created:
            methods.fill_social(profile)
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
            'command': models.Profile.objects.filter(position__lt=90, active=True).order_by('position')
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
            request.session['message'] = 'Статья не найдена'
            print(Ex)
            return redirect('/news')
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
