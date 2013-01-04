# celerybeat scheduled tasks

from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    # 'runs-every-minute': {
    #     'task': 'scenable.common.tasks.add',
    #     'schedule': crontab(minute='*'),
    #     'args': (16, 16)
    # },
}
