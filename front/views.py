from typing import Union

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from django.views import View
from django.shortcuts import render, redirect

from api import models
from front import forms, methods


class WriterView(View):
    def get(self, request, pk=None):
        if not request.user.is_authenticated:
            request.session['message'] = 'Вы должны войти, чтобы редактировать статью'
            return redirect('/auth/login/')
        if pk:
            article = models.News.objects.filter(pk=pk, author_profile=request.user.profile).first()
            if not article:
                request.session['message'] = 'Статья не найдена или это не ваша статья'
                return redirect(f'/profile-{request.user.profile.pk}')
        else:
            article = models.News()
        sections = models.NewsSection.objects.filter(active=True, site=request.site)
        context = {
            'form': forms.NewsForm(instance=article),
            'section_list': sections,
            'footer_extend': '<script src="https://cdn.tiny.cloud/1/lh4zfqr7jd1gvgc880bkn5z61dxah88ogs92zje69rgpmk0b/'
                             'tinymce/5/tinymce.min.js" referrerpolicy="origin"/></script>'
                             "<script>tinymce.init({"
                             "selector:'#article-text-id',"
                             "menubar: false,"
                             'plugins: "code lists link image emoticons",'
                             "toolbar:  'undo redo | formatselect | bold italic | alignleft aligncenter alignright "
                             "alignjustify | bullist numlist outdent indent | emoticons | removeformat "
                             "| forecolor backcolor | link image | code',"
                             # "tinydrive_token_provider: '',"
                             "});</script>"
        }
        return render(request, 'writer.html', context)

    def post(self, request, pk=None):
        if not request.user.is_authenticated:
            request.session['message'] = 'Вы должны войти, чтобы редактировать статью'
            return redirect('/auth/login/')
        if pk:
            article = models.News.objects.filter(pk=pk, author_profile=request.user.profile).first()
            if not article:
                request.session['message'] = 'Статья не найдена или это не ваша статья'
                return redirect('/')
            form = forms.NewsForm(request.POST, request.FILES, instance=article)
        else:
            form = forms.NewsForm(request.POST, request.FILES)
        form.data = form.data.copy()
        if form.data.get('section') == '---':
            del form.data['section']
        if 'date' in form.data and not form.data.get('date'):
            del form.data['date']
        if 'youtube' in form.data and len(form.data['youtube']) > 11:
            form.data['youtube'] = methods.youtube_get_id(form.data['youtube'])
        if form.is_valid():
            form = form.save(commit=False)
            form.author_profile = request.user.profile
            if not request.user.is_staff:
                form.section = None
            form.save()
        return redirect(f'/profile-{request.user.profile.pk}')


class ProfileView(View):
    def get(self, request, pk=None):
        if not request.user.is_authenticated:
            request.session['message'] = 'Вы должны войти, чтобы увидеть профиль пользователя'
            return redirect('/auth/login/')
        if pk:
            profile = models.Profile.objects.filter(pk=pk).first()
            if not profile:
                # TODO request.session['message'] = 'Пользователь не найден'
                # profile = request.user.profile
                return redirect('/profile')
            profile_news = profile.news_set.filter(date__lte=timezone.now())
        else:
            profile = request.user.profile
            profile_news = profile.news_set.all()
        profile_html = render_to_string('include/profile.html', {
            'item': profile
        }, request)
        context = {
            'profile_html': profile_html,
            'profile': profile,
            'profile_news': profile_news
        }
        return render(request, 'profile.html', context)


class IndexView(View):
    def get(self, request):
        main = request.site.main
        context = {
            'news': models.News.objects.filter(active=True, date__lte=timezone.now())[:7],
            'main': main,
            'title': main.title
        }
        if 'message' in request.session:
            del request.session['message']
        return render(request, 'index.html', context)


class AccountView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/auth/login/')
        profile, created = models.Profile.objects.get_or_create(user=request.user,
                                                                default={'site': request.site})
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
        return redirect('/profile')


class CommandView(View):
    def get(self, request):
        command = models.Profile.objects.filter(
            position__lt=90, active=True, site=request.site
        ).order_by('position')
        context = {
            'command': render_to_string('include/command.html', {'command': command}),
        }
        return render(request, 'command.html', context)


class NewsSectionView(View):
    def get_news_section(self, pk) -> Union[HttpResponseRedirect, models.NewsSection]:
        news_section = models.NewsSection.objects.filter(pk=pk).first()
        if not news_section:
            news_section = models.NewsSection.objects.first()
            if not news_section:
                return redirect('/')
            return redirect(f'/news-{news_section.pk}')
        return news_section

    def paginate(self, qset, page, per_page=10):
        paginator = Paginator(qset, per_page)
        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)
        return items

    def get(self, request, pk):
        news_section = self.get_news_section(pk)
        if isinstance(news_section, HttpResponseRedirect):
            return news_section
        news_filter = request.GET.get('filter')
        news_qset = news_section.news_set.filter(active=True, date__lte=timezone.now())
        if news_filter:
            news_qset = news_qset.filter(Q(title__icontains=news_filter) | Q(text__icontains=news_filter))
        page = request.GET.get('page')
        try:
            newssection = render_to_string('include/newssection.html', {
                'newssection': news_section,
                'newssection_all': models.NewsSection.objects.filter(active=True, news__active=True).distinct(),
                'news': self.paginate(news_qset, page),
                'page': page,
                'filter': news_filter or ''
            }, request=request)
        except Exception as Ex:
            print(Ex)
            return redirect('/')
        context = {
            'newssection': newssection,
        }
        return render(request, 'newssection.html', context)


class ArticleView(View):
    @staticmethod
    def truncatedwords(value, arg):
        return " ".join(value.split()[:arg])

    def get(self, request, pk):
        try:
            article = models.News.objects.get(pk=pk)
            if not request.user.is_authenticated or article.author_profile != request.user.profile:
                article = models.News.objects.get(pk=pk, date__lte=timezone.now())
        except Exception as Ex:
            # TODO request.session['message'] = 'Статья не найдена'
            print(Ex)
            return redirect('/news-1')
        article_html = render_to_string('include/article.html', {
            'article': article,
            'newssection_all': models.NewsSection.objects.filter(active=True, news__active=True).distinct()
        }, request)
        context = {
            'article': article_html,
            'title': article.title,
            # https://ruogp.me/ | mb https://yandex.ru/dev/share/ ?
            'head_extend': f"""
<meta property="og:title" content="{article.title}" />
<meta property="og:type" content="website" />
<meta property="og:url" content="{request.build_absolute_uri()}" />
<meta property="og:image" content="{request._current_scheme_host + article.cover.url}" />
<meta property="og:description" content="{self.truncatedwords(strip_tags(article.text), 30)}" />
"""
        }
        return render(request, 'article.html', context)


class StaticView(View):
    def get(self, request):
        path = request.path[1:] + '.html'
        context = {
            'main': request.site.main,
            'title': request.site.main.title
        }
        try:
            return render(request, path, context)
        except Exception as Ex:
            print(Ex)
            return redirect('/')
