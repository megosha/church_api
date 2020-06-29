import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from emoji import emojize
from django.core.management.base import BaseCommand

from api import models
from front.methods import TGram


class Command(BaseCommand):
    logger = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def handle(self, *args, **options):
        # next https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/nestedconversationbot.py
        updater = Updater(TGram.get_token(), use_context=True)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("set", self.set_boss))
        dp.add_handler(CommandHandler("boss", self.who_boss))
        dp.add_handler(MessageHandler(Filters.text, self.on_board))
        updater.start_polling()
        updater.idle()

    @staticmethod
    def on_board(update, context):
        update.message.reply_text(emojize('Bot on board!'))

    @staticmethod
    def who_boss(update, context):
        config = models.Config.get_solo()
        update.message.reply_text(config.tgram.get('boss_name', 'No BOSS('))

    @staticmethod
    def set_boss(update, context):
        if update.message.text == '/set ' + TGram.get_token(True):
            config = models.Config.get_solo()
            config.tgram['boss_id'] = update.message.chat_id
            config.tgram['boss_name'] = update.message.chat.username
            config.save()
            update.message.reply_text(emojize(f'You BOSS 🐧:cat_face:'))
