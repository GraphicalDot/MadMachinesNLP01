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
from Text_Processing.Sentence_Tokenization.Sentence_Tokenization_Classes import SentenceTokenizationOnRegexOnInterjections
from GlobalConfigs import connection, eateries, reviews, yelp_eateries, yelp_reviews
         

from ProductionEnvironmentApi.text_processing_api import PerReview, EachEatery, DoClusters
from ProductionEnvironmentApi.text_processing_db_scripts import MongoScriptsReviews, MongoScriptsEateries, \
            MongoScriptsDoClusters, MongoScripts
from ProductionEnvironmentApi.prod_heuristic_clustering import ProductionHeuristicClustering
from ProductionEnvironmentApi.join_two_clusters import ProductionJoinClusters



from ProcessingCeleryTask import MappingList, PerReviewWorker, EachEateryWorker, DoClustersWorker     


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
	@tornado.gen.coroutine
        def get(self):
                """
                This gives only the limited eatery list like the top on the basis of the reviews count
                """
                print "fuckk you"
                result = list(eateries.find(fields= {"eatery_id": True, "_id": False, "eatery_name": True, "area_or_city": True}).limit(14).sort("eatery_total_reviews", -1))
	
                for element in result:
                        eatery_id = element.get("eatery_id")
                        element.update({"reviews": reviews.find({"eatery_id": eatery_id}).count()})

                yelp_result = list(yelp_eateries.find(fields= {"eatery_id": True, "_id": False, "eatery_name": True, "area_or_city": True}).limit(5).sort("eatery_total_reviews", -1))
                
                for element in yelp_result:
                        eatery_id = element.get("eatery_id")
                        element.update({"reviews": yelp_reviews.find({"eatery_id": eatery_id}).count()})
                self.write({"success": True,
			"error": False,
			"result": result +  yelp_result,
			})


                
                
class GetWordCloud(tornado.web.RequestHandler):
	@cors
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

                celery_chain = (EachEateryWorker.s(eatery_id)| MappingListWorker.s(eatery_id, PerReviewWorker.s()))()


                while celery_chain.status != "SUCCESS":
                        pass

                try:
                        for __id in celery_chain.children[0]:
                                while __id.status != "SUCCESS":
                                        pass
                except IndexError as e:
                        pass


                DoClustersWorker.apply_async(args=[eatery_id])


                ins = EachEatery(eatery_id=eatery_id)
                if not ins.return_non_processed_reviews():
                        eatery_instance = MongoScriptsEateries(eatery_id)
                        result = eatery_instance.get_noun_phrases(category, 30)
                        self.write({"success": True,
		        	"error": False,
		        	"result": result,
		        	})
                        self.finish()
                
                for review_id, review_text, review_time in ins.return_non_processed_reviews():
                        per_review_instance = PerReview(review_id, review_text, review_time, eatery_id)
                        per_review_instance.run()
                        
                do_cluster_ins = DoClusters(eatery_id=eatery_id)
                do_cluster_ins.run()  


                eatery_instance = MongoScriptsEateries(eatery_id)
                result = eatery_instance.get_noun_phrases(category, 30)
                self.write({"success": True,
			"error": False,
			"result": result,
			})


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


