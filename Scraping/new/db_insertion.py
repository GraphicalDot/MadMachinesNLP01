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
from colored import fg, bg, attr


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


def print_messege(status, messege, function_name, error=None):

        if status=="success":
                __messege = "{0}{1}SUCCESS: {2}{3}{4} from Func_name=<<{5}>>{6}".format(fg("black"), bg('dark_green'), attr("reset"), \
			fg("dark_green"), messege, function_name, attr("reset"))
        else:
                __messege = "{0}{1}ERROR: {2}{3}{4} from Func_name=<<{5}>> with error<<{6}>>{7}".format(fg("black"), bg('red'), attr("reset"), \
			fg(202), messege, function_name, error, attr("reset"))
        
        print __messege



class DBInsert(object):

	@staticmethod
	def db_insert_eateries(eatery):
		# db = client.modified_canworks  I think needed for bulk
		try:
			ZomatoEateries.update({"eatery_id": eatery.get("eatery_id")}, {"$set": eatery}, upsert=True)
                        messege = "Eatery with eatery_id: %s  and eatery_name: %s has been updated successfully"%(eatery["eatery_id"], eatery["eatery_name"]) 
                        print_messege("success", messege, inspect.stack()[0][3])
		
                except Exception as e:
                        messege = "Eatery with eatery_id: %s  and eatery_name: %s failed"%(eatery["eatery_id"], eatery["eatery_name"]) 
                        print_messege("Error", messege, inspect.stack()[0][3], e)

		return
	
	@staticmethod
	def db_insert_reviews(reviews):
		for review in reviews:
			try:
				ZomatoReviews.insert(review)
                                messege = "Review  with review_id: %s  has been updated successfully"%(review["review_id"]) 
                                print_messege("success", messege, inspect.stack()[0][3])
                        except Exception as e:
                                messege = "Review  with review_id: %s  failed"%(review["review_id"]) 
                                print_messege("Error", messege, inspect.stack()[0][3], e)
                                pass
		return 


        @staticmethod
	def db_insert_users(reviews):
		for review in reviews:
			try:
				result = ZomatoUsers.update({"user_id": review.get("user_id"), "user_name": review.get("user_name")},{"$set": \
                                        {"user_url": review.get("user_url"), "user_followers": review.get("user_followers"), "user_reviews" : \
                                        review.get("user_reviews"), "updated_on": int(time.time())}}, upsert=True)
                                messege = "User with user_id: %s  and user_name: %s has been updated successfully"%(review["user_id"], review["user_name"]) 
                                print_messege("success", messege, inspect.stack()[0][3])
			
                        except Exception as e:
                                messege = "User  with user_id: %s  failed"%(review["user_id"]) 
                                print_messege("Error", messege, inspect.stack()[0][3], e)
                                pass

		return

