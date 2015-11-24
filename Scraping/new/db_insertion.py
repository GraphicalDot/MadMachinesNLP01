#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
This is the file responsible for actually inserting data in the database.
"""

from Testing_database import DB, collection, client
#from custom_logging import exceptions_logger
import traceback
import sys
import logging
import inspect
#from main_scrape import scrape
import pymongo
import traceback
import time
from pymongo.errors import BulkWriteError
from Testing_colored_print import bcolors

#LOG_FILENAME = 'exceptions_logger.log'
#:wlogging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG,)

import ConfigParser                                                                                                                                                                                                                        
config = ConfigParser.RawConfigParser()
config.read("global.cfg")
config.read("zomato_dom.cfg")

connection = pymongo.MongoClient(config.get("zomato", "host"), config.getint("zomato", "port"))
ZomatoReviews = connection[config.get("zomato", "database")][config.get("zomato", "reviews")]
ZomatoEateries = connection[config.get("zomato", "database")][config.get("zomato", "eatery")]
ZomatoUsers= connection[config.get("zomato", "database")][config.get("zomato", "users")]


class DBInsert(object):

	@staticmethod
	def db_insert_eateries(eatery):
		# db = client.modified_canworks  I think needed for bulk
		try:
			ZomatoEateries.update({"eatery_id": eatery.get("eatery_id")}, {"$set": eatery}, upsert=True)
                        print "{color}SUCCESS: FUNCTION--<{function_name}>  SUCCESS--<{success}>".format(color=bcolors.OKBLUE, \
                                        function_name=inspect.stack()[0][3], success="Eatery has been inserted successfully")
		
                except Exception as e:
                        print "{color}ERROR: FUNCTION--<{function_name}>  ERROR--<{error}>".format(color=bcolors.FAIL, \
                                                                    function_name=inspect.stack()[0][3], error=e)

		return
	
	@staticmethod
	def db_insert_reviews(reviews):
		for review in reviews:
			try:
				ZomatoReviews.insert(review)
				print "{start_color} Review with __review_id {id} {end_color}>".format(start_color=bcolors.OKBLUE, \
                                                                    id=review.get("__review_id"), end_color=bcolors.RESET)
			except Exception as e:
                                print "{start_color} ERROR:: FUNCTION--<{function_name}>  error--<{error}> {end_color}".format(start_color=bcolors.FAIL, \
                                        function_name=inspect.stack()[0][3], error=e, end_color=bcolors.RESET)

		return 


        @staticmethod
	def db_insert_users(reviews):
		for review in reviews:
			try:
				result = ZomatoUsers.update({"user_id": review.get("user_id"), "user_name": review.get("user_name")},{"$set": \
                                        {"user_url": review.get("user_url"), "user_followers": review.get("user_followers"), "user_reviews" : \
                                        review.get("user_reviews"), "updated_on": int(time.time())}}, upsert=True)
				print "{start_color} user with user_id {id} {end_color}>".format(start_color=bcolors.OKBLUE, \
                                                                    id=review.get("user_id"), end_color=bcolors.RESET)
			
                        except Exception as e:
                                print "{color} ERROR: FUNCTION--<{function_name}>  ERROR--<{error}>".format(color=bcolors.FAIL, function_name=inspect.stack()[0][3], error=e)

		return

	@staticmethod
	def insert_db(url, number_of_restaurants, stop, skip):
		__data = scrape(url, number_of_restaurants, stop, skip)
		DBInsert.db_insert_eateries(__data[0])
		DBInsert.db_insert_reviews(__data[1])
		DBInsert.db_insert_users(__data[2])
		return

	@staticmethod
	def db_delete_reviews(eatery_id):
		review_collection = collection("review")
		try:
			review_collection.delete_many({"eatery_id":str(eatery_id)})
		except Exception as e:
			print "{color} FUNCTION--<{function_name}>  ERROR--<{error}>".format(color=bcolors.FAIL, function_name=inspect.stack()[0][3], error=e)
		return

	@staticmethod
	def db_delete_eatery(eatery_id):
		eatery_collection = collection("eatery")
		try:
			eatery_collection.delete_one({"eatery_id":str(eatery_id)})
		except Exception as e:
			print "{color} FUNCTION--<{function_name}>  ERROR--<{error}>".format(color=bcolors.FAIL, function_name=inspect.stack()[0][3], error=e)
		return
#if __name__ == "__main__":
#	DBInsert.insert_db("http://www.zomato.com/ncr/malviya-nagar-delhi-restaurants?category=1", 40, 40 , 2)


# {u'nYields': 0,
#  u'nscannedAllPlans': 25359,
#   u'allPlans': [{u'cursor': u'BasicCursor', u'indexBounds': {},
#    u'nscannedObjects': 25359, u'nscanned': 25359, u'n': 25359}],
#     u'millis': 19, u'nChunkSkips': 0, u'server': u'Shubh:27017',
#      u'n': 25359, u'cursor': u'BasicCursor',
#       u'scanAndOrder': False, u'indexBounds': {}, u'nscannedObjectsAllPlans': 25359,
#        u'isMultiKey': False,
#          u'indexOnly': False, u'nscanned': 25359, u'nscannedObjects': 25359}
