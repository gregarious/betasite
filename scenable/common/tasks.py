# Project-wide celery tasks

from celery import task


# temp. sample for celery testing
@task
def add(x, y):
    return x + y
