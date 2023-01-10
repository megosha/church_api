import time
from datetime import timedelta, datetime

from api.tasks import log, say2boss
from church_api.celery import app
from mailing import models


@app.task(name="mailing.tasks.congratulation", ignore_result=True)
def congratulation():
    timeout = timedelta(minutes=10)
    for conf in models.SmsConfig.objects.all():
        with log(conf.site.name):
            conf.check_balance()
            if msg_ids := conf.mailing():
                for msg_id in msg_ids:
                    max_time = datetime.now() + timeout
                    result = 'OK'
                    while (status := conf.status(msg_id)) not in conf.FINAL_STATUSES:
                        if datetime.now() > max_time:
                            result = 'Timeout'
                            break
                        time.sleep(30)
                    say2boss(f'Result: {result}, Status {msg_id}: {dict(conf.STATUSES).get(status)}')


@app.task(name="mailing.tasks.notification", ignore_result=True)
def notification():
    for conf in models.SmsConfig.objects.all():
        with log(conf.site.name):
            conf.check_balance()
            msg_ids = conf.notifying()
            say2boss(f'Отправлены напоминания: {len(msg_ids)}')
