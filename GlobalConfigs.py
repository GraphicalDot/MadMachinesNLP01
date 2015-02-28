#-*- coding: utf-8 -*-
"""
Author: Kaali
Dated: 19 february, 2015
Purpose: This file has all the config variables stored in it,
"""

#MONGO_REVIEWS_IP = "192.168.1.15"
MONGO_REVIEWS_IP = "localhost"
MONGO_REVIEWS_PORT = 27017


#MONGO_NLP_RESULTS_IP = "192.168.1.15"
MONGO_NLP_RESULTS_IP = "localhost"
MONGO_NLP_RESULTS_PORT = 27017
MONGO_NLP_RESULTS_DB = "NLP_RESULTS_DB"
MONGO_NLP_RESULTS_COLLECTION = "NLP_RESULTS_COLLECTION"



##This mongodb has the collections which deals with the eatery_id and its noun phrases for 
##particular category, and each category stored has its last updated epoch
#MONGO_NLP_RESULTS_IP = "192.168.1.15"
MONGO_EATERY_NP_RESULTS = "localhost"
MONGO_EATERY_NP_RESULTS_PORT = 27017
MONGO_EATERY_NP_RESULSTS_DB = "NLP_RESULTS_DB"
MONGO_EATERY_NP_RESULTS_COLLECTION = "NLP_RESULTS_COLLECTION"





#CELERY_REDIS_BROKER_IP = "192.168.1.15" 
CELERY_REDIS_BROKER_IP = "localhost" 
CELERY_REDIS_BROKER_PORT = 6379
CELERY_REDIS_BROKER_DB_NUMBER = 0 


