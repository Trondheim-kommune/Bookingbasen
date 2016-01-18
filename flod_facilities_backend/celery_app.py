#!/usr/bin/env python

# -*- coding: utf-8 -*-

from celery import Celery
celery_app = Celery()
celery_app.config_from_object('celeryconfig')
