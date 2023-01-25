import logging
from datetime import datetime
import string
from urllib.parse import urlparse, parse_qs

import os
import requests
from telegram.bot import Bot
from telegram.utils.helpers import escape_markdown
import youtube_dl
from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import select_template

from api import models


class TGram:

    def __init__(self):
        self._bot = Bot(self.get_token())

    @staticmethod
    def get_token(phraze=False):
        if not settings.configured:
            settings.configure()
        if phraze:
            if not settings.TGRAM_PHRAZE:
                raise Exception('Phraze not set')
            return settings.TGRAM_PHRAZE
        if not settings.TGRAM_TOKEN:
            raise Exception('Token not set')
        return settings.TGRAM_TOKEN

    @staticmethod
    def say2boss(text):
        boss_id = models.Config.get_solo().tgram.get('boss_id')
        if not boss_id:
            print('BOSS not found')
            return None
        return TGram().send_message(boss_id, text)

    def send_message(self, chat_id, text, parse_mode=None):
        try:
            return self._bot.send_message(chat_id, text, parse_mode)
        except Exception as Ex:
            print(Ex)
            return False

    def delete_message(self, chat_id, message_id):
        return self._bot.delete_message(chat_id, message_id)


def get_set(item: str):
    if not settings.configured:
        settings.configure()
    if hasattr(settings, item):
        return getattr(settings, item)


def send_email(title, text, emails: iter = ('andrey@ngbarnaul.ru',), as_html: bool = False):
    mail = EmailMultiAlternatives(title, text, settings.EMAIL_HOST_USER, emails)
    if as_html:
        mail.content_subtype = "html"
    try:
        mail.send(fail_silently=False)
    except Exception as Ex:
        return Ex


def fill_profile(request):
    profile, created = models.Profile.objects.get_or_create(user=request.user, defaults=dict(site=request.site))
    if created:
        fill_social(profile)
    return profile


def fill_social(profile: models.Profile):
    social_account = SocialAccount.objects.filter(user=profile.user).first()
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
                save_image(profile, data['photo_max_orig'], social_account.provider)
        elif social_account.provider == 'odnoklassniki':
            profile.social_ok = f'https://ok.ru/profile/{data["uid"]}'
            profile.name = data.get('name', '')
            profile.city = data['location'].get('city', '') if data.get('location') else ''
            if data.get('birthday'):
                profile.birthday = datetime.strptime(data.get('birthday'), '%Y-%m-%d').date()
            if data.get('pic1024x768'):
                save_image(profile, data['pic1024x768'], social_account.provider)
        elif social_account.provider == 'google':
            profile.name = data.get('name', '')
            if data.get('picture'):
                save_image(profile, data['picture'], social_account.provider)
            if data.get('email'):
                profile.social_email = data['email']
        elif social_account.provider == 'facebook':
            profile.social_fb = f'https://www.facebook.com/profile.php?id={data["uid"]}'
            profile.name = data.get('name', '')
            if data.get('email'):
                profile.social_email = data['email']
        profile.save()


def save_image(model, url, provider='no'):
    fname = f"profile_{model.pk}_{provider}.jpg"
    cover = os.path.join(settings.MEDIA_ROOT, fname)
    with open(cover, 'wb+') as dest:
        preview = requests.get(url)
        dest.write(preview.content)
        model.image.save(fname, dest)


