from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from api import models
from front.methods import send_email, say2boss


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        models.Token.objects.create(user=instance)


@receiver(post_save, sender=models.News)
def create_news(sender, instance: models.News = None, created=False, **kwargs):
    if created:
        text = f'New article: {instance.author_profile} - {instance.section} - {instance.title}'
        result = say2boss(text)
        if not result:
            send_email('church22.ru - create_news', text)
