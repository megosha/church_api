import logging
from datetime import datetime

import requests
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.utils import timezone
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from emoji import emojize
from django.core.management.base import BaseCommand

from api import models
from api.tasks import say2boss
from front import methods


class Command(BaseCommand):
    logger = None
    article_markup = ReplyKeyboardMarkup([
        ['Раздел', 'Заголовок', 'Обложка', 'Статья', 'YouTube'],
        ['Опубликовать', 'Отмена']
    ], one_time_keyboard=True)
    user_commands = ReplyKeyboardMarkup([
        ['/time_offset_start']
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
        time_offset_handler = ConversationHandler(
            entry_points=[CommandHandler('time_offset_start', self.time_offset_start)],
            states={
                1: [MessageHandler(Filters.text, self.time_offset_1)],
                2: [MessageHandler(Filters.text, self.time_offset_2)],
                3: [MessageHandler(Filters.text, self.time_offset_repeat)],
                0: [MessageHandler(Filters.text, self.conversation_end)]
            },
            fallbacks=[MessageHandler(Filters.regex('^/end'), self.conversation_end)]
        )

        dp.add_handler(broadcast_handler)
        dp.add_handler(time_offset_handler)
        # dp.add_handler(article_handler)
        # dp.add_handler(CommandHandler("broadcast", self.broadcast))
        # dp.add_handler(CommandHandler("set", self.set_boss))
        dp.add_handler(CommandHandler("boss", self.who_boss))
        dp.add_handler(CommandHandler("help", self.help))
        dp.add_handler(MessageHandler(Filters.text, self.on_board))

        updater.start_polling()
        updater.idle()

    @staticmethod
    def str2dt(time):
        try:
            return datetime.strptime(time, '%H:%M:%S')
        except ValueError:
            try:
                return datetime.strptime(time, '%M:%S')
            except ValueError:
                try:
                    return datetime.strptime(time, '%S')
                except ValueError:
                    raise

    def conversation_end(self, update, context):
        update.message.reply_text(
            emojize('Bot on board!'),
            reply_markup=Command.user_commands
        )
        return ConversationHandler.END

    @staticmethod
    def time_offset_start(update, context):
        keyboard = [[InlineKeyboardButton('/end', callback_data=0)]]
        update.message.reply_text('Высчитываем смещение времени.\nВведите время из первого видео (1:02:04)',
                                  reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
        return 1

    # @staticmethod
    def time_offset_1(self, update, context):
        keyboard = [[InlineKeyboardButton('/end', callback_data=0)]]
        t1 = update.message.text
        if t1 == '/end':
            return 0
        self.dt1 = Command.str2dt(t1)
        update.message.reply_text('Введите соответствующее время из второго видео (32:45)',
                                  reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
        return 2

    # @staticmethod
    def time_offset_2(self, update, context):
        keyboard = [[InlineKeyboardButton('/end', callback_data=0)]]
        t2 = update.message.text
        if t2 == '/end':
            return 0
        self.dt2 = Command.str2dt(t2)
        update.message.reply_text('Введите время из первого видео для расчета (1:22:34)',
                                  reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
        return 3

    # @staticmethod
    def time_offset_repeat(self, update, context):
        keyboard = [[InlineKeyboardButton('/end', callback_data=0)]]
        t = update.message.text
        if t == '/end':
            return 0
        dt = Command.str2dt(t)
        result = (dt - self.dt1 + self.dt2).time()
        update.message.reply_text(f'Соответствуюзее время второго видео: {result}\n'
                                  f'Введите время из первого видео для расчета (1:22:34)',
                                  reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
        return 3

    @staticmethod
    def broadcast(update, context):
        boss = models.BotContact.objects.filter(chat_id=update.effective_chat.id).first()
        if not boss or boss.rights < 10:
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
    def broadcast_action(update, context):
        youtube_id = methods.youtube_get_id(update.message.text)
        if not youtube_id:
            update.message.reply_text(f'youtube_id не найден')
            return ConversationHandler.END

        boss = models.BotContact.objects.get(chat_id=update.effective_chat.id)
        boss.profile.site.main.youtube = youtube_id
        boss.profile.site.main.save()
        update.message.reply_text(f'Ссылка обновлена на: {youtube_id}')

        try:
            title, preview = methods.youtube_get_desc(youtube_id)
            cover = NamedTemporaryFile(delete=True, suffix='.jpg')
            cover.write(requests.get(preview).content)
            cover.flush()
        except Exception as exc:
            update.message.reply_text(f'Не удалось получить данные: {exc}')
            return ConversationHandler.END
        section = models.NewsSection.objects.filter(title='Видео').first()
        if not section:
            section = models.NewsSection.objects.first()
        article = models.News.objects.create(section=section, author_profile=boss.profile.site.main.profile,
                                             date=timezone.now(), title=title, youtube=youtube_id)
        article.cover.save(f'broadcast_{article.pk}.jpg', File(cover))
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

    @staticmethod
    def on_board(update, context):
        chat_id = update.effective_chat.id
        username = update.effective_chat.username or ''
        text: str = update.effective_message.text
        bot_user, created = models.BotContact.objects.update_or_create(
            chat_id=chat_id, defaults=dict(username=username,last_message=timezone.now()))
        if chat_id < 0:
            print('Post to channel')
        else:
            print('Post to PM')
            if update.effective_message.from_user.is_bot:
                return
            if bot_user.rights > 10:
                update.message.reply_text(
                    emojize('Bot on board!'),
                    reply_markup=ReplyKeyboardMarkup(Command.get_keys(context), one_time_keyboard=True)
                )
            elif not text.startswith('/'):
                say2boss(f"{username} ({chat_id})\n{text}")
                update.message.reply_text(
                    emojize('Ваше сообщение передано боссу!'),
                    reply_markup=Command.user_commands
                )
            else:
                update.message.reply_text(
                    emojize('Bot on board!'),
                    reply_markup=Command.user_commands
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
