#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
This is the file responsible for actually inserting data in the database.
"""

from database import DB, collection, CONNECTION
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
from colored_print import bcolors

#LOG_FILENAME = 'exceptions_logger.log'
#:wlogging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG,)

class DBInsert(object):


	@staticmethod
	def db_insert_eateries(eatery):
		eatery_collection = collection("eatery")
		db = CONNECTION.modified_canworks
		
                try:
                        eatery_collection.update({"eatery_id": eatery.get("eatery_id")}, {"$set": eatery}, upsert=False)
    
                except Exception as e:
		        print "{color} FUNCTION--<{function_name}>  ERROR--<{error}>".format(color=bcolors.FAIL, function_name=inspect.stack()[0][3], error=e)


                """
                bulk = db.eatery.initialize_unordered_bulk_op()
		bulk.insert(eatery)
		try:
			bulk.execute()
		except BulkWriteError as __error:
			print "{color} FUNCTION--<{function_name}>  ERROR--<{error}>".format(color=bcolors.OKGREEN, function_name=inspect.stack()[0][3], error=__error.details)
                """
		return
	
	@staticmethod
	def db_insert_reviews(reviews):
		review_collection = collection("review")
		for review in reviews:
			try:
				review_collection.insert(review, safe=True)
				print "{color} FUNCTION--<{function_name}>  SUCCESS--<{success}>".format(color=bcolors.OKBLUE, function_name=inspect.stack()[0][3], success="Review has been inserted successfully")
			except Exception as e:
				print "{color} FUNCTION--<{function_name}>  ERROR--<{error}>".format(color=bcolors.FAIL, function_name=inspect.stack()[0][3], error=e)
		return
	
	@staticmethod
	def db_insert_users(users):
		user_collection = collection("user")
	
		
		for user in users:
			try:
				result = user_collection.update({"user_id": user.get("user_id"), "user_name": user.get("user_name")},{"$set": {"user_url": user.get("user_url"), "user_followers": user.get("user_followers"), "user_reviews" : user.get("user_reviews"), "updated_on": int(time.time())}}, upsert=True)	

				print "{color} FUNCTION--<{function_name}>  MESSEGE--<Update Existing={messege}>".format(color=bcolors.OKBLUE, function_name=inspect.stack()[0][3], messege=result.get("updatedExisting"))
			except Exception as e:
				print "{color} FUNCTION--<{function_name}>  ERROR--<{error}>".format(color=bcolors.FAIL, function_name=inspect.stack()[0][3], error=e)
		return


	@staticmethod
	def insert_db(url, number_of_restaurants, stop, skip):
		__data = scrape(url, number_of_restaurants, stop, skip)
		DBInsert.db_insert_eateries(__data[0])
		DBInsert.db_insert_reviews(__data[1])
		DBInsert.db_insert_users(__data[2])
		return 

#if __name__ == "__main__":
#	DBInsert.insert_db("http://www.zomato.com/ncr/malviya-nagar-delhi-restaurants?category=1", 40, 40 , 2)
