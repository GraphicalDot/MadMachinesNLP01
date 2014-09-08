#!/usr/bin/env python
from __future__ import absolute_import
from celery import states
from celery.task import Task, TaskSet
from celery.result import TaskSetResult
from celery.utils import gen_unique_id, cached_property
from celery.decorators import periodic_task
from datetime import timedelta
from celery.utils.log import get_task_logger
import time
import pymongo
import random
from celery_app.App import app
from main_scrape import scrape_links, eatery_specific


from celery import task, subtask, group
connection = pymongo.Connection()
db = connection.intermediate
collection = db.intermediate_collection


@app.task(ignore_result = True, max_retries=3, retry=True)
def eateries_list(url, number_of_restaurants, skip):
	print "got into eateries list"
	eateries_list = scrape_links(url, number_of_restaurants, skip)
	return eateries_list



@app.task(ignore_result = True, max_retries=3, retry=True)
def process_eatery(eatery_dict):
	print "got into process_eatery"
	eatery_specific(eatery_dict)
	return

@app.task(ignore_result = True, max_retries=3, retry=True)
def dmap(it, callback):
	# Map a callback over an iterator and return as a group
	callback = subtask(callback)
	return group(callback.clone([arg,]) for arg in it)()

@app.task(ignore_result = True, max_retries=3, retry=True)
def runn(url, number_of_restaurants, skip):
	process_list = eateries_list.s(url, number_of_restaurants, skip) | dmap.s(process_eatery.s())
	process_list()
	return

