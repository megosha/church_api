from django.core.management.base import BaseCommand

from api import models


class Command(BaseCommand):

    def handle(self, *args, **options):
        titles = 'Ветхий Завет', 'Новый Завет'
        for title in titles:
            print(title)
            news = models.NewsSection.objects.get(title=title).news_set.exclude(title='Бытие')
            for article in news:
                print(article.title)
                text = ''
                chapter = 1
                for line in article.text.splitlines():
                    if line == '':
                        text += f'\nГлава {chapter}\n'
                        chapter += 1
                    else:
                        text += f'{line}\n'
                article.text = text
                article.save()
