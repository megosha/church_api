import logging

from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from emoji import emojize
from django.core.management.base import BaseCommand

from api import models
from front.methods import TGram


class Command(BaseCommand):
    logger = None
    article_markup = ReplyKeyboardMarkup([
        ['Раздел', 'Заголовок', 'Обложка', 'Статья', 'YouTube'],
        ['Опубликовать', 'Отмена']
    ], one_time_keyboard=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def handle(self, *args, **options):
        # next https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/nestedconversationbot.py
        updater = Updater(TGram.get_token(), use_context=True)
        dp = updater.dispatcher
        article_handler = ConversationHandler(
            entry_points=[CommandHandler('article', self.article)],
            states={
                0: [MessageHandler(Filters.regex('^(Раздел|Заголовок|Обложка|Статья|YouTube)$'),
                                   self.article_choice), ],
                1: [MessageHandler(Filters.text, self.article_typing), ],
            },
            fallbacks=[MessageHandler(Filters.regex('^Отмена'), self.article_cancel)]
        )
        dp.add_handler(article_handler)
        dp.add_handler(CommandHandler("broadcast", self.broadcast))
        dp.add_handler(CommandHandler("set", self.set_boss))
        dp.add_handler(CommandHandler("boss", self.who_boss))
        dp.add_handler(CommandHandler("help", self.help))
        dp.add_handler(MessageHandler(Filters.text, self.on_board))
        updater.start_polling()
        updater.idle()

    @staticmethod
    def article(update, context):
        update.message.reply_text("Написать статью на сайт", reply_markup=Command.article_markup)

    @staticmethod
    def article_choice(update, context):
        text = update.message.text
        context.user_data['choice'] = text
        update.message.reply_text(f'Введите {text}')
        return 1

    @staticmethod
    def article_typing(update, context):
        user_data = context.user_data
        text = update.message.text
        category = user_data['choice']
        user_data[category] = text
        del user_data['choice']
        update.message.reply_text(f"Статья: {user_data}", reply_markup=Command.article_markup)
        return 0

    @staticmethod
    def article_cancel(update, context):
        user_data = context.user_data
        if 'choice' in user_data:
            del user_data['choice']
        update.message.reply_text(f"Отмена статьи: {user_data}")
        user_data.clear()
        return ConversationHandler.END

    @staticmethod
    def broadcast(update, context):
        data = update.message.text.replace('/broadcast', '').strip()
        # data = data[data.rfind('/'):]
        update.message.reply_text(f'data: {data}')


    @staticmethod
    def help(update, context):
        commands = ', '.join([', '.join(h.command) for h in context.dispatcher.handlers[0] if hasattr(h, 'command')])
        update.message.reply_text(f'Commands: {commands}')

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
        else:
            update.message.reply_text('Wrong argument')
