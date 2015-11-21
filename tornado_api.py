#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Author:Kaali
Dated: 17 January, 2015
Day: Saturday
Description: This file has been written for the android developer, This will be used by minimum viable product implementation
            on android 

Comment: None
"""


from __future__ import absolute_import
import base64
import copy
import re
import csv
import codecs
from textblob import TextBlob 
import tornado.escape
import tornado.ioloop
import tornado.web
import tornado.autoreload
from tornado.httpclient import AsyncHTTPClient
from tornado.log import enable_pretty_logging
import hashlib
import subprocess
import shutil
import json
import os
import StringIO
import difflib
from textblob.np_extractors import ConllExtractor 
from bson.json_util import dumps
from Text_Processing import NounPhrases, get_all_algorithms_result, RpRcClassifier, \
		bcolors, CopiedSentenceTokenizer, SentenceTokenizationOnRegexOnInterjections, get_all_algorithms_result, \
		path_parent_dir, path_trainers_file, path_in_memory_classifiers, timeit, cd, SentimentClassifier, \
		TagClassifier, NERs, NpClustering


from GlobalAlgorithmNames import TAG_CLASSIFIER_LIB, SENTI_CLASSIFIER_LIB, FOOD_SB_TAG_CLASSIFIER_LIB, \
        COST_SB_TAG_CLASSIFIER_LIB, SERV_SB_TAG_CLASSIFIER_LIB, AMBI_SB_TAG_CLASSIFIER_LIB, \
        SENTI_CLASSIFIER_LIB_THREE_CATEGORIES


from compiler.ast import flatten
from topia.termextract import extract
from Text_Processing import WordTokenize, PosTaggers, NounPhrases
import decimal
import time
from datetime import timedelta
import pymongo
from collections import Counter
from functools import wraps
import itertools
import random
from sklearn.externals import joblib
import numpy
from multiprocessing import Pool
import base64
import requests
from PIL import Image
import inspect
import functools
import tornado.httpserver
from itertools import ifilter
from tornado.web import asynchronous
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from bson.son import SON
from termcolor import cprint 
from pyfiglet import figlet_format

from Text_Processing.Sentence_Tokenization.Sentence_Tokenization_Classes import SentenceTokenizationOnRegexOnInterjections
from GlobalConfigs import connection, eateries, reviews, yelp_eateries, yelp_reviews, eateries_results_collection,\
                    elasticsearch, users_details, users_feedback, users_queries, training_sentiment_collection,\
                    training_food_collection, training_tag_collection, training_service_collection , \
                    training_ambience_collection, training_cost_collection

from ProductionEnvironmentApi.text_processing_api import PerReview, EachEatery, DoClusters
from ProductionEnvironmentApi.text_processing_db_scripts import MongoScriptsReviews, MongoScriptsEateries, \
            MongoScriptsDoClusters, MongoScripts
from ProductionEnvironmentApi.prod_heuristic_clustering import ProductionHeuristicClustering
from ProductionEnvironmentApi.join_two_clusters import ProductionJoinClusters
from ProductionEnvironmentApi.elasticsearch_db import ElasticSearchScripts
from ProductionEnvironmentApi.query_resolution import QueryResolution



from ProcessingCeleryTask import MappingListWorker, PerReviewWorker, EachEateryWorker, DoClustersWorker     

from stanford_corenlp import save_tree

def print_execution(func):
        "This decorator dumps out the arguments passed to a function before calling it"
        argnames = func.func_code.co_varnames[:func.func_code.co_argcount]
        fname = func.func_name
        def wrapper(*args,**kwargs):
                start_time = time.time()
                print "{0} Now {1} have started executing {2}".format(bcolors.OKBLUE, func.func_name, bcolors.RESET)
                result = func(*args, **kwargs)
                print "{0} Total time taken by {1} for execution is --<<{2}>>--{3}\n".format(bcolors.OKGREEN, func.func_name,
                                (time.time() - start_time), bcolors.RESET)
                return result
        return wrapper




def cors(f):
        @functools.wraps(f) # to preserve name, docstring, etc.
        def wrapper(self, *args, **kwargs): # **kwargs for compability with functions that use them
                self.set_header("Access-Control-Allow-Origin",  "*")
                self.set_header("Access-Control-Allow-Headers", "content-type, accept")
                self.set_header("Access-Control-Max-Age", 60)
                return f(self, *args, **kwargs)
        return wrapper
                                                        




def time_series(__result):
        n_result = list()

        def __a(__dict, dates):
            __result = []
            for date in dates:
                    if __dict[date]:
                            __result.append(__dict[date])
                    else:
                            __result.append(0)
            return __result

        for element in __result:
                n_result.append([str(element[0].replace("-", "")), str(element[1].split(" ")[0])])
        
        sentiments, dates = zip(*n_result)
        dates = sorted(list(set(dates)))
        
        neutral = __a(Counter([x[1].split(" ")[0] for x in ifilter(lambda x: x[0] == "neutral" , n_result)]), dates)
        superpositive = __a(Counter([x[1].split(" ")[0] for x in ifilter(lambda x: x[0] == "superpositive" , n_result)]), dates)
        supernegative = [-abs(num) for num in __a(Counter([x[1].split(" ")[0] for x in ifilter(lambda x: x[0] == "supernegative" , n_result)]), dates)]
        negative = [-abs(num) for num in __a(Counter([x[1].split(" ")[0] for x in ifilter(lambda x: x[0] == "negative" , n_result)]), dates)]
        positive = __a(Counter([x[1].split(" ")[0] for x in ifilter(lambda x: x[0] == "positive" , n_result)]), dates)

        series = [{"name": e[0], "data": eval(e[0]), "color": e[1]} for e in [("neutral", "#ADB8C2"), ("superpositive", "green"), ("supernegative", "#B46254"), ("positive", "#598C73"), ("negative", "#8B7BA1")]]
        
        cumulative = numpy.cumsum([sum(e) for e in zip(negative, supernegative, superpositive, positive, neutral)])
        return {"categories": dates,
                "series": series, 
                "cumulative": [{"name": "cumulative", "data": list(cumulative), "color": "LightSlateGray"}]}


def convert_for(data):
                        highchart_categories = []
                        supernegative, superpositive, negative, neutral, positive = [], [], [], [], []
                        if type(data) == list:
                                for __data in data:
                            
                                        highchart_categories.append(__data.get("name"))
                                        supernegative.append(__data.get("super-negative"))
                                        superpositive.append(__data.get("super-positive"))
                                        negative.append(__data.get("negative"))
                                        positive.append(__data.get("positive"))
                                        neutral.append(__data.get("neutral"))
                        
                        if type(data) == dict:
                            for name, __data in data.iteritems():
                                        highchart_categories.append(name)
                                        supernegative.append(__data.get("super-negative"))
                                        superpositive.append(__data.get("super-positive"))
                                        negative.append(__data.get("negative"))
                                        positive.append(__data.get("positive"))
                                        neutral.append(__data.get("neutral"))

                        highchart_series = [
                                    {"name": "supernegative", "data": supernegative, 'color': "#B46254"},
                                    {"name": "negative", "data": negative, 'color': "#8B7BA1"},
                                    {"name": "neutral", "data": neutral, 'color': "#ADB8C2"},
                                    {"name": "positive", "data": positive, 'color': "#598C73"},
                                    {"name": "superpositive", "data": superpositive, 'color': "green"}, 
                                    ]

                        return {"categories": highchart_categories, "series": highchart_series}

class UsersFeedback(tornado.web.RequestHandler):
	@cors
	@tornado.gen.coroutine
	@asynchronous
        def post(self):
                
                feedback = self.get_argument("feedback")
                name = self.get_argument("name")
                telephone = self.get_argument("telephone")
                email = self.get_argument("email")
                print feedback
                users_feedback.insert({"feedback": feedback, "name": name, "telephone": telephone, "email": email, "timestamp": time.time()})
                self.write({"success": True,
			"error": False,
			})
                self.finish()
                return

class UsersDetails(tornado.web.RequestHandler):
	@cors
	@tornado.gen.coroutine
	@asynchronous
        def post(self):
                fb_id = self.get_argument("id")
                name = self.get_argument("name")
                email = self.get_argument("email")
                picture = self.get_argument("picture")
                print fb_id, name, email, picture
                print users_details
                print users_details.update({"fb_id": fb_id}, {"$set": { "name": name, "email": email, "picture": picture}}, upsert=True)
                self.write({"success": True,
			"error": False,
			})
                self.finish()
                return


class LimitedEateriesList(tornado.web.RequestHandler):
	@cors
	@print_execution
        #@tornado.gen.coroutine
        @asynchronous
        def get(self):
                """
                This gives only the limited eatery list like the top on the basis of the reviews count
                """
                projection={"eatery_id": True, "eatery_name": True, "eatery_address": True, "eatery_coordinates": True, "eatery_total_reviews": True, "_id": False}
                result = [eatery for eatery in list(eateries.find({"eatery_area_or_city": "ncr"},  projection).limit(100).sort("eatery_total_reviews", -1)) if eatery.get("eatery_coordinates")]
                self.write({"success": True,
			"error": False,
                        "result": result,
			})
                self.finish()





class EateriesOnCharacter(tornado.web.RequestHandler):
	@cors
	@print_execution
        #@tornado.gen.coroutine
        @asynchronous
        def post(self):
                """
                Returns eateries on the basis of the character starting the name of the eatery
                
                """
                page_num = int(self.get_argument("page_num"))
                skip = page_num*10
                projection={"eatery_id": True, "eatery_name": True, "eatery_address": True, "eatery_coordinates": True, "_id": False, "trending_factor": True}
                result = [eatery for eatery in list(eateries.find({"eatery_area_or_city": "ncr"},  projection).skip(skip).limit(10).sort("eatery_total_reviews", -1)) \
                        if eatery.get("eatery_coordinates")]
                

                def highest_trending(eatery_data, category):
                        result = sorted([[eatery_data[category][key].get("trending_factor"), key] for key in eatery_data[category].keys()], reverse=True, key=lambda x: x[0])
                        if not "null" in result[0][1].split("-"):
                                return result[0][1]
                        return result[1][1]



                for eatery in result:
                        eatery_data = eateries_results_collection.find_one({"eatery_id": eatery.get("eatery_id")})
                        sorted_by_trending = sorted(eatery_data["food"]["dishes"], reverse=True, key = lambda x: x.get("trending_factor"))
                        
                        if eatery_data:
                                    try:
                                            eatery.update({"trending1": sorted_by_trending[0].get("name")})
                                            eatery.update({"trending2": sorted_by_trending[1].get("name")})
                                    except Exception as e:
                                            print e
                                            eatery.update({"trending1": "Not enough data"})
                                            eatery.update({"trending2": "Not enough data"})
                                            
                                    eatery.update({"cost": highest_trending(eatery_data, "cost")})
                                    eatery.update({"service": highest_trending(eatery_data, "service")})
                                    eatery.update({"ambience": highest_trending(eatery_data, "ambience")})
                        else:
                                eatery.update({"trending1": "abc"})
                                eatery.update({"trending2": "def"})
               
                print result
                self.write({"success": True,
			"error": False,
                        "result": result,
			})
                self.finish()


                


#TODO : Tornadoright now hangs and slows down for another requests, if any one of the request fails
##Return something if a requests cannot be completed before a certain time limit
class GetWordCloud(tornado.web.RequestHandler):
        @property
        def executor(self):
                return self.application.executor
    
    
        @cors
	@print_execution
	@tornado.gen.coroutine
        def post(self):
                """
                Args:
                    eatery_id
                    category
                """
            
                eatery_id = self.get_argument("eatery_id")
                category = self.get_argument("category")


                        
                if not bool(reviews.find({"eatery_id": eatery_id}).count()):
                        self.set_status(400)
                        self.write({"error": True, "success": False, "error_messege": "The eatery id  {0} is not present".format(eatery_id),})
                        self.finish()
                        return 

                if reviews.find({"eatery_id": eatery_id}).count() == 0:
                        self.set_status(400)
                        self.finish({"error": True, "success": False, "error_messege": "The eatery id  {0} has no reviews prsent in the database".format(eatery_id),})
                        return 

                category = category.lower()
                #name of the eatery
                eatery_name = eateries.find_one({"eatery_id": eatery_id}).get("eatery_name")
                if category not in ["service", "food", "ambience", "cost"]:
                        self.set_status(400)
                        self.finish({"error": True, "success": False, "error_messege": "This is a n invalid tag %s"%category,})
                        return 
       
                """
                if start_epoch and end_epoch:
                        review_list = [(post.get("review_id"), post.get("review_text")) for post in 
                            reviews.find({"eatery_id" :eatery_id, "converted_epoch": {"$gt":  start_epoch, "$lt" : end_epoch}})]
                else:
                        review_list = [(post.get("review_id"), post.get("review_text")) for post in reviews.find({"eatery_id" :eatery_id})] 
                """
                print "Processing word cloud"
                __result = yield self._exe(eatery_id, category)
                
                if category != "food":
                        new_list = list()
                        for key, value in __result.iteritems():
                                value.update({"name": key})
                                new_list.append(value)
                        __result = new_list

                
                
                for element in __result:
                        element.update({"superpositive": element.get("super-positive") })
                        element.update({"supernegative": element.get("super-negative")})
                        element.pop("super-negative")
                        element.pop("super-positive")
               

                self.write({"success": True,
			"error": False,
			"result": __result,
                        })
                self.finish()
                return 


        @run_on_executor
        def _exe(self, eatery_id, category):
                celery_chain = (EachEateryWorker.s(eatery_id)| MappingListWorker.s(eatery_id, PerReviewWorker.s()))()


                while celery_chain.status != "SUCCESS":
                        pass

                try:
                        for __id in celery_chain.children[0]:
                                while __id.status != "SUCCESS":
                                        pass
                except IndexError as e:
                        pass


                do_cluster_result = DoClustersWorker.apply_async(args=[eatery_id])

                while do_cluster_result.status != "SUCCESS":
                        pass
                eatery_instance = MongoScriptsEateries(eatery_id)
                result = eatery_instance.get_noun_phrases(category, 40)
                return result

class UpdateClassifier(tornado.web.RequestHandler):
        @cors
        @timeit
        def post(self):
                """
                Update the classifier with new data into the InMemoryClassifiers folder
                args = update_classifiers.parse_args()    
                whether_allowed = False
                """
                
                if not whether_allowed:
                        return {"success": False,
                                "error": True,
                                "messege": "Right now, Updating Tags or sentiments are not allowed",
                                }


                
                return {"success": True,
                        "error": False,
                        "messege": "Updated!!!",
                        }



class ChangeTagOrSentiment(tornado.web.RequestHandler):
        @cors
        @timeit
        def post(self):
                """
                Updates a sentece with change tag or sentiment from the test.html,
                as the sentences will have no review id, the review_id will be marked as misc and will be stored in 
                training_sentiment_collection or training_tag_collection depending upon the tag or seniment being updated
                eatery_name =  self.get_argument("eatery_name")
                """
                args = change_tag_or_sentiment_parser.parse_args()    
                sentence = args["sentence"]
                value = args["value"]
                whether_allowed = True


                print sentence, value
                if not whether_allowed:
                        return {"success": False,
                                "error": True,
                                "messege": "Right now, Updating Tags or sentiments are not allowed",
                                }


                __collection = connection.training_data.training_sentiment_collection
                __collection.insert({"review_id": "misc", "sentence": sentence, "sentiment": value, "epoch_time": time.time(), 
                                "h_r_time": time.asctime()})
                return {"success": True,
                        "error": False,
                        "messege": "Updated!!!",
                        }


class GetTrending(tornado.web.RequestHandler):
        @cors
	@print_execution
	@tornado.gen.coroutine
        def post(self):
                """
                """
                        
                latitude = float(self.get_argument("lat"))
                longitude = float(self.get_argument("lng"))
                print type(longitude)
                result = ElasticSearchScripts.get_trending(latitude, longitude)
 
                for __category in ["food", "service", "cost", "ambience"]:
                        for __list in result[__category]:
                                    superpositive = __list.pop("super-positive")
                                    supernegative = __list.pop("super-negative")
                                    __list.update({"superpositive": superpositive, "supernegative": supernegative})


 
                self.write({"success": True,
			        "error": False,
			        "result": result,
			        })
                self.finish()
                return 



def process_object(__object):
            """

            """
            superpositive = __object.pop("super-positive")
            supernegative= __object.pop("super-negative")
            totalsentiments = __object.pop("total_sentiments")
            __object.update({"totalsentiments": totalsentiments, "superpositive": superpositive, "supernegative": supernegative})


            __object.update(time_series(__object["timeline"]))
            __object.update({"subcategory": __object["eatery_name"]})
            return __object

class Query(tornado.web.RequestHandler):
        @property
        def executor(self):
                return self.application.executor
    
        @cors
	@print_execution
	@tornado.gen.coroutine
        def post(self):
                """
               result returned :
               {'ambience': ['decor'], 'food': {}, 'cost': [], 'service': [], 
                'sentences': {'food': [(u'i want to have awesome chicken tikka t', u'dishes')], 
                'ambience': [(u'would have nice decor .', u'decor')], 'cost': [], 'service': []}}
                """

                text = self.get_argument("text")
                text =  text.replace("\n", "")
               
                try:
                        l_result = {"food": {}, "ambience": {}, "cost": {}, "service": {}}
                        processed_dishes = list()
                        __result = yield self._exe(text)

                        """
                        __result = {"food": {"dishes": [{"match": [], "suggestions": []}, 
                            {"match": [], "suggestions": []}, 
                        ],
                        }
                        }
                        for element in __result["food"]["dishes"]:
                                if type(element.get("match")) == list:
                                        __match = list()
                                        __suggestions = list()
                                        for __dish in element.get("match"):
                                                __match.append(process_object(__dish))
                                        for __dish in element.get("suggestions"):
                                                __suggestions.append(process_object(__dish))
                                        processed_dishes.append({"name": element.get("name"), "match": __match, "suggestions": __suggestions})
                        l_result["food"]["dishes"] = processed_dishes
                         
                        for main_category, __out in __result.iteritems():
                        __list = list()
                        for item in __out:
                        result.update({main_category: __list})


                        for key, value in result.iteritems():
                        for __value in value:
                        """
                        users_queries.insert({"query": text, "result": __result, "timestamp": time.time()})
                        self.write({"success": True,
			        "error": False,
			        "result": __result,
			        })
                    
                except StandardError as e:
                        print e
                        self.write({"success": False,
			        "error": True,
			        "messege": "Some error occurred while processing your query",
			        })

                self.finish()

        
        @run_on_executor
        def _exe(self, text):
                try:
                        query_resolution_instance = QueryResolution(text)
                        result = query_resolution_instance.run()
                        print "Result from  the query resolution"
                        print result
                        
                        #es_instance  = ElasticSearchScripts()
                        #result = es_instance.elastic_query_processing(result)
                        return result
                except Exception as e:
                        print e
                        raise StandardError("The request cannot be completed, the reason being %s"%e)

class NearestEateries(tornado.web.RequestHandler):
	@cors
	@print_execution
        #@tornado.gen.coroutine
        @asynchronous
        def post(self):
                """
                This gives only the limited eatery list like the top on the basis of the reviews count
                """
                
                lat =  float(self.get_argument("lat"))
                long =  float(self.get_argument("long")) 
                
                print self.get_argument("range")
                range = self.get_argument("range")
                if not range:
                        range = 5
                else:
                        range = int(range)
                


                projection={"eatery_id": True, "eatery_name": True, "eatery_address": True, "eatery_coordinates": True, "eatery_total_reviews": True, "_id": False}
                #result = eateries.find({"eatery_coordinates": {"$near": [lat, long]}}, projection).sort("eatery_total_reviews", -1).limit(10)
                result = eateries.find({"eatery_coordinates" : SON([("$near", { "$geometry" : SON([("type", "Point"), ("coordinates", [lat, long]), \
                        ("$maxDistance", range)])})])}, projection).limit(10)

                __result  = list(result)
                print __result
                self.write({"success": True,
			"error": False,
                        "result": __result,
			})
                self.finish()
                
class EateryDetails(tornado.web.RequestHandler):
	@cors
	@print_execution
        #@tornado.gen.coroutine
        @asynchronous
        def post(self):
                """
                NUmber of dishes to be returne is 14 , and the overfood is to be included also


                keys of each dict in food key of result are
                [u'name', 'series', 'cumulative', u'negative', 'supernegative', u'neutral', u'timeline', 'superpositive', 
                'totalsentiments', u'similar', u'positive', 'categories']

                """
                number_of_dishes = 20
                eatery_id =  self.get_argument("eatery_id")

                type_of_data =  self.get_argument("type_of_data")
               
                
                result = eateries_results_collection.find_one({"eatery_id": eatery_id})
                if not result:
                        self.write({"success": False,
			        "error": True,
                                "messege": "eatery id not present in the database" ,
	        		})
                        self.finish()
                        return  
                
                dishes = sorted(result["food"]["dishes"], key=lambda x: x.get("total_sentiments"), reverse=True)[0: number_of_dishes]
                overall_food = result["food"]["overall-food"]
                ambience = result["ambience"]
                cost = result["cost"]
                service = result["service"]


                if type_of_data == "highchart":
                            result = {
                                        "food": convert_for(dishes),
                                        "ambience": convert_for(ambience), 
                                        "cost": convert_for(cost), 
                                        "service": convert_for(service), 
                                        "eatery_address": result["eatery_address"],
                                    }

                else:
                        [dish.pop("timeline") for dish in dishes]    
                        [dish.pop("similar") for dish in dishes]    
                        [ambience[key].pop("timeline") for key in ambience.keys()]    
                        [cost[key].pop("timeline") for key in cost.keys()]    
                        [service[key].pop("timeline") for key in service.keys()]    
                        result = {
                                        "food": dishes,
                                        "ambience": ambience, 
                                        "cost": cost, 
                                        "service": service, 
                                        "eatery_address": result["eatery_address"],
                                    }
                        


                cprint(figlet_format('Finished executing %s'%self.__class__.__name__, font='mini'), attrs=['bold'])
                self.write({"success": True,
			"error": False,
                        "result": result})
                self.finish()


class GetDishSuggestions(tornado.web.RequestHandler):
        @cors
	@print_execution
	@tornado.gen.coroutine
        def get(self):
                """
                """
                        
                dish_name = self.get_argument("query")
                
                result = ElasticSearchScripts.dish_suggestions(dish_name)
                result = list(set(["{0}".format(element["name"]) for element in result]))
                print result 

                self.write({"success": True,
			        "error": False,
			        "options": result,
			        })
                self.finish()
                return 

class GetDishes(tornado.web.RequestHandler):
        @cors
	@print_execution
	@tornado.gen.coroutine
        def post(self):
                """
                """
                dish_name = self.get_argument("dish_name")
                
                result = ElasticSearchScripts.get_dishes(dish_name)
                print result
                for __list in result:
                                    superpositive = __list.pop("super-positive")
                                    supernegative = __list.pop("super-negative")
                                    __list.update({"superpositive": superpositive, "supernegative": supernegative})
                self.write({"success": True,
			        "error": False,
			        "result": result,
			        })
                self.finish()
                return 

class GetEatery(tornado.web.RequestHandler):
        @cors
	@print_execution
	@tornado.gen.coroutine
        def post(self):
                """
                """
                        
                number_of_dishes = 20
                eatery_name =  self.get_argument("eatery_name")
                type_of_data =  self.get_argument("type_of_data")
                result = eateries_results_collection.find_one({"eatery_name": eatery_name})
                if not result:
                        """
                        If the eatery name couldnt found in the mongodb for the popular matches
                        Then we are going to check for demarau levenshetin algorithm for string similarity
                        """



                    
                    
                    
                        return 
                
                dishes = sorted(result["food"]["dishes"], key=lambda x: x.get("total_sentiments"), reverse=True)[0: number_of_dishes]
                overall_food = result["food"]["overall-food"]
                ambience = result["ambience"]
                cost = result["cost"]
                service = result["service"]


                if type_of_data == "highchart":
                            result = {
                                        "food": convert_for(dishes),
                                        "ambience": convert_for(ambience), 
                                        "cost": convert_for(cost), 
                                        "service": convert_for(service), 
                                        "eatery_address": result["eatery_address"],
                                    }

                else:
                        [dish.pop("timeline") for dish in dishes]    
                        [dish.pop("similar") for dish in dishes]    
                        [ambience[key].pop("timeline") for key in ambience.keys()]    
                        [cost[key].pop("timeline") for key in cost.keys()]    
                        [service[key].pop("timeline") for key in service.keys()]    
                        result = {
                                        "food": dishes,
                                        "ambience": ambience, 
                                        "cost": cost, 
                                        "service": service, 
                                        "eatery_address": result["eatery_address"],
                                    }
                        

                cprint(figlet_format('Finished executing %s'%self.__class__.__name__, font='mini'), attrs=['bold'])
                self.write({"success": True,
			"error": False,
                        "result": result})
                self.finish()

                return 

class GetEaterySuggestions(tornado.web.RequestHandler):
        @cors
	@print_execution
	@tornado.gen.coroutine
        def get(self):
                """
                """
                        
                dish_name = self.get_argument("query")
                
                result = ElasticSearchScripts.eatery_suggestions(dish_name)
                result = list(set(["{0}".format(element["eatery_name"]) for element in result]))
                print result
                self.write({"success": True,
			        "error": False,
			        "options": result,
			        })
                self.finish()
                return 

class SentenceTokenization(tornado.web.RequestHandler):
        @cors
	@print_execution
	@tornado.gen.coroutine
        def post(self):
                """
                """
                
                cprint(figlet_format("Now exceuting %s"%self.__class__.__name__, font='mini'), attrs=['bold'])

                text = self.get_argument("text")
                link = self.get_argument("link")
                tokenizer = None

                
                conll_extractor = ConllExtractor()
                topia_extractor = extract.TermExtractor()
                
                if link:
                        print "Link is present, so have to run goose to extract text"
                        print link 


                text =  text.replace("\n", "")
                
                if not tokenizer:
                        tokenizer = SentenceTokenizationOnRegexOnInterjections()
                        result = tokenizer.tokenize(text)
                else:
                        result = nltk.sent_tokenize(text)

                tags = TAG_CLASSIFIER_LIB.predict(result)
                sentiments = SENTI_CLASSIFIER_LIB_THREE_CATEGORIES.predict(result)


                def assign_proba(__list):
                        return {"mixed": round(__list[0], 2), 
                                "negative": round( __list[1], 2), 
                                "neutral": round(__list[2], 2) , 
                                "positive": round(__list[3], 2), }
                
                      
                sentiment_probabilities = map(assign_proba, SENTI_CLASSIFIER_LIB_THREE_CATEGORIES.predict_proba(result))

                new_result = list()
                
                
                for sentence, tag, sentiment, probability in zip(result, tags, sentiments, sentiment_probabilities):
                        try:
                                subcategory = list(eval('{0}_SB_TAG_CLASSIFIER_LIB.predict(["{1}"])'.format(tag[0:4].upper(), sentence)))[0]
                        except:
                                subcategory = None

                        if max(probability) < .7:
                                polarity_result = "can't decide"
                        else:
                                polarity_result = "decided"

                        file_name, dependencies, indexeddependencies = save_tree(sentence)

                        if file_name:
                                with open(file_name, "rb") as image_file:
                                        encoded_string = base64.b64encode(image_file.read())
                        else:
                                    encoded_string = None
        
                        blob = TextBlob(sentence)
                        tb_nps = list(blob.noun_phrases) 
                        
                        blob = TextBlob(sentence, np_extractor=conll_extractor)
                        tb_conll_nps = list(blob.noun_phrases) 

                        te_nps = [e[0] for e in topia_extractor(sentence)]

                        print sentence, dependencies, "\n" 
                        new_result.append(
                                {"sentence": sentence,
                                "encoded_string": encoded_string,
                                "polarity": sentiment, 
                                "sentiment_probabilities": probability, 
                                "dependencies": dependencies, 
                                "indexeddependencies": indexeddependencies,
                                "polarity_result": polarity_result,
                                "noun_phrases": ["a", "b", "c"],
                                "tag": tag, 
                                "tb_conll_nps": tb_conll_nps,
                                "te_nps": te_nps, 
                                "subcategory": subcategory
                                            })

                self.write({"success": True,
			        "error": False,
			        "result": new_result,
			        })
                self.finish()
                return 


class UploadSentence(tornado.web.RequestHandler):
        @cors
	@print_execution
	@tornado.gen.coroutine
        def post(self):
                sentence = self.get_argument("sentence")
                sentiment = self.get_argument("sentiment")
                tag = self.get_argument("tag")
                subtag = self.get_argument("subtag")

                print sentence, sentiment, tag, subtag
                print training_sentiment_collection.count(), training_tag_collection.count(), training_food_collection.count(), training_service_collection.count(), training_cost_collection.count(), training_ambience_collection.count()
                training_tag_collection.insert({"sentence": sentence, "tag": tag, "review_id": "misc"})
                
                
                p = lambda sentiment:  "super-{0}".format(sentiment.replace("super", "")) if sentiment.startswith("super") else sentiment

                training_sentiment_collection.insert({"sentence": sentence, "sentiment": p(sentiment), "review_id": "misc"})
               
                
                try:
                        collection = eval("training_{0}_collection".format(tag))
                        collection.insert({"sentence": sentence, "sub_tag": subtag})
                except Exception as e:
                        print e
                        
                print training_sentiment_collection.count(), training_tag_collection.count(), training_food_collection.count(), training_service_collection.count(), training_cost_collection.count(), training_ambience_collection.count()
                self.write({"success": True,
			        "error": False,
			        })
                self.finish()




def main():
        http_server = tornado.httpserver.HTTPServer(Application())
        tornado.autoreload.start()
        http_server.listen("8000")
        enable_pretty_logging()
        tornado.ioloop.IOLoop.current().start()


class Application(tornado.web.Application):
        def __init__(self):
                handlers = [
                    (r"/limited_eateries_list", LimitedEateriesList),
                    (r"/get_word_cloud", GetWordCloud),
                    (r"/resolve_query", Query),
                    (r"/get_trending", GetTrending),
                    (r"/nearest_eateries", NearestEateries),
                    (r"/eateries_on_character", EateriesOnCharacter),
                    (r"/users_details", UsersDetails),
                    (r"/users_feedback", UsersFeedback),
                    (r"/get_dishes", GetDishes),
                    (r"/get_eatery", GetEatery),
                    (r"/get_dish_suggestions", GetDishSuggestions),
                    (r"/get_eatery_suggestions", GetEaterySuggestions),
                    (r"/sentence_tokenization", SentenceTokenization),
                    (r"/upload_sentence", UploadSentence),
                
                    (r"/eatery_details", EateryDetails),]
                settings = dict(cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",)
                tornado.web.Application.__init__(self, handlers, **settings)
                self.executor = ThreadPoolExecutor(max_workers=60)



if __name__ == '__main__':
    cprint(figlet_format('Server Reloaded', font='big'), attrs=['bold'])
    main()
