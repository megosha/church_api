from django.contrib import admin
from django.apps import apps
from django.utils.safestring import mark_safe
from solo.admin import SingletonModelAdmin

from api import models


# admin.site.register(models.Main, SingletonModelAdmin)
admin.site.register(models.Config, SingletonModelAdmin)


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["name", "position", "active"]


@admin.register(models.News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ["date", "title", "section", "active"]
    readonly_fields = ["cover_img", "image_img"]

    def cover_img(self, obj: models.News):
        return mark_safe(f'<img src="{obj.cover.url}" width="200px">')

    def image_img(self, obj: models.News):
        return mark_safe(f'<img src="{obj.image.url}" width="200px">')


@admin.register(models.Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ["created", "title", "sended"]


skip_models = ('authtoken.Token.objects', 'account.EmailAddress.objects', 'socialaccount.SocialApp.objects',
               'socialaccount.SocialToken.objects', 'socialaccount.SocialAccount.objects',
               'django_celery_beat.IntervalSchedule.objects', 'django_celery_beat.CrontabSchedule.objects',
               'django_celery_beat.SolarSchedule.objects', 'django_celery_beat.ClockedSchedule.objects',
               'django_celery_beat.PeriodicTask.objects',)
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
