import asyncio

from django.core.management.base import BaseCommand
from telethon import TelegramClient

from api import models


class Command(BaseCommand):
    def handle(self, *args, **options):
        config = models.Config.command('parse_bible')
        if not config:
            print('parse_tg settings not found')
            return
        if not ('api_id' in config and 'api_hash' in config and 'channel' in config):
            print('parse_tg settings must include: api_id, api_hash, channel')
            return
        client = TelegramClient('parse_tg', config['api_id'], config['api_hash'])
        asyncio.run(self.parse_channel(client, config))

    async def parse_channel(self, client: TelegramClient, config: dict):
        async with client:
            async for message in client.iter_messages(config['channel'], reverse=True):
                if message.audio:
                    book = message.audio.attributes[0].performer
                    part = message.audio.attributes[0].title
                    file_name = message.audio.attributes[1].file_name
                    text = message.text
                    # path = await message.download_media()
                    print(book, part, file_name, text[:10])
                else:
                    print(message.text)
