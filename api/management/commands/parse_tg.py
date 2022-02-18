import asyncio
import os

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
        section = models.NewsSection.objects.get(title='Медиа')
        title = f'{parse_book} - Библия - аудиоверсия - РБО'
        text_start = f'Библия - {parse_book} - аудиоверсия - Современный русский перевод Русского Библейского Общества'
        author = 'Телеграм "Слушать Библию" @bible_fj'
        media_path = 'media/books'
        audio = '<audio id="{num}" controls preload=none type="audio/mpeg" src="/{media_path}/{filename}">' \
                'not support audio</audio>'
        html = """<script>
for (let song = 1; song <= {total}; song++) {{
  var song_obj = document.getElementById(song);
  song_obj.onplay = play_start;
  song_obj.onended = play_next;
}}

function play_next(evt) {{
  evt.currentTarget.pause();
  if (evt.currentTarget.id == {total}) return;
  next_song = document.getElementById(parseInt(evt.currentTarget.id) + 1);
  next_song.load();
  next_song.play();
}}

var playing = null;
function play_start(evt) {{
  if (playing && playing.target.id !== evt.currentTarget.id) playing.target.pause();
  playing = evt;
}}
</script>"""
        client = TelegramClient('parse_tg', config['api_id'], config['api_hash'])
        async with client:
            text = text_start + '\n\n'
            right_book = False
            num = 0
            async for message in client.iter_messages(config['channel'], reverse=True):
                if message.audio:
                    book = message.audio.attributes[0].performer
                    if book == parse_book:
                        num += 1
                        if not right_book:
                            right_book = True
                        part = message.audio.attributes[0].title
                        # file_name = message.audio.attributes[1].file_name
                        path = await message.download_media()
                        os.replace(path, f"{media_path}/{path}")
                        text += f'{message.text}\n{audio.format(num=num, filename=path, media_path=media_path)}\n\n'
                        print(book, part, path, message.text[:20])
                    elif right_book:
                        break
                    else:
                        print(book, message.text[:20])
                elif message.text:
                    print(message.text[:20])
        news = models.News.objects.create(
            section=section, author_profile=models.Main.objects.first().profile,
            title=title, text=text, html=html.format(total=num), author=author
        )
        print(news.pk)
