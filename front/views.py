from datetime import datetime

import os
import requests
from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.dateparse import parse_date
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
    @staticmethod
    def save_image(model, url, provider='no'):
        fname = f"profile_{model.pk}_{provider}.jpg"
        cover = os.path.join(settings.MEDIA_ROOT, fname)
        with open(cover, 'wb+') as dest:
            preview = requests.get(url)
            dest.write(preview.content)
            model.image.save(fname, dest)


    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/auth/login/')
        profile, created = models.Profile.objects.get_or_create(user=request.user)
        if created:
            social_account = SocialAccount.objects.filter(user=request.user).first()
            if social_account:
                data = social_account.extra_data
                if social_account.provider == 'vk':
                    profile.social_vk = f'https://vk.com/id{data["id"]}'
                    profile.name = f"{data.get('first_name', '')} {data.get('last_name', '')}"
                    profile.city = data['city'].get('title', '') if data.get('city') else ''
                    if data.get('bdate'):
                        profile.birthday = datetime.strptime(data.get('bdate'), '%d.%m.%Y').date()
                    if data.get('email'):
                        profile.social_email = data['email']
                    if data.get('photo_max_orig'):
                        self.save_image(profile, data['photo_max_orig'], social_account.provider)
                    profile.social_vk = f'https://ok.ru/profile/{data["uid"]}'
                elif social_account.provider == 'odnoklassniki':
                    profile.social_ok = f'https://ok.ru/profile/{data["uid"]}'
                    profile.name = data.get('name', '')
                    profile.city = data['location'].get('city', '') if data.get('location') else ''
                    if data.get('birthday'):
                        profile.birthday = datetime.strptime(data.get('birthday'), '%Y-%m-%d').date()
                    if data.get('pic1024x768'):
                        self.save_image(profile, data['pic1024x768'], social_account.provider)
                elif social_account.provider == 'google':
                    profile.name = data.get('name', '')
                    if data.get('picture'):
                        self.save_image(profile, data['picture'], social_account.provider)
                    if data.get('email'):
                        profile.social_email = data['email']
                elif social_account.provider == 'facebook':
                    pass
                profile.save()
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
