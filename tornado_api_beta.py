#!/usr/bin/env python
#-*- coding: utf-8 -*-


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

from compiler.ast import flatten
from topia.termextract import extract
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
from Crypto.PublicKey import RSA
import jwt
from jwt import _JWTError
from Text_Processing.Sentence_Tokenization.Sentence_Tokenization_Classes import SentenceTokenizationOnRegexOnInterjections
from connections import eateries, reviews, eateries_results_collection, reviews_results_collection, short_eatery_result_collection, \
        bcolors, users_reviews_collection, users_feedback_collection, users_details_collection

from ProductionEnvironmentApi.text_processing_api import PerReview, EachEatery, DoClusters
from ProductionEnvironmentApi.text_processing_db_scripts import MongoScriptsReviews, MongoScriptsDoClusters
from ProductionEnvironmentApi.prod_heuristic_clustering import ProductionHeuristicClustering
from ProductionEnvironmentApi.join_two_clusters import ProductionJoinClusters
from ProductionEnvironmentApi.elasticsearch_db import ElasticSearchScripts

file_path = os.path.dirname(os.path.abspath(__file__))
parent_dirname = os.path.dirname(os.path.dirname(file_path))
print parent_dirname

if not os.path.exists("%s/private.pem"%parent_dirname):
        os.chdir(parent_dirname)
        subprocess.call(["openssl", "genrsa", "-out", "private.pem", "1024"])
        subprocess.call(["openssl", "rsa", "-in", "private.pem", "-out", "public.pem", "-outform", "PEM", "-pubout"])
        os.chdir(file_path)

private = open("%s/private.pem"%parent_dirname).read()
public = open("%s/public.pem"%parent_dirname).read()
private_key = RSA.importKey(private)
public_key = RSA.importKey(public)

