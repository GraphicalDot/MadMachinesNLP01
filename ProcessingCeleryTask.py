#!/usr/bin/env python
#-*- coding: utf-8 -*-
from __future__ import absolute_import
import celery
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
from processing_celery_app.App import app
from celery.registry import tasks
import logging
import inspect
from celery import task, subtask, group
from sklearn.externals import joblib
import time
connection = pymongo.Connection()
db = connection.intermediate
collection = db.intermediate_collection
from Text_Processing import WordTokenize, PosTaggers, SentenceTokenizationOnRegexOnInterjections, bcolors

logger = logging.getLogger(__name__)

db = connection.modified_canworks
reviews = db.review


"""
status: List active nodes in this cluster
        celery -A ProcessingCeleryTask status

purge: Purge messages from all configured task queues.
        celery -A ProcessingCeleryTask purge


inspect active: List active tasks
        celery -A proj inspect active
        These are all the tasks that are currently being executed.

inspect scheduled: List scheduled ETA tasks
        celery -A proj inspect scheduled
        These are tasks reserved by the worker because they have the eta or countdown argument set.

inspect reserved: List reserved tasks
        celery -A proj inspect reserved

inspect revoked: List history of revoked tasks
        celery -A proj inspect revoked
        
inspect registered: List registered tasks
        celery -A proj inspect registered

inspect stats: Show worker statistics (see Statistics)
        celery -A proj inspect stats
        
control enable_events: Enable events
        celery -A proj control enable_events

control disable_events: Disable events
        celery -A proj control disable_events


To daemonize the celery workers
https://celery.readthedocs.org/en/latest/tutorials/daemonizing.html#daemonizing
-P threads

   The thread pool will execute tasks in separate threads and the --concurrency
      argument controls the maximum number of threads used for that.



To run tasks for scraping one restaurant 
runn.apply_async(["https://www.zomato.com/ncr/pita-pit-lounge-greater-kailash-gk-1-delhi", None, None, True])

TO scrape a list of restaurant use this
runn.apply_async(args=["https://www.zomato.com/ncr/south-delhi-restaurants", 30, 270, False])
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


@app.task(ignore_result=True, max_retries=3, retry=True)
def eateries_list(url, number_of_restaurants, skip, is_eatery):
	print "{color} Execution of the function {function_name} starts".format(color=bcolors.OKBLUE, function_name=inspect.stack()[0][3])
	eateries_list = scrape_links(url, number_of_restaurants, skip, is_eatery)
	return eateries_list


"""

@app.task()
class WordTokenization(celery.Task):
	ignore_result=True, 
	max_retries=3, 
	acks_late=True
	default_retry_delay = 5
	def run(self, __tuple):
                """
                Args:
                    tuple (sentence, tag, sentiment)

                """
                word_tokenize = WordTokenize(__tuple[0])
                result = {"word_tokenization": word_tokenize.word_tokenized_list,
                                "sentence": __tuple[0], 
                                "tag": __tuple[1],
                                "sentiment": __tuple[2]}
		logger.info("Getting reviw text for review id {0}".format(word_tokenize.word_tokenized_list))
	        return  result

	def after_return(self, status, retval, task_id, args, kwargs, einfo):
		#exit point of the task whatever is the state
		logger.info("Ending run extracting reviews")
		pass

	def on_failure(self, exc, task_id, args, kwargs, einfo):
		print "fucking faliure occured"
		self.retry(exc=exc)



@app.task()
class SentenceTokenization(celery.Task):
	ignore_result=True, 
	max_retries=3, 
	acks_late=True
	default_retry_delay = 5
	def run(self, review_id):
                sent_tokenizer = SentenceTokenizationOnRegexOnInterjections()
                review_text = reviews.find_one({"review_id": review_id}).get("review_text")
		logger.info("Getting reviw text for review id {0}".format(review_id))
                tag_classifier = joblib.load("Text_Processing/PrepareClassifiers/InMemoryClassifiers/svm_linear_kernel_classifier_tag.lib")
                sentiment_classifier =joblib.load("Text_Processing/PrepareClassifiers/InMemoryClassifiers/svm_linear_kernel_classifier_sentiment.lib")
                
                tokenized_sentence_list = sent_tokenizer.tokenize(review_text)
                result = zip(tokenized_sentence_list, tag_classifier.predict(tokenized_sentence_list), 
                                                        sentiment_classifier.predict(tokenized_sentence_list))
                
		logger.info("Getting reviw text for review id {0}".format(result))
	        return  result

	def after_return(self, status, retval, task_id, args, kwargs, einfo):
		#exit point of the task whatever is the state
		logger.info("Ending run extracting reviews")
		pass

	def on_failure(self, exc, task_id, args, kwargs, einfo):
		print "fucking faliure occured"
		self.retry(exc=exc)

@app.task()
class ReviewIds(celery.Task):
	ignore_result=True, 
	max_retries=3, 
	acks_late=True
	default_retry_delay = 5
	def run(self, eatery_id):
                reviews_id = reviews.find({"eatery_id": eatery_id})
                result = [review.get("review_id") for review in reviews_id]
		print "Returning review ids"
		return result

	def after_return(self, status, retval, task_id, args, kwargs, einfo):
		#exit point of the task whatever is the state
		logger.info("Ending run extracting reviews")
		pass

	def on_failure(self, exc, task_id, args, kwargs, einfo):
		print "fucking faliure occured"
		self.retry(exc=exc)


@app.task(ignore_result=True, max_retries=3, retry=True, acks_late= True)
def MappingList(it, callback):
	# Map a callback over an iterator and return as a group
	callback = subtask(callback)
	return group(callback.clone([arg,]) for arg in it)()



@app.task(ignore_result=True, max_retries=3, retry=True)
def return_result(eatery_id):
        #process_list = ReviewIds.s(eatery_id)| MappingList.s(SentenceTokenization.s()) | MappingList.s(WordTokenization.s())
        process_list = ReviewIds.s(eatery_id)| MappingList.s(SentenceTokenization.s()) 
        return  process_list()
                    

