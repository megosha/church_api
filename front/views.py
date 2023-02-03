from typing import Union

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.template import TemplateDoesNotExist
from django.template.loader import select_template
from django.utils import timezone
from django.utils.html import strip_tags
from django.views import View

from api import models
from front import forms, methods
from front.exceptions import Redirect


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
        context = dict(
            form=forms.NewsForm(instance=article),
            section_list=sections,
            footer_extend='<script src="https://cdn.tiny.cloud/1/lh4zfqr7jd1gvgc880bkn5z61dxah88ogs92zje69rgpmk0b/'
                          'tinymce/5/tinymce.min.js" referrerpolicy="origin"/></script>'
                          "<script>tinymce.init({"
                          "selector:'#article-text-id',"
                          "menubar: false,"
                          'plugins: "code lists link image emoticons",'
                          "toolbar:  'undo redo | formatselect | bold italic | alignleft aligncenter alignright "
                          "alignjustify | bullist numlist outdent indent | emoticons | removeformat "
                          "| forecolor backcolor | link image | code',"
                          "});</script>"  # "tinydrive_token_provider: '',"
        )
        return HttpResponse(methods.render_with_site('writer.html', request, context, True))

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
                request.session['message'] = 'Пользователь не найден'
                return redirect('/profile')
            profile_news = profile.news_set.filter(date__lte=timezone.now())
        else:
            profile = methods.fill_profile(request)
            profile_news = profile.news_set.all()

        context = dict(
            profile_html=methods.render_with_site('include/profile.html', request, dict(item=profile)),
            profile=profile,
            profile_news=profile_news
        )
        return HttpResponse(methods.render_with_site('profile.html', request, context, True))


class IndexView(View):

    def get(self, request):
        context = dict(
            news=models.News.objects.filter(active=True, section__active=True, section__media=models.NewsSection.NEWS,
                                            date__lte=timezone.now(), section__site=request.site)[:7],
            liders=models.Profile.objects.filter(
                position__lt=90, active=True, site=request.site).order_by('position')[:3],
            have_books=models.NewsSection.objects.filter(
                media=models.NewsSection.BOOKS, site=self.request.site).exists()
        )
        if 'message' in request.session:
            context['message'] = request.session['message']
            del request.session['message']
        return HttpResponse(methods.render_with_site('index.html', request, context, True))


class AccountView(View):

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/auth/login/')

        profile = methods.fill_profile(request)
        context = dict(
            account=methods.render_with_site('include/account.html', request, dict(item=profile))
        )
        return HttpResponse(methods.render_with_site('account.html', request, context, True))

    def post(self, request):
        profile = request.user.profile
        form = forms.ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            methods.profile_social_proceed(form.instance)
            form.save()
        return redirect('/profile')


class CommandView(View):

    def get(self, request):
        command = models.Profile.objects.filter(
            position__lt=90, active=True, site=request.site
        ).order_by('position')
        context = dict(
            command=methods.render_with_site('include/command.html', request, dict(command=command))
        )
        return HttpResponse(methods.render_with_site('command.html', request, context, True))


class PaginatorMixin:

    @staticmethod
    def paginate(qset, page, per_page=10):
        paginator = Paginator(qset, per_page)
        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)
        return items


class AudioView(View):
    pre_path = '/www/church_api/media/audio/'

    def get(self, request, path: str = ''):
        from os import listdir
        from os.path import isfile, join
        full_path = self.pre_path + path.replace('@', '/')
        dirs = sorted(listdir(full_path))
        files = {f for f in listdir(path) if isfile(join(path, f))}
        context = dict(
            dirs=dirs,
            files=files,
        )
        # TODO
        return HttpResponse(methods.render_with_site('audio.html', request, context, True))


