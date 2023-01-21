import inspect
import json
import logging
import time
from contextlib import contextmanager

import pytz
import requests
from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_duration, parse_datetime
from django_celery_beat.models import ClockedSchedule, PeriodicTask
from emoji import emojize

from church_api.celery import app
from front import methods
from api import models

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


@app.task(name="api.tasks.post_weather", ignore_result=True)
def post_weather(chat_id=None):
    token = methods.get_set('GISMETEO_TOKEN')
    if not token:
        return
    import locale
    locale.setlocale(locale.LC_ALL, '')
    from django.utils.timezone import activate
    activate(settings.TIME_ZONE)
    emoji_time = {4: "⛅️", 10: "☀️", 16: "🌗", 22: "🌙"}
    emoji_dir = {0: "", 1: "⬆", 2: "↗", 3: "➡", 4: "↘", 5: "⬇", 6: "↙", 7: "⬅", 8: "↖"}
    logger.info("post_weather start")
    url = 'https://api.gismeteo.net/v2/weather/forecast/by_day_part/4720/?days=3'
    response = requests.get(url, headers={'X-Gismeteo-Token': token})
    if response.status_code != requests.codes.ok:
        logger.error(f"post_weather response status_code: {response.status_code}")
        return
    now = timezone.localtime()
    text = f"Погода {now:%d %B}:\n"
    dates = response.json()['response']
    flag = False
    for date in dates:
        dt = parse_datetime(date['date']['local']).astimezone(pytz.timezone(settings.TIME_ZONE))
        if now.date() != dt.date():
            break
        if False and now > dt:
            if flag:
                continue
            url = 'https://api.gismeteo.net/v2/weather/current/4720/'
            response = requests.get(url, headers={'X-Gismeteo-Token': token})
            if response.status_code != requests.codes.ok:
                logger.error(f"post_weather response status_code: {response.status_code}")
            else:
                flag = True
                date = response.json()['response']
                dt = parse_datetime(date['date']['local'])
        comfort = date['temperature']['comfort']['C']
        air = date['temperature']['air']['C']
        desc = date['description']['full']
        humidity = date['humidity']['percent']
        pressure = date['pressure']['mm_hg_atm']
        wind = date['wind']['speed']['m_s']
        direction = date['wind']['direction']['scale_8']
        gm = date['gm']
        storm = "🌩 " if date['storm'] else ""
        text += f"\n{emoji_time.get(dt.hour, '⛅️')} {dt:%H:%M}:\n" \
                f"- Темпер. {air}, ощущ. {comfort}\n" \
                f"- Влажн. {humidity}%, давл. {pressure} мм.\n" \
                f"- Ветер {emoji_dir[direction]} {wind} м/с, г/м поле {gm}/8\n" \
                f"- {storm}{desc}\n"
    text += "\nПо данным gismeteo.ru\n\n" \
            "Благословенного дня и отличного настроения независимо от погоды!"

    chat_id = chat_id or methods.get_set('TTP_ID')
    # result = methods.TGram().send_message(chat_id, text)
    result = methods.TGram().say2boss(text)
    logger.info(f"post_weather end: {result}")


@app.task(name="api.tasks.take_meter_value", ignore_result=True)
def take_meter_value():
    logger.info("take_meter_value start")
    text = emojize('Не забудьте передать показания счётчиков. :cat_face:')
    say2group(text)


@app.task(name="api.tasks.time_to_pray", ignore_result=True)
def time_to_pray():
    logger.info("time_to_pray start")
    text = methods.get_set('TTP_TEXT')
    say2group(text)


@app.task(name="api.tasks.say2boss", ignore_result=True)
def say2boss(text):
    with log():
        methods.TGram.say2boss(text)


@app.task(name="api.tasks.send_email", ignore_result=True)
def send_email(title, text, emails=None, as_html=False):
    logger.info(f"send_email start ('{title}', {emails})")
    result = methods.send_email(title, text, emails, as_html)
    logger.info(f"send_email end: {result}")


@app.task(name="api.tasks.say2group", ignore_result=True)
def say2group(text, chat_id=None):
    logger.info("say2group start")
    chat_id = chat_id or methods.get_set('TTP_ID')
    result = methods.TGram().send_message(chat_id, text)
    logger.info(f"say2group end: {result}")


@contextmanager
def log(text='', only_warning=False):
    func = inspect.stack()[2].function
    func = f'{func} {text}' if text else func
    if not only_warning:
        logger.info(f'{func} start')
    try:
        yield
    except Exception as exc:
        logger.warning(f'{func} Exception: {exc}')
    else:
        if not only_warning:
            logger.info(f'{func} stop')


