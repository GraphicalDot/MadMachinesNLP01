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
from Text_Processing.Sentence_Tokenization.Sentence_Tokenization_Classes import SentenceTokenizationOnRegexOnInterjections
from GlobalConfigs import connection, eateries, reviews, yelp_eateries, yelp_reviews, eateries_results_collection, elasticsearch
         

from ProductionEnvironmentApi.text_processing_api import PerReview, EachEatery, DoClusters
from ProductionEnvironmentApi.text_processing_db_scripts import MongoScriptsReviews, MongoScriptsEateries, \
            MongoScriptsDoClusters, MongoScripts
from ProductionEnvironmentApi.prod_heuristic_clustering import ProductionHeuristicClustering
from ProductionEnvironmentApi.join_two_clusters import ProductionJoinClusters
from ProductionEnvironmentApi.elasticsearch_db import ElasticSearchScripts
from ProductionEnvironmentApi.query_resolution import QueryResolution



from ProcessingCeleryTask import MappingListWorker, PerReviewWorker, EachEateryWorker, DoClustersWorker     


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


class FBLogin(tornado.web.RequestHandler):
	@cors
	@tornado.gen.coroutine
	def post(self):
                """
                If the length of the new user_friends pposted ont he api uis greater than the length
                of the user_friends present in the database,
                then the list of user_friends shall be updated in the database
                """

		args = fb_login_parser.parse_args()
                print args
                if not android_users.find_one({"fb_id": args["fb_id"]}):
                        android_users.update({"fb_id": args["fb_id"]}, {"$set": {
                                                "user_name": args["user_name"],
                                                "email": args["email"],
                                                "gender": args["gender"], 
                                                "date_of_birth": args["date_of_birth"],
                                                "location": args["location"],
                                                "user_friends": args["user_friends"],}} , upsert=True) 
                
                        return {"error": False,
                                "success": True,
                                "error_code": 0,
                                "messege": "The user with fb_id {0} and name {1} has been inserted correctly".
                                                    format(args["fb_id"], args["user_name"] ),}
                
                
                if android_users.find_one({"fb_id": args["fb_id"]}):
                        if len(android_users.find_one({"fb_id": args["fb_id"]}).get("user_friends")) < len(args["user_friends"]):
                                android_users.update({"fb_id": args["fb_id"]}, {"$set": {
                                                "user_friends": args["user_friends"],}} , upsert=False) 
                                
                    
                                return {"error": False,
                                        "success": True,
                                        "error_code": 0,
                                        "messege": "The user with fb_id {0} and name {1} has been updated with new user_friends".
                                                    format(args["fb_id"], args["user_name"] ),}
                
                        return {"error": True,
                                "success": False,
                                "error_code": 0, 
                                "messege": "The user with fb_id {0} and name {1} already exists".
                                                    format(args["fb_id"], args["user_name"] ),}
                
                return


class PostComment(tornado.web.RequestHandler):
	@cors
	
	@tornado.gen.coroutine
        def post(self):
                args = post_comment_parser.parse_args()
                if not android_users.find_one({"fb_id": args["fb_id"]}):
                        return {"error": True,
                                "success": False,
                                "messege": "Please register the user first before posting the comment",}
                
                android_users.update({"fb_id": args["fb_id"]}, {"$push": {
                                                "comments": args["comment"],}}) 
            
                return {"error": False,
                        "success": True,
                        "messege": "The comment has been posted successfully",}
                        



class SuggestName(tornado.web.RequestHandler):
	@cors
	@tornado.gen.coroutine
	def post(self):
                args = suggest_name_parser.parse_args()
                if not android_users.find_one({"fb_id": args["fb_id"]}):
                        return {"error": True,
                                "success": False,
                                "messege": "Please register the user first before posting the comment",}
                
                android_users.update({"fb_id": args["fb_id"]}, {"$push": {
                                                "name_suggestion": args["name_suggestion"],}}) 
            
                return {"error": False,
                        "success": True,
                        "messege": "The suggestion for the name has been taken successfully",}



            
class PostPicture(tornado.web.RequestHandler):
	@cors
	@tornado.gen.coroutine
        def post(self):
                args = post_pic_parser.parse_args()
                if not android_users.find_one({"fb_id": args["fb_id"]}):
                        return {"error": True,
                                "success": False,
                                "messege": "Please register the user first before posting the image",}

                try:
                        base64.decodestring(args["image_string"])

                except Exception as e:
                        return {"error": True,
                                "success": False,
                                "messege": "The pic cannot be posted because of the error {0}".format(e),}

                
                #md5 checksum of the base64 encoded image, to form its unique id
                image_id = hashlib.md5(args["image_string"]).hexdigest() 


                #to check whether the same user is going to upload the same pic again
                if users_pic.find_one({"fb_id": args["fb_id"], "image_id": image_id }):
                        return {"error": True,
                                "success": False,
                                "messege": "This pic for this user has already been posted",}
                        


                android_users.update({"fb_id": args["fb_id"]}, {"$push": {
                                            "pics": image_id,}}) 
                
                users_pic.insert({"image_id": image_id, "image_name": args["image_name"], "fb_id": args["fb_id"], 
                                "image_base64_encoded_string": args["image_string"]})


                return {"error": False,
                        "success": True,
                        "messege": "The pic has been posted successfully",}


                #do we have image name options to be selected from
            
