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
from celery_app.App import app
from main_scrape import EateriesList, EateryData
from celery.registry import tasks
import logging
import inspect
from celery import task, subtask, group
from colored_print import bcolors
from colored import fg, bg, attr
from db_insertion import DBInsert
import pprint
from celery.exceptions import Ignore


connection = pymongo.Connection()
db = connection.intermediate
collection = db.intermediate_collection


logger = logging.getLogger(__name__)

##If set to True all the scraping results will be udpated to the database
UPDATE_DB = True
"""
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
"""
def print_messege(status, messege, function_name, error=None):

        if status=="success":
                __messege = "{0}{1}SUCCESS: {2}{3}{4} from Func_name=<<{5}>>{6}".format(fg("black"), bg('dark_green'), attr("reset"), \
                        fg("dark_green"), messege, function_name, attr("reset"))
        else:
                __messege = "{0}{1}ERROR: {2}{3}{4} from Func_name=<<{5}>> with error<<{6}>>{7}".format(fg("black"), bg('red'), attr("reset"), \
                        fg(202), messege, function_name, error, attr("reset"))

        print __messege










@app.task()
class GenerateEateriesList(celery.Task):
        ignore_result = True
        max_retries = 3
        retry = True
	acks_late=True
        default_retry_delay=5
        print "{start_color} {function_name}:: This worker is meant to get all the eateries dict present\n\
                on the url given to it {end_color}".format(\
                start_color=bcolors.OKGREEN, function_name=inspect.stack()[0][3], end_color = bcolors.RESET)
        def run(self, url, number_of_restaurants, skip, is_eatery):
	        self.start = time.time()
                eateries_list = EateriesList(url, number_of_restaurants, skip, is_eatery)
                result = eateries_list.eateries_list
                for eatery in result:
	                print "{fg}{bg} Eatery with eatery details {eatery} {reset}".format(fg=fg("green"), \
                        bg=bg("dark_blue"), eatery=eatery, reset=attr("reset"))
            
                return result
        
        def after_return(self, status, retval, task_id, args, kwargs, einfo):
                #exit point of the task whatever is the state
                logger.info("{fg} {bg}Ending --<{function_name}--> of task --<{task_name}>-- with time taken\
                        --<{time}>-- seconds  {reset}".format(fg=fg('white'), bg=bg('green'), \
                        function_name=inspect.stack()[0][3], task_name= self.__class__.__name__,
                            time=time.time() -self.start, reset=attr('reset')))
                pass

        def on_failure(self, exc, task_id, args, kwargs, einfo):
                logger.info("{fg}{bg}Ending --<{function_name}--> of task --<{task_name}>-- failed fucking\
                        miserably {reset}".format(fg=fg("white"), bg=bg("red"),\
                        function_name=inspect.stack()[0][3], task_name= self.__class__.__name__, reset=attr('reset')))
                logger.info("{fg}{bg}{einfo}".format(fg=fg("white"), bg=bg("red"), einfo=einfo))
                self.retry(exc=exc)



@app.task()
class ScrapeEachEatery(celery.Task):
	ignore_result=True, 
	max_retries=3, 
	acks_late=True
	default_retry_delay = 5
        print "{start_color} {function_name}:: This worker is when given a eatery_dict scrapes more information\n\
                about that eatery and also scrapes review that has been written after the last time eatery was \n\
                scraped, calls EateryData which returns eatery_dict and review_list\n\
                Also it is also responsible to inserting that data into backend database{end_color}".format(\
                start_color=bcolors.OKGREEN, function_name=inspect.stack()[0][3], end_color = bcolors.RESET)
	def run(self, eatery_dict):
	        self.start = time.time()
		print "{color} Execution of the function {function_name} starts".format(color=bcolors.OKBLUE, function_name=inspect.stack()[0][3])
		__instance = EateryData(eatery_dict)
                print eatery_dict
                try:
                        eatery_dict, reviewslist = __instance.run()
                     
                        DBInsert.db_insert_eateries(eatery_dict)
                        DBInsert.db_insert_reviews(reviewslist)
                        DBInsert.db_insert_users(reviewslist)
                except StandardError as e:
                        messege = "Eatery with eatery_url %s failed "%(eatery_dict["eatery_url"])
                        print print_messege("Error", messege, "ScrapeEachEatery run method", e)
                        celery.control.purge()
                return

        def after_return(self, status, retval, task_id, args, kwargs, einfo):
                #exit point of the task whatever is the state
                logger.info("{fg} {bg}Ending --<{function_name}--> of task --<{task_name}>-- with time taken\
                        --<{time}>-- seconds  {reset}".format(fg=fg('white'), bg=bg('green'), \
                        function_name=inspect.stack()[0][3], task_name= self.__class__.__name__,
                            time=time.time() -self.start, reset=attr('reset')))
                pass

        """
        def on_failure(self, exc, task_id, args, kwargs, einfo):
                logger.info("{color} Ending --<{function_name}--> of task --<{task_name}>-- failed fucking\
                        miserably {reset}".format(color=bcolors.OKBLUE,\
                        function_name=inspect.stack()[0][3], task_name= self.__class__.__name__, reset=bcolors.RESET))
                logger.info("{0}{1}".format(einfo, bcolors.RESET))
                print task_id
                app.backend.mark_as_done(task_id)
                raise Ignore()
                self.retry(exc=exc)
        """






