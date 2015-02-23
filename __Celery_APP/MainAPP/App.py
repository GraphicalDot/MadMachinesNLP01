#!/usr/bin/env python
#-*- coding: utf-8 -*-
from __future__ import absolute_import
from celery import Celery
import os

tasks_path = "{0}/ProcessingCeleryTask".format(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('CELERY_CONFIG_MODULE', 'MainAPP.celeryconfig')

app = Celery("MainAPP",
            include=[tasks_path])

app.config_from_envvar('CELERY_CONFIG_MODULE')


if __name__ == "__main__":
	app.start()
