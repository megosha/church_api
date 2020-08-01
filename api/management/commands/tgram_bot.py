import logging

import requests
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.utils import timezone
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from emoji import emojize
from django.core.management.base import BaseCommand

from api import models
from front import methods


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
        updater = Updater(methods.TGram.get_token(), use_context=True)
        dp = updater.dispatcher

        article_handler = ConversationHandler(
            entry_points=[CommandHandler('article', self.article)],
            states={
                0: [MessageHandler(Filters.regex('^(Раздел|Заголовок|Обложка|Статья|YouTube)$'),
                                   self.article_choice)],
                1: [MessageHandler(Filters.text, self.article_typing)],
            },
            fallbacks=[MessageHandler(Filters.regex('^Отмена'), self.article_cancel)]
        )
        broadcast_handler = ConversationHandler(
            entry_points=[CommandHandler('broadcast', self.broadcast)],
            states={
                0: [CommandHandler('broadcast', self.broadcast), MessageHandler(Filters.text, self.broadcast_action)]
            },
            fallbacks=[MessageHandler(Filters.regex('^Отмена'), self.article_cancel)]
        )

        dp.add_handler(broadcast_handler)
        dp.add_handler(article_handler)
        # dp.add_handler(CommandHandler("broadcast", self.broadcast))
        dp.add_handler(CommandHandler("set", self.set_boss))
        dp.add_handler(CommandHandler("boss", self.who_boss))
        dp.add_handler(CommandHandler("help", self.help))
        dp.add_handler(MessageHandler(Filters.text, self.on_board))

        updater.start_polling()
        updater.idle()

    @staticmethod
    def broadcast(update, context):
        config = models.Config.get_solo()
        if config.tgram.get('boss_name') != update.message.chat.username:
            update.message.reply_text(emojize('You are not Boss :suspect:'))
            return
        #     return [InlineKeyboardButton(i, callback_data=f'/{i}') for i in l]
        # keyboard = [Command.append_slash(i) for i in Command.get_keys(context)]
        # reply_markup=InlineKeyboardMarkup(keyboard)
        keyboard = [[InlineKeyboardButton('Отмена', callback_data='2')]]
        update.message.reply_text('Публикуем трансляцию и статью на сайт. Введите ссылку трансляции YouTube',
                                  reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
        return 0

    @staticmethod
    def youtube_get_id(link: str):
        youtube_id = link.split('/')[-1].split('=')[-1]
        if len(youtube_id) == 11:
            return youtube_id

    @staticmethod
    def broadcast_action(update, context):
        youtube_id = Command.youtube_get_id(update.message.text)
        if not youtube_id:
            update.message.reply_text(f'youtube_id не найден')
            return ConversationHandler.END
        API_KEY = methods.get_set('GOOGLE_API_KEY')
        # preview = f'https://img.youtube.com/vi/{youtube_id}/maxresdefault.jpg'
        url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={youtube_id}&key={API_KEY}'
        try:
            data = requests.get(url).json()
            title = data['items'][0]['snippet']['title']
            preview = data['items'][0]['snippet']['thumbnails']['maxres']['url']
            cover = NamedTemporaryFile(delete=True)
            cover.write(requests.get(preview).content)
            cover.flush()
        except Exception as Ex:
            update.message.reply_text(f'Не удалось получить данные: {Ex}')
            return ConversationHandler.END
        try:
            article_title = title.split('"')[1] + ' - Трансляция'
        except:
            article_title = title
        section = models.NewsSection.objects.filter(title='Видео').first()
        if not section:
            section = models.NewsSection.objects.first()
        author = models.Profile.objects.filter(telegram=update.message.chat.username).first()
        article = models.News.objects.create(section=section, author_profile=author, date=timezone.now(),
                                             title=article_title, youtube=youtube_id)
        article.cover.save(f'broadcast_{article.pk}', File(cover))
        models.Main.objects.update(youtube=youtube_id)
        update.message.reply_text(f'Ссылка обновлена на: {youtube_id}')
        # logger.info("Location of %s: %s", user.first_name, update.message.text)
        update.message.reply_text(emojize('200 OK :thumbs_up:'))
        return ConversationHandler.END

    @staticmethod
    def broadcast_cancel(update, context):
        # user = update.message.from_user
        # logger.info("User %s canceled the conversation.", user.first_name)
        # update.message.reply_text('Bye! Hope to see you again next time.',
        #                           reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

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
    def get_commands(context):
        commands = []
        for h in context.dispatcher.handlers[0]:
            if hasattr(h, 'command'):
                commands.extend(h.command)
            elif hasattr(h, 'entry_points'):
                commands.extend(h.entry_points[0].command)
        return commands

    @staticmethod
    def append_slash(l: list):
        return [f'/{i}' for i in l]

    @staticmethod
    def get_keys(context):
        command = []
        entry_points = []
        for h in context.dispatcher.handlers[0]:
            if hasattr(h, 'command'):
                command.extend(h.command)
            elif hasattr(h, 'entry_points'):
                entry_points.extend(h.entry_points[0].command)
        return [Command.append_slash(command), Command.append_slash(entry_points)]

    @staticmethod
    def help(update, context):
        update.message.reply_text(f'Commands: {", ".join(Command.get_commands(context))}')

    # @staticmethod
    # def append_slash(l: list):
    #     return [InlineKeyboardButton(i, callback_data=f'/{i}') for i in l]
    # keyboard = [Command.append_slash(i) for i in Command.get_keys(context)]
    # reply_markup=InlineKeyboardMarkup(keyboard)

    @staticmethod
    def on_board(update, context):
        update.message.reply_text(
            emojize('Bot on board!'),
            reply_markup=ReplyKeyboardMarkup(Command.get_keys(context), one_time_keyboard=True)
        )

    @staticmethod
    def who_boss(update, context):
        config = models.Config.get_solo()
        update.message.reply_text(config.tgram.get('boss_name', 'No BOSS('))

    @staticmethod
    def set_boss(update, context):
        if update.message.text == '/set ' + methods.TGram.get_token(True):
            config = models.Config.get_solo()
            config.tgram['boss_id'] = update.message.chat_id
            config.tgram['boss_name'] = update.message.chat.username
            config.save()
            update.message.reply_text(emojize(f'You BOSS 🐧:cat_face:'))
        else:
            update.message.reply_text('Wrong argument')
