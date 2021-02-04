import logging

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
