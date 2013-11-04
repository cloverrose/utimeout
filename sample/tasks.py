# -*- coding:utf-8 -*-

from celery import Celery
import utimeout

celery = Celery('tasks', broker='amqp://guest@localhost//')

@celery.task
def start(cmd, timeout):
    return utimeout.start_process(cmd, timeout)
