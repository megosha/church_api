import asyncio

from django.core.management.base import BaseCommand
from telethon import TelegramClient

from api import models


class Command(BaseCommand):
    def handle(self, *args, **options):
        config = models.Config.command('parse_tg')
        if not config or not ('api_id' in config and 'api_hash' in config and 'channel' in config):
            print('parse_tg settings not found, example: '
                  '{"parse_tg": {"api_id": "api_id", "api_hash": "api_hash", "channel": "channel"}}')
            return
        asyncio.run(self.parse_channel(config))

    async def parse_channel(self, config: dict):
        parse_book = 'Исход'
        client = TelegramClient('parse_tg', config['api_id'], config['api_hash'])
        async with client:
            right_book = False
            async for message in client.iter_messages(config['channel'], reverse=True):
                if message.audio:
                    book = message.audio.attributes[0].performer
                    if book == parse_book:
                        if not right_book:
                            right_book = True
                        part = message.audio.attributes[0].title
                        file_name = message.audio.attributes[1].file_name
                        text = message.text
                        path = await message.download_media()
                        # TODO переместить файл в медиа, создать модель, прописать js
                        print(book, part, file_name, text[:10])
                    elif right_book:
                        break
                    print(book, message.text[:10])
                else:
                    print(message.text[:20])
