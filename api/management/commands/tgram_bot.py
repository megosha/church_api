from time import sleep

from django.core.management.base import BaseCommand

import logging

import requests
import telegram
from telegram.error import NetworkError, Unauthorized
from emoji import emojize
from django.conf import settings

from api import models


def say2boss(text):
    boss_id = models.Config.get_solo().tgram.get('boss_id')
    if not boss_id:
        print('BOSS not found')
        return None
    url = f'https://api.telegram.org/bot{Command.get_token()}/sendMessage?chat_id={boss_id}&parse_mode=Markdown&text={text}'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f'status_code {response.status_code}')
    except Exception as Ex:
        print(Ex)
        return False


class Command(BaseCommand):
    update_id = None
    phraze = None

    @staticmethod
    def get_token(phraze=False):
        if not settings.configured:
            settings.configure()
        if phraze:
            return settings.TGRAM_PHRAZE
        return settings.TGRAM_TOKEN

    def handle(self, *args, **options):
        bot = telegram.Bot(self.get_token())
        self.phraze = self.get_token(True)
        try:
            self.update_id = bot.get_updates()[0].update_id
        except IndexError:
            self.update_id = None
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        while True:
            try:
                self.listen(bot)
            except NetworkError:
                sleep(1)
            except Unauthorized:
                self.update_id += 1

    def listen(self, bot):
        for update in bot.get_updates(offset=self.update_id, timeout=10):
            self.update_id = update.update_id + 1
            if update.message:
                if update.message.text == self.phraze:
                    config = models.Config.get_solo()
                    config.tgram['boss_id'] = update.message.chat_id
                    config.tgram['boss_name'] = update.message.chat.username
                    config.save()
                    update.message.reply_text(emojize(f'You BOSS 🐧:cat_face:'))
                elif update.message.text == 'who boss':
                    config = models.Config.get_solo()
                    update.message.reply_text(config.tgram.get('boss_name', 'No BOSS('))
                else:
                    update.message.reply_text(emojize('i hear you 🐧:cat_face:'))
