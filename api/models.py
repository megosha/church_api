from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Profile(models.Model):
    class Meta:
        ordering = ('position',)
    name = models.CharField(max_length=255, blank=True, default='')
    function = models.CharField(max_length=255, blank=True, default='')
    image = models.ImageField(blank=True, null=True)
    about = models.TextField(blank=True, default='')
    active = models.BooleanField(default=True)
    position = models.SmallIntegerField(default=-10)
    phone = models.CharField(max_length=32, blank=True, default='')
    social_email = models.CharField(max_length=64, blank=True, default='')
    social_page = models.CharField(max_length=64, blank=True, default='')
    social_vk = models.CharField(max_length=64, blank=True, default='')
    social_fb = models.CharField(max_length=64, blank=True, default='')
    social_ok = models.CharField(max_length=64, blank=True, default='')
    social_insta = models.CharField(max_length=64, blank=True, default='')
    social_youtube = models.CharField(max_length=64, blank=True, default='')

    def __str__(self):
        return f'{self.position} - {self.name}'
