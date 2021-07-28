#!/usr/bin/python3

from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
# pylint: disable=import-error,no-name-in-module
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'predict.settings')

app = Celery('predict')  # pylint: disable=invalid-name

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


app.conf.beat_schedule = {
    # Execute every hour
    'get-prediction': {
        'task': 'main.tasks.get_prediction',
        'schedule': crontab(minute='*/5'),
    }
}


@app.task(bind=True)
def debug_task(self):
    """ Default Debug function """
    print('Request: {0!r}'.format(self.request))
