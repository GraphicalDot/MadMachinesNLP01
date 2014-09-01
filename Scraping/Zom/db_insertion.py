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

#LOG_FILENAME = 'exceptions_logger.log'
#:wlogging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG,)

class DBInsert(object):


	@staticmethod
	def db_insert_eateries(eatery):
		eatery_collection = collection("eatery")
		db = CONNECTION.modified_canworks
		bulk = db.eatery.initialize_unordered_bulk_op()
		bulk.insert(eatery)
		try:
			bulk.execute()
		except BulkWriteError as error:
			print error.details

		return
	
	@staticmethod
	def db_insert_reviews(reviews):
		review_collection = collection("review")
		for review in reviews:
			try:
				review_collection.insert(review, safe=True)
			except Exception as e:
				print e
			#	print traceback.print_stack()
		return
	
	@staticmethod
	def db_insert_users(users):
		print "This is the length of the users_list %s"%len(users)
		user_collection = collection("user")
	
		
		for user in users:
			try:
				result = user_collection.update({"user_id": user.get("user_id"), "user_name": user.get("user_name")},{"$set": {"user_url": user.get("user_url"), "user_followers": user.get("user_followers"), "user_reviews" : user.get("user_reviews"), "updated_on": int(time.time())}}, upsert=True)	

				print user.get("user_id"), type(user.get("user_id"))
				print user_collection.find_one({"user_id": user.get("user_id")})
				print result.get("updatedExisting"), "\n\n"
			except Exception as e:
				print "%s occurred while updating %s"%(e, user.get("user_id"))
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