@app.task()
class MapListToTask(celery.Task):
	ignore_result=True 
	max_retries=3 
	acks_late=True
	default_retry_delay = 5
        print "{start_color} {function_name}:: Maps EateriesList to EateryData, by creating parallel tasks \n\
                for EateryData {end_color}".format(\
                start_color=bcolors.OKGREEN, function_name=inspect.stack()[0][3], end_color = bcolors.RESET)
        def run(self, it, callback):
	# Map a callback over an iterator and return as a group
	        self.start = time.time()
	        callback = subtask(callback)
	        return group(callback.clone([arg,]) for arg in it)()

        def after_return(self, status, retval, task_id, args, kwargs, einfo):
                logger.info("{fg} {bg}Ending --<{function_name}--> of task --<{task_name}>-- with time taken\
                        --<{time}>-- seconds  {reset}".format(fg=fg('white'), bg=bg('green'), \
                        function_name=inspect.stack()[0][3], task_name= self.__class__.__name__,
                            time=time.time() -self.start, reset=attr('reset')))
                pass

        def on_failure(self, exc, task_id, args, kwargs, einfo):
                logger.info("{color} Ending --<{function_name}--> of task --<{task_name}>-- failed fucking\
                        miserably {reset}".format(color=bcolors.OKBLUE,\
                        function_name=inspect.stack()[0][3], task_name= self.__class__.__name__, reset=bcolors.RESET))
                logger.info("{0}{1}".format(einfo, bcolors.RESET))
                self.retry(exc=exc)


@app.task()
class StartScrapeChain(celery.Task):
	ignore_result=True 
	max_retries=3
	acks_late=True
	default_retry_delay = 5
        
        print "{start_color} {function_name}:: This worker is meant to scrape all the eateries present on the url \n\
                with their reviews, It forms chain between ScrapeEachEatery and GenerateEateriesList\n \
                for more information on monitoring of celery workers\n\
                visit: http://docs.celeryproject.org/en/latest/userguide/monitoring.html\n{end_color}".format(\
                start_color=bcolors.OKGREEN, function_name=inspect.stack()[0][3], end_color = bcolors.RESET)
        print "http://docs.celeryproject.org/en/latest/userguide/monitoring.html"
        def run(self, url, number_of_restaurants, skip, is_eatery):
	        self.start = time.time()
                #process_list = eateries_list.s(url, number_of_restaurants, skip, is_eatery)| dmap.s(process_eatery.s())
                process_list = GenerateEateriesList.s(url, number_of_restaurants, skip, is_eatery)| MapListToTask.s(ScrapeEachEatery.s())
	        process_list()
	        return
        
    
        def after_return(self, status, retval, task_id, args, kwargs, einfo):
                #exit point of the task whatever is the state
                logger.info("{fg} {bg}Ending --<{function_name}--> of task --<{task_name}>-- with time taken\
                        --<{time}>-- seconds  {reset}".format(fg=fg('white'), bg=bg('green'), \
                        function_name=inspect.stack()[0][3], task_name= self.__class__.__name__,
                            time=time.time() -self.start, reset=attr('reset')))
                pass

        def on_failure(self, exc, task_id, args, kwargs, einfo):
                logger.info("{color} Ending --<{function_name}--> of task --<{task_name}>-- failed fucking\
                        miserably {reset}".format(color=bcolors.OKBLUE,\
                        function_name=inspect.stack()[0][3], task_name= self.__class__.__name__, reset=bcolors.RESET))
                logger.info("{0}{1}".format(einfo, bcolors.RESET))
                self.retry(exc=exc)
                
        
