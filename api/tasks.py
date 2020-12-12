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