def print_execution(func):
        "This decorator dumps out the arguments passed to a function before calling it"
        argnames = func.func_code.co_varnames[:func.func_code.co_argcount]
        fname = func.func_name
        def wrapper(*args,**kwargs):
                start_time = time.time()
                print "{0} Now {1} have started executing {2}".format(bcolors.OKBLUE, func.func_name, bcolors.RESET)
                result = func(*args, **kwargs)
                print "{0} Total time taken by {1} for execution is --<<{2}>>-- from ip--{3}\n".format(bcolors.OKGREEN, func.func_name,
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
                                                        





def httpauth(arguments):
        def real_decorator(func):
                def wrapped(self, *args, **kwargs):
                        token =  self.get_argument("token")
                        print arguments
                        try:
                                header, claims = jwt.verify_jwt(token, public_key, ['RS256'])
                                self.claims = claims
                                self.messege = None
                                for __arg in arguments:
                                        try:
                                                claims[__arg]
                                        except Exception as e:
                                                self.messege = "Missing argument %s"%__arg
                                                self.set_status(400)
                        except _JWTError:
                                self.messege = "Token expired"
                                self.set_status(403)
                        except Exception as e:
                                self.messege = "Some error occurred"
                                print e
                                self.set_status(500)
                            
                        
                        if self.messege:
                                self.write({
                                        "error": True,
                                        "success": False, 
                                        "messege": self.messege, 
                                })
                                
                        return func(self, *args, **kwargs) 
                return wrapped                   
        return real_decorator


class GetKey(tornado.web.RequestHandler):
	@cors
	@tornado.gen.coroutine
	@asynchronous
        def post(self):
                    if self.get_argument("secret") != '967d2b1f6111a198431532149879983a1ad3501224fb0dbf947499b1':
                            self.write({
                                "error": False,
                                "success": True, 
                                "messege": "Key, Nahi milegi", 
                                })
                            self.finish()
                            return 

                    self.write({
                                "error": True,
                                "success": False, 
                                "result": private, 
                        })
                    self.finish()
                    return 


class Test(tornado.web.RequestHandler):
	@cors
	@tornado.gen.coroutine
	@asynchronous
        @print_execution
        @httpauth(["latitude", "longitude"])
        def post(self):
                if not self.messege:
                        self.__on_response()
                self.finish()
                return 

        def __on_response(self):
                time.sleep(10)
                self.write({"success": True,
                            "error": False, 
                            "result": "success",
                            })
                return 

class UsersFeedback(tornado.web.RequestHandler):
	@cors
	@tornado.gen.coroutine
	@asynchronous
        def post(self):
                x_real_ip = self.request.headers.get("X-Real-IP")
                remote_ip = x_real_ip or self.request.remote_ip
                feedback = self.get_argument("feedback")
                name = self.get_argument("name")
                email = self.get_argument("email")

                try:
                        fb_id = self.get_argument("fb_id")
                except Exception as e:
                        fb_id = None
                        pass
                
                if users_feedback_collection.find_one({"feedback": feedback, "name": name, "email": email, "ip": remote_ip}):
                        self.set_status(409)
                        self.write({
                            "error": True, 
                            "success": False, 
                            "messege": "This feedback has already been submitted"
                            })
                        self.finish()
                        return 
                
                users_feedback_collection.insert({"feedback": feedback, "fb_id": fb_id,  "epoch": time.time(), "name": name, "email": email, "ip": remote_ip})
                self.write({
                            "error": False, 
                            "success": True, 
                            "messege": "The feedback has been posted, Thank you for your efforts", 
                            })
                self.finish()
                return


class WriteReview(tornado.web.RequestHandler):
	@cors
	@tornado.gen.coroutine
	@asynchronous
        def post(self):
                fb_id = self.get_argument("fb_id")
                review_text = self.get_argument("review_text")
                __eatery_id = self.get_argument("__eatery_id")
                __eatery_name = self.get_argument("eatery_name")

                if not users_details_collection.find_one({"fb_id": fb_id}):
                        self.set_status(401)
                        self.write({
                                "error": True, 
                                "success": False, 
                                "messege": "User needs to login"
                            })
                        self.finish()
                        return 



                __dict = {"review_text": review_text, "fb_id": fb_id, "__eatery_id": __eatery_id, "__eatery_name": __eatery_name}
                if users_reviews_collection.find_one(__dict):
                        self.write({
                            "error": True, 
                            "success": False, 
                            "messege": "This review has already been posted"
                            })
                        self.finish()
                        return 
                

                __dict.update({"epoch": time.strftime('%m/%d/%Y %H:%M:%S',  time.gmtime(1346114717972/1000.))})
                users_reviews_collection.insert(__dict)
                self.write({
                            "error": False, 
                            "success": True, 
                            "messege": "This review has been posted",
                            })
                self.finish()
                return 

            
class FetchReview(tornado.web.RequestHandler):
	@cors
	@tornado.gen.coroutine
	@asynchronous
        def post(self):
                __eatery_id = self.get_argument("__eatery_id")
                try:
                        limit = int(self.get_argument("limit"))
                except Exception as e:
                        print e
                        limit = 10
                
                try:
                        skip = int(self.get_argument("skip"))
                except Exception as e:
                        print e
                        skip = 0
                

                result = list()
                
                if not users_reviews_collection.find_one({"__eatery_id": __eatery_id}):
                        self.write({
                                    "error": True,
                                    "success": False, 
                                    "messege": "No reviews are present",
                                })
                        self.finish()
                        return 
                        

                for review in users_reviews_collection.find({"__eatery_id": __eatery_id}).skip(skip).limit(limit):
                        review.pop("_id")
                        result.append(review)

                self.write({
                            "error": False, 
                            "success": True, 
                            "result": result,
                            })
                self.finish()
                return 



class UsersDetails(tornado.web.RequestHandler):
	@cors
	@tornado.gen.coroutine
	@asynchronous
        def post(self):
                """
                User when does a fb login
                """
                fb_id = self.get_argument("fb_id")
                name = self.get_argument("name")
                email = self.get_argument("email")
                picture = self.get_argument("picture")
                print users_details_collection.update({"fb_id": fb_id}, {"$set": { "name": name, "email": email, "picture": picture}}, upsert=True, multi=False)
                self.write({"success": True,
			"error": False,
			})
                self.finish()
                return



class GetTrending(tornado.web.RequestHandler):
        @cors
	@print_execution
	@tornado.gen.coroutine
        def post(self):
                """
                Returns 10 nearest entries based on the four categories  to the latitude and longitude given to it
                Args:
                    latitude
                    longitude
                """
                latitude = float(self.get_argument("latitude"))
                longitude = float(self.get_argument("longitude"))
                print type(longitude)
                __result = ElasticSearchScripts.get_trending(latitude, longitude)
                

                print __result["service"]
                result = dict()
                for __category in [u'food', u'ambience', u'cost', u'service']:
                        __list = list()
                        for element in __result[__category]:
                                __eatery_id = element.get("__eatery_id")
                                __eatery_details = short_eatery_result_collection.find_one({"__eatery_id": __eatery_id})
                                for e in ["eatery_highlights", "eatery_cuisine", "eatery_trending", "eatery_id", "eatery_known_for", "eatery_type", "_id"]:
                                        try:
                                                __eatery_details.pop(e)
                                        except Exception as e:
                                                pass
                                element.update({"eatery_details": __eatery_details})
                                __list.append(element)
                        
                        result[__category] = __list

                self.write({"success": True,
			        "error": False,
			        "result": result,
			        })
                self.finish()
                return 


##edited on 24 december Done
class NearestEateries(tornado.web.RequestHandler):
	@cors
	@print_execution
        #@tornado.gen.coroutine
        @asynchronous
        def post(self):
                """
                Accoriding to the latitude, longitude given to it gives out the 10 restaurants nearby
                """
                
                latitude =  float(self.get_argument("latitude"))
                longitude =  float(self.get_argument("longitude")) 
                

                #result = eateries.find({"eatery_coordinates": {"$near": [lat, long]}}, projection).sort("eatery_total_reviews", -1).limit(10)
                #result = eateries.find({"eatery_coordinates" : SON([("$near", { "$geometry" : SON([("type", "Point"), ("coordinates", [lat, long]), \
                #        ("$maxDistance", range)])})])}, projection).limit(10)


                try:
                        short_eatery_result_collection.index_information()["location_2d"]

                except Exception as e:
                        self.write({"success": False,
			        "error": True,
                                "result": "Location index not present of collection",
			    })
                        self.finish()
                        return 
                        
                projection={"__eatery_id": True, "eatery_name": True, "eatery_address": True, "eatery_coordinates": True, "food": True, "_id": False, "cost": True, \
                        "service": True, "ambience": True, "overall": True, "menu": True}
                
                result = short_eatery_result_collection.find({"location": {"$near": [latitude, longitude]}}, projection ).limit(10)
                
                __result  = list(result)
                self.write({"success": True,
			"error": False,
                        "result": __result,
			})
                self.finish()
                return 
                

class TextSearch(tornado.web.RequestHandler):
        @cors
	@print_execution
	@tornado.gen.coroutine
        def post(self):
                """
                This api will be called when a user selects or enter a query in search box
                """
                text = self.get_argument("text")
                __type = self.get_argument("type")


                if __type == "dish":
                        """
                        It might be a possibility that the user enetered the dish which wasnt in autocomplete
                        then we have to search exact dish name of seach on Laveneshtein algo
                        """
                        ##search in ES for dish name 

                        result = list()
                        __result = ElasticSearchScripts.get_dish_match(text)
                        for dish in __result:
                                __eatery_id = dish.get("__eatery_id")
                                __eatery_details = short_eatery_result_collection.find_one({"__eatery_id": __eatery_id})
                                for e in ["eatery_highlights", "eatery_cuisine", "eatery_trending", "eatery_id", "eatery_known_for", "eatery_type", "_id"]:
                                        try:
                                                __eatery_details.pop(e)
                                        except Exception as e:
                                                pass
                                dish.update({"eatery_details": __eatery_details})
                                result.append(dish)

                elif __type == "cuisine":
                        ##gives out the restarant for cuisine name
                        print "searching for cuisine"
                        result = list()
                        __result = ElasticSearchScripts.eatery_on_cuisines(text)
                        print __result
                        for eatery in __result:
                                    __result= short_eatery_result_collection.find_one({"__eatery_id": eatery.get("__eatery_id")}, {"_id": False, "food": True, "ambience": True, \
                                            "cost":True, "service": True, "menu": True, "overall": True, "location": True, "eatery_address": True, "eatery_name": True, "__eatery_id": True})

                                    eatery.update({"eatery_details": __result})
                                    result.append(eatery)

                elif __type == "eatery":
                       
                            
                            result = eateries_results_collection.find_one({"eatery_name": text})
                            __result = process_result(result)
                            for e in ["eatery_highlights", "eatery_cuisine", "eatery_trending", "eatery_id", "eatery_known_for", "eatery_type", "_id", "processed_reviews", "old_considered_ids"]:
                                    try:
                                            result.pop(e)
                                    except Exception as e:
                                            pass
                            
                            result.update(__result)


                elif not  __type:
                        print "No type defined"

                else:
                        print __type
                        self.write({"success": False,
			        "error": True,
			        "messege": "Maaf kijiyega, Yeh na ho paayega",
			        })
                        self.finish()
                        return 
                self.write({"success": False,
			        "error": True,
			        "result": result,
			})
                self.finish()
                return 



class Suggestions(tornado.web.RequestHandler):
        @cors
	@print_execution
	@tornado.gen.coroutine
        def post(self):
                """


                Return:

                        [
                        {u'suggestions': [u'italian food', 'italia salad', 'italian twist', 'italian folks', 'italian attraction'], 'type': u'dish'},
                        {u'suggestions': [{u'eatery_name': u'Slice of Italy'}], u'type': u'eatery'},
                        {u'suggestions': [{u'name': u'Italian'}, {u'name': u'Cuisines:Italian'}], 'type': u'cuisine'}
                        ]

                """
                        
                query = self.get_argument("query")
                
                dish_suggestions = ElasticSearchScripts.dish_suggestions(query)
                cuisines_suggestions =  ElasticSearchScripts.cuisines_suggestions(query)
                eatery_suggestions = ElasticSearchScripts.eatery_suggestions(query)
                #address_suggestion = ElasticSearchScripts.address_suggestions(query)
                

                if cuisines_suggestions:
                        cuisines_suggestions= [e.get("name") for e in cuisines_suggestions]
                
                if eatery_suggestions:
                        eatery_suggestions= [e.get("eatery_name") for e in eatery_suggestions]


                self.write({"success": True,
			        "error": False,
                                "result": [{"type": "dish", "suggestions": [e.get("name") for e in dish_suggestions] },
                                            {"type": "eatery", "suggestions": eatery_suggestions },
                                            {"type": "cuisine", "suggestions": cuisines_suggestions }
                                            ]
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
                        
                __eatery_id =  self.get_argument("__eatery_id")
                result = eateries_results_collection.find_one({"__eatery_id": __eatery_id})
                if not result:
                        """
                        If the eatery name couldnt found in the mongodb for the popular matches
                        Then we are going to check for demarau levenshetin algorithm for string similarity
                        """

                        self.write({"success": False,
			        "error": True,
                                "result": "SOmehoe eatery with this eatery is not present in the DB"})
                        self.finish()
                        return 
                
                result = process_result(result)
                cprint(figlet_format('Finished executing %s'%self.__class__.__name__, font='mini'), attrs=['bold'])
                self.write({"success": True,
			"error": False,
                        "result": result})
                self.finish()

                return 


def process_result(result):
                number_of_dishes = 20
                dishes = sorted(result["food"]["dishes"], key=lambda x: x.get("total_sentiments"), reverse=True)[0: number_of_dishes]
                overall_food = result["food"]["overall-food"]
                ambience = result["ambience"]
                cost = result["cost"]
                service = result["service"]
                overall = result["overall"]
                menu = result["menu"]

                ##removing timeline
                [value.pop("timeline") for (key, value) in ambience.iteritems()]
                [value.pop("timeline") for (key, value) in cost.iteritems()]
                [value.pop("timeline") for (key, value) in service.iteritems()]
                overall.pop("timeline")
                menu.pop("timeline")
                [element.pop("timeline") for element in dishes]
                [element.pop("similar") for element in dishes]



                result = {"food": dishes,
                            "ambience": ambience, 
                            "cost": cost, 
                            "service": service, 
                            "menu": menu,
                            "overall": overall,
                            }
                        
                return result


app = tornado.web.Application([
                    (r"/suggestions", Suggestions),
                    (r"/textsearch", TextSearch),
                    (r"/test", Test),
                    (r"/getkey", GetKey),
                    
                    (r"/gettrending", GetTrending),
                    (r"/nearesteateries", NearestEateries),
                    (r"/usersdetails", UsersDetails),
                    (r"/usersfeedback", UsersFeedback),
                    (r"/usersdetails", UsersDetails),
                    (r"/writereview", WriteReview),
                    (r"/fetchreview", FetchReview),
                    (r"/geteatery", GetEatery),])

def main():
        http_server = tornado.httpserver.HTTPServer(app)
        """
        http_server.listen("8000")
        enable_pretty_logging()
        tornado.ioloop.IOLoop.current().start()
        """
        http_server.bind("8000")
        enable_pretty_logging()
        http_server.start(0) 
        loop = tornado.ioloop.IOLoop.instance()
        loop.start()
"""
class Application(tornado.web.Application):
        def __init__(self):
                handlers = [
                    (r"/suggestions", Suggestions),
                    (r"/textsearch", TextSearch),
                    
                    (r"/gettrending", GetTrending),
                    (r"/nearesteateries", NearestEateries),
                    (r"/usersdetails", UsersDetails),
                    (r"/usersfeedback", UsersFeedback),
                    (r"/geteatery", GetEatery),]
                tornado.web.Application.__init__(self, handlers, **settings)
                self.executor = ThreadPoolExecutor(max_workers=60)

"""

if __name__ == '__main__':
    cprint(figlet_format('Server Reloaded', font='big'), attrs=['bold'])
    main()
