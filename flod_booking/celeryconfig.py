import os
from celery.schedules import crontab

# This broker acts a middleman sending and receiving messages to workers who in turn process tasks as they receive them.
BROKER_URL = 'amqp://guest:guest@localhost:5672//'
# Backend is used to keep track of task state and results.
CELERY_RESULT_BACKEND = 'amqp://guest:guest@localhost:5672//'
CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']
CELERY_TIMEZONE = 'Europe/Oslo'
CELERYBEAT_SCHEDULE = {
    'every-minute': {
        'task': 'celery_tasks.notifications_strotimer.send_notifications_strotimer_task',
        'schedule': crontab(minute='*/60')
    },
}
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ENABLE_UTC = False
# You can tell celery to run the task in sync by adding this,
# this is only meant to be in use for debugging or development stages!
if os.environ.get('DEBUG', True):
	CELERY_ALWAYS_EAGER = True