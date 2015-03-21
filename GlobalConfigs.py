#-*- coding: utf-8 -*-
"""
Author: Kaali
Dated: 19 february, 2015
Purpose: This file has all the config variables stored in it,
"""

#MONGO_REVIEWS_IP = "192.168.1.6"
MONGO_REVIEWS_IP = "localhost"
MONGO_REVIEWS_PORT = 27017
MONGO_REVIEWS_DB = "modified_canworks"
MONGO_REVIEWS_EATERIES_COLLECTION = "eatery"
MONGO_REVIEWS_REVIEWS_COLLECTION = "review"


##This mongodb has the collections which deals with the eatery_id and its noun phrases for 
##particular category, and each category stored has its last updated epoch
#MONGO_NP_RESULTS_IP = "192.168.1.6"
MONGO_NP_RESULTS_IP = "localhost"
MONGO_NP_RESULTS_PORT = 27017
MONGO_NP_RESULTS_DB = "NLP_NP_RESULTS_DB"
MONGO_SENTENCES_NP_RESULTS_COLLECTION = "SENTENCES_NL_RESULTS_COLLECTION"
MONGO_REVIEWS_NP_RESULTS_COLLECTION = "REVIEWS_NP_RESULTS_COLLECTION"
MONGO_EATERY_NP_RESULTS_COLLECTION = "EATERY_NP_RESULTS_COLLECTION"





#CELERY_REDIS_BROKER_IP = "192.168.1.6" 
CELERY_REDIS_BROKER_IP = "localhost" 
CELERY_REDIS_BROKER_PORT = 6379
CELERY_REDIS_BROKER_DB_NUMBER = 0 

