import json
import logging
from datetime import timedelta

from django.utils import timezone
from django.utils.dateparse import parse_duration
from django_celery_beat.models import ClockedSchedule, PeriodicTask
from emoji import emojize

from church_api.celery import app
from front import methods

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


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
    logger.info("say2boss start")
    result = methods.TGram.say2boss(text)
    logger.info(f"say2boss end: {result}")


@app.task(name="api.tasks.send_email", ignore_result=True)
def send_email(title, text, emails=None, as_html=False):
    logger.info(f"send_email start ('{title}', {emails})")
    result = methods.send_email(title, text, emails, as_html)
    logger.info(f"send_email end: {result}")


@app.task(name="api.tasks.say2group", ignore_result=True)
def say2group(text, chat_id=None):
    logger.info("say2group start")
    chat_id = chat_id or methods.get_set('TTP_ID')
    result = methods.TGram.send_message(text, chat_id)
    logger.info(f"say2group end: {result}")


@app.task(name="api.tasks.delete_message", ignore_result=True)
def delete_message(chat_id, message_id):
    logger.info("delete_message start")
    result = methods.TGram.delete_message(chat_id, message_id)
    logger.info(f"delete_message end: {result}")


class ViewTasks:
    def __init__(self, task, params=None, clocked_time=None):
        self.params: dict = params or dict()
        self.task = task
        self.clocked_time = clocked_time

    def proceed(self):
        task = getattr(ViewTasks, self.task)
        if not self.clocked_time:
            task.delay(**self.params)
        else:
            clocked, _ = ClockedSchedule.objects.get_or_create(clocked_time=self.clocked_time)
            PeriodicTask.objects.create(name=f'ViewTasks {self.task}', clocked=clocked, task=task.name, one_off=True,
                                        kwargs=json.dumps(self.params))

    @staticmethod
    @app.task(ignore_result=True)
    def post2group(chat_id, text, delete_after = None):
        response = methods.TGram.send_message(text, chat_id)
        if delete_after:
            delete_after = parse_duration(delete_after)
            clocked, _ = ClockedSchedule.objects.get_or_create(clocked_time=timezone.now() + delete_after)
            task = 'api.tasks.delete_message'
            PeriodicTask.objects.create(name=f'ViewTasks post2group - {task}', clocked=clocked, task=task, one_off=True,
                                        kwargs=json.dumps(dict(
                                            chat_id=chat_id, message_id=response['result']['message_id'])))
