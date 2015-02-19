#!/usr/bin/env python
#-*- coding: utf-8 -*-
from celery import Celery
import os
os.environ.setdefault('CELERY_CONFIG_MODULE', 'MainApp.celeryconfig')

app = Celery("MainApp")

app.config_from_envvar('CELERY_CONFIG_MODULE')


if __name__ == "__main__":
	app.start()