def youtube_get_id(url: str) -> str:
    # Examples:
    # - http://youtu.be/SA2iWivDJiE
    # - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    # - http://www.youtube.com/embed/SA2iWivDJiE
    # - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in {'www.youtube.com', 'youtube.com'}:
        if query.path == '/watch':
            return parse_qs(query.query)['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
        if query.path[:6] == '/live/':
            return query.path.split('/')[2]


def extract_info(youtube_id):
    url = f'http://www.youtube.com/watch?v={youtube_id}'
    with youtube_dl.YoutubeDL() as ydl:
        try:
            video = ydl.extract_info(url, download=False)
        except youtube_dl.utils.DownloadError as exc:
            raise
    if 'entries' in video:
        video = video['entries'][0]  # Can be a playlist or a list of videos
    return video


def youtube_get_desc(youtube_id):
    title = None
    preview = None
    error = ''
    API_KEY = get_set('GOOGLE_API_KEY')
    if API_KEY:
        url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={youtube_id}&key={API_KEY}'
        try:
            data = requests.get(url).json()
            if 'error' in data and 'message' in data['error']:
                raise Exception(data['error']['message'])
            title = data['items'][0]['snippet']['title']
            preview = data['items'][0]['snippet']['thumbnails']['maxres']['url']
        except Exception as exc:
            error = str(exc)
    if not title:
        try:
            video = extract_info(youtube_id)
            title = video['title']
            if not preview:
                preview = video['thumbnail']
        except Exception as exc:
            error += f' | {exc}' if error else str(exc)
    if not title:
        raise Exception(error)
    if not preview:
        preview = f'https://img.youtube.com/vi/{youtube_id}/maxresdefault.jpg'
    return title, preview


def render_with_site(path: str, request, context: dict = None, update_context=False):
    context = context or {}
    if update_context:
        context.update(default_context(request))
    template = select_template([request.site.add_prefix(path), path])
    return template.render(context, request)


def default_context(request) -> dict:
    return dict(
        main=request.site.main,
        title=request.site.main.title,
        names_domains=models.Site.objects.filter(active=True).values_list('name', 'domain'),
        path=request.path,
    )


def validate_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc, result.path])
    except:
        return False


def clean_text(text: str):
    text = text.strip()
    if text.startswith('@'):
        text = text[1:]
    return text


def social_id_to_url(social_id: str, service):
    if not social_id:
        return ''
    if validate_url(social_id):
        return social_id
    social_id = clean_text(social_id)
    if '@' in social_id:
        return social_id
    d = dict(
        fb=f'https://www.facebook.com/{social_id}',
        vk=f'https://vk.com/{social_id}',
        ok=f'https://ok.ru/{social_id}',
        insta=f'https://www.instagram.com/{social_id}/',
        youtube=(f'https://www.youtube.com/channel/{social_id}' if len(social_id) >= 24
                 else f'https://www.youtube.com/{social_id}'),
        page=f'http://{social_id}',
        telegram=f'https://t.me/{social_id}',
    )
    return d[service]


def profile_social_proceed(profile: models.Profile):
    profile.social_fb = social_id_to_url(profile.social_fb, 'fb')
    profile.social_vk = social_id_to_url(profile.social_vk, 'vk')
    profile.social_ok = social_id_to_url(profile.social_ok, 'ok')
    profile.social_insta = social_id_to_url(profile.social_insta, 'insta')
    profile.social_youtube = social_id_to_url(profile.social_youtube, 'youtube')
    profile.social_page = social_id_to_url(profile.social_page, 'page')
    profile.telegram = social_id_to_url(profile.telegram, 'telegram')


def to_repr(obj):
    return ''.join(filter(lambda x: x in string.printable, str(obj)))


def dict_get(data: dict, keys: list):
    if keys[0] in data:
        return dict_get(data[keys[0]], keys[1:]) if keys else data
    return


class YouTube:
    def __init__(self):
        self.api_key = get_set('GOOGLE_API_KEY')
        self.api_prefix = 'https://www.googleapis.com/youtube/v3/'

    def get_live(self, channel_id, filter=None, raise_exception=True, log_warning=True):
        response = requests.get(
            f'{self.api_prefix}search?part=snippet&channelId={channel_id}&type=video&eventType=live&key={self.api_key}'
        )
        if response.status_code != 200:
            raise Exception(f'response.status_code: {response.status_code}')
        for item in response.json()['items']:
            video_id = item['id']['videoId']
            title = item['snippet']['title']
            if filter:
                if filter in title:
                    return video_id
            else:
                return video_id
        if log_warning:
            logging.warning(f"YouTube.get_live items({filter}) not found {response.json()}")
        if raise_exception:
            raise Exception(
                f'channel {channel_id}, filter {filter} not found. lives count {len(response.json()["items"])}')