class RawTextParser(tornado.web.RequestHandler):
        @cors
        @timeit
        def post(self):
                result = list()
                from Text_Processing.PosTaggers.pos_tagging import PosTaggers

                
                path = "/home/kaali/Programs/Python/Canworks/Canworks/Text_Processing/PrepareClassifiers/InMemoryClassifiers/"
                args = raw_text_processing_parser.parse_args()
                text = args["text"]
                tag = args["tag"]


                text = text.replace("\n", "")
                sentiment_result = list()
                sent_tokenizer = SentenceTokenizationOnRegexOnInterjections()
                sentences = sent_tokenizer.tokenize(text)

                tag_classifier = joblib.load("{0}/{1}".format(path_in_memory_classifiers, "svm_linear_kernel_classifier_tag.lib"))
                new_sentiment_classifier = joblib.load("{0}/{1}".format(path_in_memory_classifiers, "svm_linear_kernel_classifier_sentiment_new_dataset.lib"))
                
	

                predicted_sentences = zip(sentences, tag_classifier.predict(sentences))
                def normalize_sentiments(result):
                        edited_result = list()
                        for (sent, sentiment, noun_phrases) in result:
                                __nouns = list()
                                if sentiment.startswith("super"):
                                        sentiment = sentiment.split("-")[1]
                                        __nouns.extend(noun_phrases)
                                        __nouns.extend(noun_phrases)
                                else:
                                    __nouns.extend(noun_phrases)
                                edited_result.append([sent, sentiment,  __nouns ])
                        return edited_result

                def populate_result(sent_sentiment_tags):
                        print sent_sentiment_tags
                        edited_result = list()
                        for (sent, sentiment, noun_phrases) in sent_sentiment_tags:
                                __nouns = list()
                                if sentiment.startswith("super"):
                                        sentiment = sentiment.split("-")[1]
                                        __nouns.append(noun_phrases)
                                        __nouns.append(noun_phrases)
                                else:
                                    __nouns.append(noun_phrases)
                                edited_result.append([(sentiment,noun) for noun in  __nouns ])
                        
                        result_dict = dict()
                        for (sentiment, noun_phrase), frequency in Counter(list(itertools.chain(*edited_result))).iteritems():
                                if result_dict.has_key(noun_phrase):
                                        result = result_dict.get(noun_phrase)
                                        positive, negative, neutral = result.get("positive"), result.get("negative"),\
                                                result.get("neutral") 

                                        

                                        new_frequency_negative = (negative, negative+1)[sentiment == "negative"]
                                        new_frequency_positive = (positive, positive+1)[sentiment == "positive"]
                                        new_frequency_neutral = (neutral, neutral+1)[sentiment == "neutral"]
                                        
                                        result_dict.update({noun_phrase: {"negative": new_frequency_negative, "positive": new_frequency_positive, 
                                             "neutral": new_frequency_neutral, }})
                                else:
                                        result_dict.update({
                                                noun_phrase:
                                                {"positive": (0, frequency)[sentiment == "positive"], 
                                                "negative": (0, frequency)[sentiment == "negative"],
                                                "neutral": (0, frequency)[sentiment == "neutral"],
                                                }
                                            })
                        
                        
                        result = list()
                        for noun_phrase, polarity_dict in result_dict.iteritems():
                            result.append({"name": noun_phrase,
                                        "positive": polarity_dict.get("positive"),
                                        "negative": polarity_dict.get("negative"),
                                        "neutral": polarity_dict.get("neutral"),
                                        })
                        return result

                if tag == "food":
                        sentences = [e[0] for e in predicted_sentences if e[1] == "food"]
                        sub_tag_classifier = joblib.load("{0}/{1}".format(path_in_memory_classifiers,\
                                                    "svm_linear_kernel_classifier_food_sub_tags_5May.lib"))                
                        
                        sentences = [encoding_help(e[0]) for e in zip(sentences, sub_tag_classifier.predict(sentences)) if e[1] == "dishes"]
                        predicted_sentiment = new_sentiment_classifier.predict(sentences)
                        
                        #noun_phrases_algorithm_name = "topia_n_textblob"
                        noun_phrases_algorithm_name = "topia"
                        __nouns = NounPhrases(sentences, default_np_extractor=noun_phrases_algorithm_name)
                        result  = [__tuple for __tuple in zip(sentences, predicted_sentiment, 
                                __nouns.noun_phrases[noun_phrases_algorithm_name]) if __tuple[2]]
                
                        edited_result = normalize_sentiments(result)

                        
                        from FoodDomainApiHandlers.heuristic_clustering import HeuristicClustering
                        __result = HeuristicClustering(edited_result, sentences, None)
                        result = sorted(__result.result, reverse=True, key= lambda x: x.get("positive")+x.get("negative"))


                if tag == "ambience":
                        result = list()
                        sentences = [e[0] for e in predicted_sentences if e[1] == "ambience"]
                        ambience_classifier = joblib.load("{0}/{1}".format(path_in_memory_classifiers, "svm_linear_kernel_classifier_ambience.lib"))
                        predicted_sentiment = new_sentiment_classifier.predict(sentences)
                    
                        predicted_sub_tags = ambience_classifier.predict(sentences)
                        result = populate_result(zip(sentences, predicted_sentiment, predicted_sub_tags))

                if tag == "service":
                        sentences = [e[0] for e in predicted_sentences if e[1] == "service"]
                        predicted_sentiment = new_sentiment_classifier.predict(sentences)
                        
                        predicted_sub_tags = ambience_classifier.predict(sentences)
                        
                        result = populate_result(zip(sentences, predicted_sentiment, predicted_sub_tags))
                
                
                if tag == "cost":
                        sentences = [e[0] for e in predicted_sentences if e[1] == "cost"]
                        cost_classifier = joblib.load("{0}/{1}".format(path_in_memory_classifiers, "svm_linear_kernel_classifier_cost.lib"))
                        predicted_sentiment = new_sentiment_classifier.predict(sentences)
                        predicted_sub_tags = cost_classifier.predict(sentences)
                        
                        result = populate_result(zip(sentences, predicted_sentiment, predicted_sub_tags))

                

                return {"success": True,
				"error": False,
                                "result": result,
                                }


class Application(tornado.web.Application):
        def __init__(self):
                handlers = [
                    (r"/limited_eateries_list", LimitedEateriesList),
                    (r"/get_word_cloud", GetWordCloud),
                        ]
                settings = dict(cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",)
                tornado.web.Application.__init__(self, handlers, **settings)

def main():
        http_server = tornado.httpserver.HTTPServer(Application())
        tornado.autoreload.start()
        http_server.listen("8000")
        tornado.ioloop.IOLoop.current().start()



if __name__ == '__main__':
    main()