class GetPics(tornado.web.RequestHandler):
	@cors
	@tornado.gen.coroutine
	def get(self):
                args = get_pics_parser.parse_args()
                args["dish_name"]
                return {"error": False,
                        "success": True,
                        "result": result,}








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
            
                def Error(arg):
                        return {"error": True,
                                "success": False,
                                "messege": "{0} is required in the form".format(arg),
                                }


                eatery_id = self.get_argument("eatery_id")
                if not eatery_id: self.finish(Error("eatery_id"))
                
                category = self.get_argument("category")
                if not category: self.finish(Error("category"))


                        
                if not reviews.find({"eatery_id": eatery_id}):
                        self.finish({"error": True, "success": False, "error_messege": "The eatery id  {0} is not present".format(eatery_id),})


                category = category.lower()
                #name of the eatery
                eatery_name = eateries.find_one({"eatery_id": eatery_id}).get("eatery_name")
                if category not in ["service", "food", "ambience", "cost"]:
                        self.finish({"error": True, "success": False, "error_messege": "This is a n invalid tag %s"%category,})
       
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
        @property
        def executor(self):
                return self.application.executor

        @cors
	@print_execution
	@tornado.gen.coroutine
        def post(self):
                """
                Args:
                    Location:
                x_real_ip = self.request.headers.get("X-Real-IP")            
                print self.request.remote_ip

                location = self.get_argument("location")
                if not location:
                        location = None
                
                

                """
                        
                __result = yield self._exe("location")
                result = dict()
                for main_category, __out in __result.iteritems():
                        __list = list()
                        for item in __out:
                                superpositive = item.pop("super-positive")
                                supernegative= item.pop("super-negative")
                                totalsentiments = item.pop("total_sentiments")
                                item.update({"totalsentiments": totalsentiments, "superpositive": superpositive, "supernegative": supernegative})
                                __list.append(item)
                        result.update({main_category: __list})


                for key, value in result.iteritems():
                        for __value in value:
                                __value.update(time_series(__value["timeline"]))
                                __value.update({"subcategory": key})

                self.write({"success": True,
			"error": False,
			"result": result,
                        })
                self.finish()
        
        @run_on_executor
        def _exe(self, location):
                result = ElasticSearchScripts.get_trending(location)
                return result



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
                def Error(arg):
                        self.write({"error": True,
                                "success": False,
                                "messege": "Text is required in the form",
                                })
                        self.finish()


                text = self.get_argument("text")
                if not text: self.finish(Error())
               
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
                
                number_of_dishes = 14
                eatery_id =  self.get_argument("eatery_id")
                print eatery_id
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

                """
                
                def convert_for_highcharts(__dict):
                        superpositive = __dict.pop("super-positive")
                        supernegative= __dict.pop("super-negative")
                        totalsentiments = __dict.pop("total_sentiments")
                        __dict.update({"totalsentiments": totalsentiments, "superpositive": superpositive, "supernegative": supernegative})
                        timeline = __dict.pop("timeline")
                        __dict.update(time_series(timeline))
                        return __dict

                food = [convert_for_highcharts(dish) for dish in dishes]
                overall_food_dict = convert_for_highcharts(overall_food)
                overall_food.update({"name": "overall-food"})
                food.append(overall_food)
                """


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

                result = {"food": convert_for(dishes),
                                    "ambience": convert_for(ambience), 
                                    "cost": convert_for(cost), 
                                    "service": convert_for(service)}

                print result
                self.write({"success": True,
			"error": False,
                        "result": result})
                self.finish()



def main():
        http_server = tornado.httpserver.HTTPServer(Application())
        tornado.autoreload.start()
        http_server.listen("8000")
        tornado.ioloop.IOLoop.current().start()


class Application(tornado.web.Application):
        def __init__(self):
                handlers = [
                    (r"/limited_eateries_list", LimitedEateriesList),
                    (r"/get_word_cloud", GetWordCloud),
                    (r"/resolve_query", Query),
                    (r"/get_trending", GetTrending),
                    (r"/nearest_eateries", NearestEateries),
                    (r"/eatery_details", EateryDetails),]
                settings = dict(cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",)
                tornado.web.Application.__init__(self, handlers, **settings)
                self.executor = ThreadPoolExecutor(max_workers=60)



if __name__ == '__main__':
    print "server reloaded Dude"
    main()