class ViewTasks:
    def __init__(self, task, profile_id, params=None, clocked_time=None):
        self.params: dict = params or dict()
        self.task = task
        self.clocked_time = clocked_time
        self.params['profile_id'] = profile_id

    @staticmethod
    def _add_task_id(p_task: PeriodicTask, kwargs: dict):
        kwargs['task_id'] = p_task.id
        p_task.kwargs = json.dumps(kwargs)
        p_task.save()

    def _proceed(self):
        task = getattr(ViewTasks, self.task)
        if not self.clocked_time:
            task.delay(**self.params)
        else:
            clocked, _ = ClockedSchedule.objects.get_or_create(clocked_time=self.clocked_time)
            p_task = PeriodicTask.objects.create(
                name=f'ViewTasks {self.task} ({self.clocked_time})', clocked=clocked, task=task.name, one_off=True,
            )
            self._add_task_id(p_task, self.params)

    @staticmethod
    @app.task(ignore_result=True)
    def start_worship(chat_id, text, youtube_live: str, profile_id, task_id=None, youtube_filter: str=None, **kwargs):
        if task_id:
            # Если это был отложенный запуск, то удалить задачу
            PeriodicTask.objects.get(id=task_id).clocked.delete()
            logger.info(f"post2group task_id: {task_id} deleted")
        for counter in range(15):
            with log('YouTube.get_live', only_warning=True) as link:
                link = methods.YouTube().get_live(youtube_live, youtube_filter, False, False)
            if link:
                break
            time.sleep(60)
        if not link:
            say2boss(f'Ошибка! Прямые эфиры не найдены')
            return
        say2boss(f'Ссылка на настройки трансляции:\nhttps://studio.youtube.com/video/{link}/livestreaming')
        text = f'{text}\nhttps://youtu.be/{link}'
        tg = methods.TGram()
        result = tg.send_message(chat_id, text)
        message_id = result['message_id']
        last_message_id = models.Profile.get_data(profile_id, 'start_worship/message_id')
        models.Profile.set_data(profile_id, 'start_worship/message_id', message_id)
        if last_message_id:
            with log('delete_message'):
                tg.delete_message(chat_id, last_message_id)

    @staticmethod
    @app.task(ignore_result=True)
    def post2group(chat_id, text, delete_after=None, task_id=None, youtube_live: str=None, youtube_filter: str=None,
                   **kwargs):
        logger.info("post2group start")
        if youtube_live:
            for counter in range(15):
                with log('YouTube.get_live', only_warning=True) as link:
                    link = methods.YouTube().get_live(youtube_live, youtube_filter, False, False)
                if link:
                    break
                time.sleep(60)
            if not link:
                if task_id:
                    PeriodicTask.objects.get(id=task_id).clocked.delete()
                    logger.info(f"post2group task_id: {task_id} deleted")
                say2boss(f'Ошибка! Прямые эфиры не найдены')
                return
            say2boss(f'Ссылка на настройки трансляции:\nhttps://studio.youtube.com/video/{link}/livestreaming')
            text = f'{text}\nhttps://youtu.be/{link}'
        result = methods.TGram().send_message(chat_id, text)
        logger.info(f"post2group result: {result}")
        if delete_after:
            logger.info("post2group delete_after start")
            task = getattr(ViewTasks, 'delete_message')
            clocked_time = timezone.now() + parse_duration(delete_after)
            clocked, _ = ClockedSchedule.objects.get_or_create(clocked_time=clocked_time)
            p_task = PeriodicTask.objects.create(
                name=f'ViewTasks post2group - delete_message ({clocked_time})', clocked=clocked, task=task.name,
                one_off=True,
            )
            ViewTasks._add_task_id(p_task, dict(chat_id=chat_id, message_id=result['message_id']))
            logger.info("post2group delete_after end")
        if task_id:
            PeriodicTask.objects.get(id=task_id).clocked.delete()
            logger.info(f"post2group task_id: {task_id} deleted")

    @staticmethod
    @app.task(ignore_result=True)
    def delete_message(chat_id, message_id, task_id=None):
        with log('delete_message'):
            methods.TGram().delete_message(chat_id, message_id)
        if task_id:
            PeriodicTask.objects.get(id=task_id).clocked.delete()
            logger.info(f"delete_message task_id: {task_id} deleted")
