from time import sleep
import logging

import telegram
from emoji import emojize
from django.core.management.base import BaseCommand

from api import models
from front.methods import get_token


class Command(BaseCommand):
    update_id = None
    phraze = None

    def handle(self, *args, **options):
        bot = telegram.Bot(get_token())
        self.phraze = get_token(True)
        try:
            self.update_id = bot.get_updates()[0].update_id
        except IndexError:
            self.update_id = None
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        while True:
            try:
                self.listen(bot)
            except telegram.error.NetworkError:
                sleep(1)
            except telegram.error.Unauthorized:
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
