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

from celery import task, subtask, group
connection = pymongo.Connection()
db = connection.intermediate
collection = db.intermediate_collection


@app.task(ignore_result = True, max_retries=3, retry=True)
def eateries_list(amount):
	return [i for i in range(amount)]




@app.task(ignore_result = True, max_retries=3, retry=True)
def process_eatery(item):
	post = {"key": item, "messege": "this is the item %s"%item}
	print collection.insert(post)
	return

@app.task(ignore_result = True, max_retries=3, retry=True)
def dmap(it, callback):
	# Map a callback over an iterator and return as a group
	callback = subtask(callback)
	return group(callback.clone([arg,]) for arg in it)()

@app.task(ignore_result = True, max_retries=3, retry=True)
def runn():
	process_list = eateries_list.s(10) | dmap.s(process_eatery.s())
	process_list()
	return

"""
@app.task(ignore_result = True, max_retries=3, retry=True)
def fetch_html(url):
	return FetchingWorkersTask.html("url")




@app.task
def error_handler(uuid):
	result = AsyncResult(uuid)
	exc = result.get(propagate=False)
	print('Task {0} raised exception: {1!r}\n{2!r}'.format(uuid, exc, result.traceback))


@app.task(ignore_result=True)
def populate_scrape_url(name):
	collection = eval("DB.%s"%name)
	#counter = list(collection.find())[0].get("counter")	
	counter = None	

	if name == "LINKEDIN":
		instance = URLWorkersTask.linkedin(counter)
		new_counter = instance[0]
		urls = instance[1]
		for url in urls:
			parsing_worker = ParsingWorkersTask()
			chain = fetch_html.s(url) | parsing_worker.linkedin.s()
			chain()
			#fetch_html.apply_async([url], link=parse_html.s(), link_error=error_handler.s())

		#TODO: update counter by inserting the new counter in mongodb

	if name == "FACEBOOK":
		instance = URLWorkersTask.facebook(counter)
		new_counter = instance[0]
		urls = instance[1]
		for url in urls:
			parsing_worker = ParsingWorkersTask()
			chain = fetch_html.s(url) | parsing_worker.facebook.s()
			chain()
		#TODO: update counter by inserting the new counter in mongodb
		
	if name == "GITHUB":
		instance = URLWorkersTask.github(counter)
		new_counter = instance[0]
		urls = instance[1]
		for url in urls:
		#TODO: update counter by inserting the new counter in mongodb
			parsing_worker = ParsingWorkersTask()
			chain = fetch_html.s(url) | parsing_worker.github.s()
			chain()
			
	pass



"""
