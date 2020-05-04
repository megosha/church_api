from django.contrib import admin
from django.apps import apps
from solo.admin import SingletonModelAdmin

from api import models


admin.site.register(models.Main, SingletonModelAdmin)


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["name", "position", "active"]


@admin.register(models.News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ["date", "title", "section", "active"]


@admin.register(models.Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ["created", "title", "sended"]


skip_models = ('authtoken.Token.objects', 'account.EmailAddress.objects', 'socialaccount.SocialApp.objects',
               'socialaccount.SocialToken.objects', 'socialaccount.SocialAccount.objects')
skip_app = 'social_django'
apps_models = apps.get_models()
for model in apps_models:
    model_objects = str(model.objects)
    if model_objects in skip_models or model_objects.startswith(skip_app):
        continue
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
