import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_api.settings')

app = Celery('church_api')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.task_default_queue = 'default'
