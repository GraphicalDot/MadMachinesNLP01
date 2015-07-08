#-*- coding: utf-8 -*-
"""
Author: Kaali
Dated: 19 february, 2015
Purpose: This file has all the config variables stored in it,
"""
import pymongo
import elasticsearch

ELASTICSEARCH_IP = "localhost"
ELASTICSEARCH_PORT = 9200

ES_CLIENT = elasticsearch.Elasticsearch(ELASTICSEARCH_IP)


##2014-07-22 20:49:11

TIME_FORMAT = "%Y-%m-%D %H:%M:%S"
#MONGO_REVIEWS_IP = "192.168.1.12"
MONGO_REVIEWS_IP = "localhost"
MONGO_REVIEWS_PORT = 27017
MONGO_REVIEWS_DB = "modified_canworks"
MONGO_REVIEWS_EATERIES_COLLECTION = "eatery"
MONGO_REVIEWS_REVIEWS_COLLECTION = "review"


#MONGO_REVIEWS_IP = "192.168.1.12"
MONGO_REVIEWS_IP = "localhost"
MONGO_REVIEWS_PORT = 27017
MONGO_YELP_DB = "YELP_DB"
MONGO_YELP_EATERIES = "YELP_EATERIES"
MONGO_YELP_REVIEWS = "YELP_REVIEWS"


##This mongodb has the collections which deals with the eatery_id and its noun phrases for 
##particular category, and each category stored has its last updated epoch
#MONGO_NP_RESULTS_IP = "192.168.1.12"
MONGO_NP_RESULTS_IP = "localhost"
MONGO_NP_RESULTS_PORT = 27017
MONGO_RESULTS_DB = "RESULTS_DB"
MONGO_SENTENCES_RESULTS_COLLECTION = "SENTENCES_RESULTS_COLLECTION"
MONGO_REVIEWS_RESULTS_COLLECTION = "REVIEWS_RESULTS_COLLECTION"
MONGO_EATERY_RESULTS_COLLECTION = "EATERY_RESULTS_COLLECTION"





#CELERY_REDIS_BROKER_IP = "192.168.1.12" 
CELERY_REDIS_BROKER_IP = "localhost" 
CELERY_REDIS_BROKER_PORT = 6379
CELERY_REDIS_BROKER_DB_NUMBER = 0 

DEBUG = {"ALL": True,
        "RESULTS": False, 
        "EXECUTION_TIME": True,
        "PRINT_DOCS": False,
        }

#connection = pymongo.MongoClient(MONGO_REVIEWS_IP, MONGO_REVIEWS_PORT, tz_aware=True, w=1,j=False, max_pool_size=200, use_greenlets=True)
connection = pymongo.MongoClient(MONGO_REVIEWS_IP, MONGO_REVIEWS_PORT)


eateries = eval("connection.{db_name}.{collection_name}".format(
                                                        db_name=MONGO_REVIEWS_DB,
                                                        collection_name=MONGO_REVIEWS_EATERIES_COLLECTION))


reviews = eval("connection.{db_name}.{collection_name}".format(
                                    db_name=MONGO_REVIEWS_DB,
                                    collection_name=MONGO_REVIEWS_REVIEWS_COLLECTION))


yelp_eateries = eval("connection.{db_name}.{collection_name}".format(
                                                        db_name=MONGO_YELP_DB,
                                                        collection_name=MONGO_YELP_EATERIES))
yelp_reviews = eval("connection.{db_name}.{collection_name}".format(
                                                        db_name=MONGO_YELP_DB,
                                                        collection_name=MONGO_YELP_REVIEWS))

reviews_results_collection = eval("connection.{db_name}.{collection_name}".format(
                                    db_name=MONGO_RESULTS_DB,
                                    collection_name=MONGO_REVIEWS_RESULTS_COLLECTION))

eateries_results_collection = eval("connection.{db_name}.{collection_name}".format(
                                    db_name=MONGO_RESULTS_DB,
                                    collection_name=MONGO_EATERY_RESULTS_COLLECTION))




class bcolors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        RESET='\033[0m'
                                   

