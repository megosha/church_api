from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models, transaction
from django.utils import timezone
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from rest_framework.authtoken.models import Token
from solo.models import SingletonModel
from sorl.thumbnail import ImageField


class Site(models.Model):
    name = models.CharField(max_length=64, default='Барнаул')
    domain = models.CharField(max_length=64, default='church22.ru', unique=True)
    path_prefix = models.CharField(max_length=64, default='', help_text='biysk/', blank=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} - {self.domain}'

    def add_prefix(self, path):
        return self.path_prefix + path


class Main(models.Model):
    site = models.OneToOneField(Site, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255, default='')
    welcome = models.TextField(default='', blank=True)
    youtube = models.CharField(max_length=16, default='', blank=True)
    profile = models.ForeignKey('Profile', on_delete=models.SET_NULL, null=True, blank=True)
    on_map = models.TextField(default='', blank=True)
    requisite = models.TextField(default='', blank=True)
    all_command = ImageField(blank=True, null=True,
                             validators=[FileExtensionValidator(allowed_extensions=('jpg', 'jpeg'))])
    no_redirect_count = models.IntegerField(default=3)

    def __str__(self):
        return str(self.site)


class Config(SingletonModel):
    tgram = models.JSONField(default=dict)
    commands = models.JSONField(default=dict)

    @classmethod
    def command(cls, command: str) -> dict:
        return cls.get_solo().commands.get(command, dict())


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    site = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True, blank=True)
    bot_user = models.OneToOneField('BotContact', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255, blank=True, default='')
    birthday = models.DateField(null=True, blank=True)
    function = models.CharField(max_length=255, blank=True, default='')
    image = ImageField(blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=('jpg', 'jpeg'))])
    about = models.TextField(blank=True, default='')
    active = models.BooleanField(default=True)
    city = models.CharField(max_length=64, blank=True, default='')
    phone = models.CharField(max_length=32, blank=True, default='')
    phone_visible = models.BooleanField(default=False, blank=True)
    social_email = models.CharField(max_length=64, blank=True, default='')
    social_page = models.CharField(max_length=64, blank=True, default='')
    social_vk = models.CharField(max_length=64, blank=True, default='')
    social_fb = models.CharField(max_length=64, blank=True, default='')
    social_ok = models.CharField(max_length=64, blank=True, default='')
    social_insta = models.CharField(max_length=64, blank=True, default='')
    social_youtube = models.CharField(max_length=64, blank=True, default='')
    telegram = models.CharField(max_length=64, blank=True, default='')
    position = models.SmallIntegerField(default=100)
    data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = 'position', 'site', 'name'

    def __str__(self):
        return f'{self.position} - {self.name}'

    @classmethod
    def get_data(cls, profile_id, key: str = None):
        data = cls.objects.only('data').get(id=profile_id).data
        if key:
            return data.get(key)
        return data

    @classmethod
    def set_data(cls, profile_id, key, value):
        cls.objects.filter(id=profile_id).update(data=models.Func(
            models.F("data"), models.Value([key]), models.Value(value, models.JSONField()), function="jsonb_set"))


class Form(models.Model):
    site = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=32, default='')
    text = models.TextField(default='')
    sended = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.title


class NewsSection(models.Model):
    NEWS = 'news'
    BOOKS = 'books'
    MEDIA = 'media'
    MEDIAS = (NEWS, NEWS), (MEDIA, MEDIA), (BOOKS, BOOKS)

    site = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True, blank=True)
    media = models.CharField(max_length=16, blank=True, choices=MEDIAS, default=NEWS)
    title = models.CharField(max_length=255, blank=True, default='')
    icon = models.CharField(max_length=32, default='mbri-info')
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = 'id',


class News(models.Model):
    section = models.ForeignKey(NewsSection, on_delete=models.SET_NULL, null=True, blank=True)
    author_profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(default=timezone.now, blank=True)
    title = models.CharField(max_length=255, default='')
    cover = ImageField(null=True, validators=[FileExtensionValidator(allowed_extensions=('jpg', 'jpeg'))])
    image = ImageField(blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=('jpg', 'jpeg'))])
    text = models.TextField(default='', blank=True)
    html = models.TextField(default='', blank=True)
    youtube = models.CharField(max_length=16, default='', blank=True)
    author = models.TextField(default='', blank=True)
    active = models.BooleanField(default=True)
    meter = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = '-date',

    def __str__(self):
        return self.title

    def meter_inc(self, key: str):
        if self.meter.get(key):
            self.meter[key] += 1
        else:
            self.meter[key] = 1
        self.save()
        return self.meter[key]


class BotContact(models.Model):
    chat_id = models.BigIntegerField(primary_key=True)
    username = models.CharField(max_length=255, default='', blank=True)
    title = models.CharField(max_length=255, default='', blank=True)
    rights = models.SmallIntegerField(default=0, blank=True)
    last_message = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.username} ({self.chat_id})"


class BotMessage(models.Model):
    contact = models.ForeignKey(BotContact, on_delete=models.CASCADE, null=True)
    text = models.TextField(default='', blank=True)
    image = ImageField(blank=True, null=True)
    crontab = models.CharField(max_length=255, default='*/*/*/*/*', blank=True, help_text='m/h/dM/MY/dW')

    def save(self, *args, **kwargs):
        minute, hour, day_of_month, month_of_year, day_of_week = self.crontab.split('/')
        with transaction.atomic():
            super(BotMessage, self).save(*args, **kwargs)
            crontab, created = CrontabSchedule.objects.get_or_create(
                minute=minute, hour=hour, day_of_month=day_of_month, month_of_year=month_of_year,
                day_of_week=day_of_week)
            PeriodicTask.objects.update_or_create(name=f'BotMessage {self.pk}', defaults=dict(
                crontab=crontab, task="api.tasks.say2group", args=f'["{self.text}", "{self.contact.chat_id}"]'))

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            task = PeriodicTask.objects.get(name=f'BotMessage {self.pk}')
            if task.crontab.periodictask_set.count() == 1:
                task.crontab.delete()
            else:
                task.delete()
            super(BotMessage, self).delete(*args, **kwargs)
