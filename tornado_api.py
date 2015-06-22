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
from tornado.web import asynchronous
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor

from Text_Processing.Sentence_Tokenization.Sentence_Tokenization_Classes import SentenceTokenizationOnRegexOnInterjections
from GlobalConfigs import connection, eateries, reviews, yelp_eateries, yelp_reviews
         

from ProductionEnvironmentApi.text_processing_api import PerReview, EachEatery, DoClusters
from ProductionEnvironmentApi.text_processing_db_scripts import MongoScriptsReviews, MongoScriptsEateries, \
            MongoScriptsDoClusters, MongoScripts
from ProductionEnvironmentApi.prod_heuristic_clustering import ProductionHeuristicClustering
from ProductionEnvironmentApi.join_two_clusters import ProductionJoinClusters



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
                result = list(eateries.find({"website": "zomato", "area_or_city": "ncr"},  {"eatery_id": True, "_id": False, "eatery_name": True, "area_or_city": True}).limit(100).sort("eatery_total_reviews", -1))
	
                for element in result:
                        eatery_id = element.get("eatery_id")
                        element.update({"reviews": reviews.find({"eatery_id": eatery_id}).count()})
                """
                yelp_result = list(yelp_eateries.find(fields= {"eatery_id": True, "_id": False, "eatery_name": True, "area_or_city": True}).limit(5).sort("eatery_total_reviews", -1))
                
                for element in yelp_result:
                        eatery_id = element.get("eatery_id")
                        element.update({"reviews": yelp_reviews.find({"eatery_id": eatery_id}).count()})
                self.write({"success": True,
			"error": False,
			"result": result +  yelp_result,
			})

                """
                self.write({"success": True,
			"error": False,
                        "result": result,
			})
                self.finish()
                
                
class Query(tornado.web.RequestHandler):
        @property
        def executor(self):
                return self.application.executor
    
        @cors
	@print_execution
	@tornado.gen.coroutine
        def post(self):
                print "post calles"
                def Error(arg):
                        self.write({"error": True,
                                "success": False,
                                "messege": "Text is required in the form",
                                })
                        self.finish()


                text = self.get_argument("text")
                if not text: self.finish(Error())
               
                food_text = None
                ambience_text = self.get_argument("text")
                service_text = self.get_argument("text")
                cost_text = self.get_argument("text")

                __result = yield self._exe(food_text, ambience_text, service_text, cost_text)
                self.write({"success": True,
			"error": False,
			"result": __result,
			})

                self.finish()

        
        @run_on_executor
        def _exe(self, food_text, ambience_text, service_text, cost_text):
                eatery_id = "308322"
                category = "food"
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
                for element in result:
                        element.update({"superpositive": element.get("super-positive") })
                        element.update({"supernegative": element.get("super-negative")})
                        element.pop("super-negative")
                        element.pop("super-positive")
                
                self.write({"success": True,
			"error": False,
			"result": result,
                        })
                self.finish()

class GetWordCloud(tornado.web.RequestHandler):
        @property
        def executor(self):
                return self.application.executor
    
    
        @cors
	@print_execution
	@tornado.gen.coroutine
        def post(self):
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
                for element in __result:
                        element.update({"superpositive": element.get("super-positive") })
                        element.update({"supernegative": element.get("super-negative")})
                        element.pop("super-negative")
                        element.pop("super-positive")
               

                """
                new_noun_phrases = list()
                keys = list()
                for e in __result:
                        keys.append({"name": e.get("name")})
                        for t in e.get("timeline"):
                                new_noun_phrases.append({"name": e.get("name"),
                                    "superpositive": (0, 1)[t[0] == "superpositive"],
                                    "supernegative": (0, 1)[t[0] == "supernegative"],
                                    "neutral": (0, 1)[t[0] == "neutral"],
                                    "positive": (0, 1)[t[0] == "positive"],
                                    "negative": (0, 1)[t[0] == "negative"],
                                    "ptime": t[1]})

                sorted_np = sorted(new_noun_phrases, key=lambda x: x.get("p-time"))
                
                print sorted_np 
                self.write({"success": True,
			"error": False,
                        "result": {"noun_phrases": sorted_np, "keys": keys},
			})
                """
                __timeline_result = list()
                for e in __result:
                        for mention_time in e["timeline"]:
                                __timeline_result.append([mention_time[1], (0, 1)[mention_time[0] == "super-positive"], (0, 1)[mention_time[0] == "positive"], (0, 1)[mention_time[0] == "neutral"], (0, 1)[mention_time[0] == "negative"], (0, 1)[mention_time[0] == "super-negative"],  e.get("name")])

                new_time_line = sorted(__timeline_result, key=lambda x: x[0])
              

                __list = list()
                __list.append(new_time_line[0])
                for element in new_time_line[1:]:
                        if element[0].split(" ")[0] == __list[-1][0][0].split(" ")[0]:
                                __list[-1].append(element)
                        else:
                                __list.append([element])

                self.write({"success": True,
			"error": False,
			"result": __list,
                        })
                self.finish()
                """
                self.write({"success": True,
			"error": False,
			"result": __result,
                        })
                self.finish()
                """
        
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
                print __collection.count()
                __collection.insert({"review_id": "misc", "sentence": sentence, "sentiment": value, "epoch_time": time.time(), 
                                "h_r_time": time.asctime()})
                print __collection.count()
                return {"success": True,
                        "error": False,
                        "messege": "Updated!!!",
                        }



class Application(tornado.web.Application):
        def __init__(self):
                handlers = [
                    (r"/limited_eateries_list", LimitedEateriesList),
                    (r"/get_word_cloud", GetWordCloud),
                    (r"/resolve_query", Query),
                        ]
                settings = dict(cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",)
                tornado.web.Application.__init__(self, handlers, **settings)
                self.executor = ThreadPoolExecutor(max_workers=60)


def main():
        http_server = tornado.httpserver.HTTPServer(Application())
        tornado.autoreload.start()
        http_server.listen("8000")
        tornado.ioloop.IOLoop.current().start()



if __name__ == '__main__':
    main()
