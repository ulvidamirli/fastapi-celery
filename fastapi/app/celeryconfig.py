from celery import Celery
from celery.schedules import crontab
import logging

"""
This is the Celery configuration file. We are using RabbitMQ as the broker and
the backend. We are also scheduling a task to run every 2 hours.

To run the Celery worker, use the following command:
celery -A app.celeryconfig worker -l info

To run the Celery beat scheduler, use the following command:
celery -A app.celeryconfig beat -l info

To run both the worker and the beat scheduler, use the following command:
celery -A app.celeryconfig worker -l info -B
"""

app = Celery('celery_tutorial',
             broker='amqp://guest:guest@rabbitmq:5672/vhost',
             include=['app.task'])

app.conf.beat_schedule = {
    'run-task-every-2-hours': {
        'task': 'app.task.sample_task',
        'schedule': crontab(minute=0, hour='*/2')  # Run every 2 hours
    },
}

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
