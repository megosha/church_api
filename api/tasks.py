import requests
import logging

from church_api.celery import app
from front import methods

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


@app.task(name="api.tasks.time_to_pray", ignore_result=True)
def time_to_pray():
    logger = logging.getLogger(__name__)
    logger.info("time_to_pray start")
    token = methods.TGram.get_token()
    chat_id = methods.get_set('TTP_ID')
    text = methods.get_set('TTP_TEXT')
    result = requests.get(f'https://api.telegram.org/bot{token}/sendMessage', params=dict(
        chat_id=chat_id,
        text=text
    ))
    logger.info(f"time_to_pray end: {result}")


@app.task(name="api.tasks.say2boss", ignore_result=True)
def say2boss(text):
    logger = logging.getLogger(__name__)
    logger.info("say2boss start")
    result = methods.TGram.say2boss(text)
    logger.info(f"say2boss end: {result}")


@app.task(name="api.tasks.send_email", ignore_result=True)
def send_email(title, text, emails=None, as_html=False):
    logger = logging.getLogger(__name__)
    logger.info(f"send_email start ('{title}', {emails})")
    result = methods.send_email(title, text, emails, as_html)
    logger.info(f"send_email end: {result}")
