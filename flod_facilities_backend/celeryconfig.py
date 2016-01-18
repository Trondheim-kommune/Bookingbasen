#!/usr/bin/env python

# -*- coding: utf-8 -*-

BROKER_URL = 'amqp://guest:guest@localhost:5672//'
CELERY_TIMEZONE = 'Europe/Oslo'
CELERY_TASK_SERIALIZER = 'json'
CELERY_ENABLE_UTC = False
