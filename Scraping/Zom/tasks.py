#!/usr/bin/env python
#-*- coding: utf-8 -*-
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

"""
To run tasks for scraping one restaurant 
runn.apply_async(["https://www.zomato.com/ncr/pita-pit-lounge-greater-kailash-gk-1-delhi", None, None, True])

TO scrape a list of restaurant use this
runn.apply_async(args=["https://www.zomato.com/ncr/south-delhi-restaurants", 30, 270, False])
"""


@app.task(ignore_result=True, max_retries=3, retry=True)
def eateries_list(url, number_of_restaurants, skip, is_eatery):
	print "got into eateries list"
	eateries_list = scrape_links(url, number_of_restaurants, skip, is_eatery)
	return eateries_list



@app.task(ignore_result=True, max_retries=3, retry=True, acks_late=True)
def process_eatery(eatery_dict):
	"""
	 Task.acks_late
	     If set to True messages for this task will be acknowledged after the task has been executed, 
	     not just before, which is the default behavior.
	
	Task.ErrorMail
	    If the sending of error emails is enabled for this task, then this is the class defining the 
	    logic to send error mails.
	
	Task.store_errors_even_if_ignored
	    If True, errors will be stored even if the task is configured to ignore results.

	
	Task.ErrorMail
	    If the sending of error emails is enabled for this task, then this is the class defining the 
	    logic to send error mails.


	 Task.rate_limit
	     Set the rate limit for this task type which limits the number of tasks that can be run in a 
	     given time frame. Tasks will still complete when a rate limit is in effect, but it may take 
	     some time before it’s allowed to start.
	     If this is None no rate limit is in effect. If it is an integer or float, it is interpreted as 
	     “tasks per second”.
	     The rate limits can be specified in seconds, minutes or hours by appending “/s”, “/m” or “/h” 
	     to the value. Tasks will be evenly distributed over the specified time frame.
	     Example: “100/m” (hundred tasks a minute). This will enforce a minimum delay of 600ms between 
	     starting two tasks on the same worker instance.
	"""
	print "got into process_eatery"
	try:
		eatery_specific(eatery_dict)
	
	except Exception as e:
		print e
		#def on_failure(self, eatery_dict):
		print "fucking faliure occured"
		eatery_specific(eatery_dict)
		        
	return

@app.task(ignore_result=True, max_retries=3, retry=True, acks_late= True)
def dmap(it, callback):
	# Map a callback over an iterator and return as a group
	callback = subtask(callback)
	return group(callback.clone([arg,]) for arg in it)()

@app.task(ignore_result=True, max_retries=3, retry=True)
def runn(url, number_of_restaurants, skip, is_eatery):
	process_list = eateries_list.s(url, number_of_restaurants, skip, is_eatery)| dmap.s(process_eatery.s())
	process_list()
	return

