import time

from api.tasks import log, say2boss
from church_api.celery import app
from mailing import models


@app.task(name="mailing.tasks.congratulation", ignore_result=True)
def congratulation():
    for conf in models.SmsConfig.objects.all():
        with log(conf.site.name):
            if balance := conf.balance() < 50:
                say2boss(f'smsaero.ru balance is low ({balance})')
            if msg_ids := conf.mailing():
                for msg_id in msg_ids:
                    while (status := conf.status(msg_id)) not in conf.FINAL_STATUSES:
                        time.sleep(3)
                    say2boss(f'Status {msg_id}: {dict(conf.STATUSES).get(status)}')
