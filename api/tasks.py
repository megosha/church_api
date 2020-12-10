import requests

from church_api.celery import app
from front import methods


@app.task(name="api.tasks.time_to_pray", ignore_result=True)
def time_to_pray():
    token = methods.TGram.get_token()
    result = requests.get(f'https://api.telegram.org/bot{token}/sendMessage', params=dict(
        chat_id='@memberbook',
        text='Hello world!'
    ))
