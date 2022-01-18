from api.tasks import log
from church_api.celery import app
from mailing import models


@app.task(name="mailing.tasks.congratulation", ignore_result=True)
def congratulation():
    for conf in models.SmsConfig.objects.all():
        with log(conf.site.name):
            conf.mailing()