class MediaView(View, PaginatorMixin):
    media = models.NewsSection.NEWS
    ordering = '-date'
    by_site = True

    def get(self, request, pk=None):
        self.media = request.resolver_match.url_name
        if self.media == models.NewsSection.BOOKS:
            self.ordering = 'title'
            self.by_site = False

        if pk:
            news_section = self.get_news_section(pk)
            news_qset = news_section.news_set.all()
        else:
            news_section = None
            news_qset = models.News.objects.filter(section__media=self.media)
            if self.by_site:
                news_qset = news_qset.filter(section__site=request.site)
        news_qset = news_qset.filter(active=True, date__lte=timezone.now()).order_by(self.ordering)

        news_filter = request.GET.get('filter')
        if news_filter:
            news_qset = news_qset.filter(Q(title__icontains=news_filter) | Q(text__icontains=news_filter))

        page = request.GET.get('page')
        context = dict(
            newssection=news_section,
            newssection_all=self.section_site_media_qset().filter(active=True, news__active=True).distinct(),
            news=self.paginate(news_qset, page),
            page=page,
            filter=news_filter or '',
            media=self.media,
        )
        context = dict(
            newssection=methods.render_with_site('include/newssection.html', request, context),
            media=self.media,
        )
        return HttpResponse(methods.render_with_site('newssection.html', request, context, True))

    def section_site_media_qset(self):
        qset = models.NewsSection.objects.filter(media=self.media)
        if self.by_site:
            return qset.filter(site=self.request.site)
        return qset

    def get_news_section(self, pk) -> models.NewsSection:
        news_section = self.section_site_media_qset().filter(pk=pk).first()
        if not news_section:
            news_section = self.section_site_media_qset().first()
            if not news_section:
                raise Redirect('/')
            raise Redirect(f'/{self.media.lower()}/{news_section.pk}')
        return news_section


class ArticleView(View):

    @staticmethod
    def truncatedwords(value, arg):
        return " ".join(value.split()[:arg])

    def get(self, request, pk):
        return self.render(request, pk)

    @classmethod
    def render(cls, request, pk):
        try:
            article = models.News.objects.get(pk=pk)
            if not request.user.is_authenticated or article.author_profile != request.user.profile:
                article = models.News.objects.get(pk=pk, date__lte=timezone.now())
        except Exception as exc:
            request.session['message'] = 'Статья не найдена'
            print(exc)
            return redirect('/news')

        context = dict(
            article=article,
        )
        article_html = methods.render_with_site('include/article.html', request, context)

        context = dict(
            article=article_html,
            title=article.title,
            head_extend=f"""
<meta property="og:title" content="{article.title}" />
<meta property="og:type" content="website" />
<meta property="og:url" content="{request.build_absolute_uri()}" />
<meta property="og:image" content="{request._current_scheme_host + article.cover.url}" />
<meta property="og:description" content="{cls.truncatedwords(strip_tags(article.text), 30)}" />
"""  # https://ruogp.me/ | mb https://yandex.ru/dev/share/ ?
        )
        article.meter_inc('view_count')
        return HttpResponse(methods.render_with_site('article.html', request, context))


class StaticView(View):

    def get(self, request):
        path = request.path[1:] + '.html'
        try:
            template = select_template([request.site.add_prefix(path), path])
        except TemplateDoesNotExist as exc:
            print(exc)
            return redirect('/')
        return HttpResponse(template.render(methods.default_context(request), request))


class YTRedirectView(View):

    @staticmethod
    def redirect_youtube(yt):
        return redirect(f'https://youtu.be/{yt}')

    def get(self, request, pk=None, yt=None):
        if yt:
            return self.redirect_youtube(yt)

        article = models.News.objects.filter(pk=pk).first()
        if not article:
            return redirect('index')

        no_redirect_count = request.site.main.no_redirect_count
        redirect_count = article.meter_inc('redirect_count')

        if article.youtube and redirect_count > no_redirect_count:
            return self.redirect_youtube(article.youtube)

        return redirect('article', pk=pk)


class LearnView(View):
    def get(self, request):
        # if not request.user.is_authenticated:
        #     request.session['message'] = 'Вы должны войти, чтобы увидеть профиль пользователя'
        #     return redirect('/auth/login/')
        mentors = models.Profile.objects.filter(
            site=request.site,
            is_mentor=True
        )
        context = dict(
            mentors=mentors,
        )
        return HttpResponse(methods.render_with_site('learn.html', request, context, True))
