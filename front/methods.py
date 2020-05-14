import os
from datetime import datetime

import requests
from django.conf import settings
from allauth.socialaccount.models import SocialAccount

from api import models


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
            profile.social_vk = f'https://ok.ru/profile/{data["uid"]}'
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
