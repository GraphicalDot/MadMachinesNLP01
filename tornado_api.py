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
         
from FoodDomainApiHandlers.food_word_cloud import FoodWordCloudApiHelper
from FoodDomainApiHandlers.ambience_word_cloud import AmbienceWordCloudApiHelper
from FoodDomainApiHandlers.cost_word_cloud import CostWordCloudApiHelper
from FoodDomainApiHandlers.service_word_cloud import ServiceWordCloudApiHelper



training_db = connection.training_data
training_sentiment_collection = training_db.training_sentiment_collection
training_tag_collection = training_db.training_tag_collection


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
                

                total_noun_phrases = self.get_argument("total_noun_phrases", None)
                word_tokenization_algorithm_name = self.get_argument("word_tokenization_algorithm_name", "punkt_n_treebank")
                noun_phrases_algorithm_name = self.get_argument("noun_phrases_algorithm_name", "topia_n_textblob")
                pos_tagging_algorithm_name = self.get_argument("pos_tagging_algorithm_name", "hunpos_pos_tagger")
                tag_analysis_algorithm_name = self.get_argument("tag_analysis_algorithm_name", "svm_linear_kernel_classifier_tag.lib")
                sentiment_analysis_algorithm_name = self.get_argument("sentiment_analysis_algorithm_name", \
                                                                    "svm_linear_kernel_classifier_sentiment.lib")
                np_clustering_algorithm_name = self.get_argument("np_clustering_algorithm_name", "k_means")
                ner_algorithm_name = self.get_argument("ner_algorithm_name", "nltk_maxent_ner")
               
                start_date = self.get_argument("start_date", None)
                end_date = self.get_argument("end_date", None)

		start_epoch = time.mktime(time.strptime(start_date, '%Y-%m-%d'))
		end_epoch = time.mktime(time.strptime(end_date, '%Y-%m-%d'))

                        
                if not reviews.find({"eatery_id": eatery_id}):
                        self.finish({"error": True, "success": False, "error_messege": "The eatery id  {0} is not present".format(eatery_id),})



                #name of the eatery
                eatery_name = eateries.find_one({"eatery_id": eatery_id}).get("eatery_name")
                if category not in ["service", "food", "ambience", "cost"]:
                        self.finish({"error": True, "success": False, "error_messege": "This is a n invalid tag %s"%category,})
        
                if start_epoch and end_epoch:
                        review_list = [(post.get("review_id"), post.get("review_text")) for post in 
                            reviews.find({"eatery_id" :eatery_id, "converted_epoch": {"$gt":  start_epoch, "$lt" : end_epoch}})]
                else:
                        review_list = [(post.get("review_id"), post.get("review_text")) for post in reviews.find({"eatery_id" :eatery_id})] 
                
                


                def insert_into_db(eatery_id, tag, result, sentiment_analysis_algorithm_name, 
                                    tag_analysis_algorithm_name):
                        results_db = connection.NLP_NP_RESULTS_DB.EATERY_NP_RESULTS_COLLECTION


                        for noun_phrase in result:
                                try:
                                        sentences_list = noun_phrase.pop("sentences")
                                        noun_phrase_name = noun_phrase.get("name")

                                        sentences_ids = insert_sentences(sentences_list, 
                                                        sentiment_analysis_algorithm_name, 
                                                        tag_analysis_algorithm_name, tag)

                                        noun_phrase.update({"sentences_ids": sentences_ids})
                                        results_db.update({"eatery_id": eatery_id}, {"$set": 
                                            {
                                                "{0}.{1}".format(tag, noun_phrase_name): noun_phrase}}, 
                                            upsert=True)
                                except Exception as e:
                                        print noun_phrase
                                        pass
                        return 

                def insert_sentences(sentences_list, sentiment_analysis_algorithm_name, tag_analysis_algorithm_name, tag):
                        """
                        Each element:
                                u'sentence': u'death chicken wings ..', u'sentiment': u'neutral'},
                        """
                        sentences_result_collection = connection.NLP_NP_RESULTS_DB.SENTENCES_NP_RESULTS_COLLECTION
                        bulk = sentences_result_collection.initialize_ordered_bulk_op()
                        sentence_ids = list()
                        for __sentence in sentences_list:
                                __sentence_id = hashlib.md5(__sentence.get("sentence")).hexdigest()
                                bulk.find({"sentence_id": __sentence_id,}).upsert().update_one(
                                            {"$set": {
                                                "sentence": __sentence.get("sentence"),
                                                "sentiment.{0}".format(sentiment_analysis_algorithm_name.replace("_sentiment.lib", "")):
                                                                                __sentence.get("sentiment"),
                                                "tag.{0}".format(tag_analysis_algorithm_name.replace("_tag.lib", "")): tag,
                                                }})
                                sentence_ids.append(__sentence_id)
                        bulk.execute()
                        return sentence_ids
                                
                


                def retrive_sentences(sentence_ids, sentiment_analysis_algorithm_name, 
                                    tag_analysis_algorithm_name):
    
                        tag_analysis_algorithm_name = tag_analysis_algorithm_name.replace("_tag.lib", "")                    
                        sentiment_analysis_algorithm_name = sentiment_analysis_algorithm_name.replace("_sentiment.lib", "")
                        sentences_result_collection = connection.NLP_NP_RESULTS_DB.SENTENCES_NP_RESULTS_COLLECTION
                        sentences = list()
                        try:
                            for sentence_id in sentence_ids:
                                sentence = sentences_result_collection.find_one({"sentence_id": sentence_id})
                                sentences.append({"sentence": sentence.get("sentence"),
                                                "sentiment": sentence.get("sentiment").get(sentiment_analysis_algorithm_name),
                                    })
                        except Exception as e:
                                print 
                        return sentences
                
                def check_if_exists(eatery_id, tag, sentiment_analysis_algorithm_name, 
                                        tag_analysis_algorithm_name):
                        results_db = connection.NLP_NP_RESULTS_DB.EATERY_NP_RESULTS_COLLECTION
                        result_list = list()
                       
                        if bool(list(results_db.find({"eatery_id": eatery_id, tag: {"$exists": True}}))):
                                print "result found"
                                print eatery_id
                                print tag
                                for noun, noun_dict in results_db.find_one({"eatery_id": eatery_id}).get(tag).iteritems():
                                        try:
                                                sentences = retrive_sentences(noun_dict.get("sentences_ids"), sentiment_analysis_algorithm_name, 
                                                            tag_analysis_algorithm_name)
                                                noun_dict.update({"sentences": sentences})
                                                noun_dict.pop("sentences_ids")
                                                result_list.append(noun_dict)
                                        except Exception as e:
                                                print e
                                                pass
                                return result_list
                        return False

                if category == "service":
                        result = check_if_exists(eatery_id, "service", sentiment_analysis_algorithm_name, 
                                            tag_analysis_algorithm_name)
                        if result:
                                try:
                                        return {"success": True,
				        "error": False,
                                        "result": result,
                                        "sentences": list(), 
                                    }
                                except Exception as e:
                                        raise StandardError("{0}It Seems the data for this eatery werent inserted properly before\
                                                    \nTry flushing your database{1}".format(bcolors.FAIL, bcolors.RESET))
                        __instance = ServiceWordCloudApiHelper(reviews= review_list, eatery_name=eatery_name, 
                                    category=category, tag_analysis_algorithm_name=tag_analysis_algorithm_name, 
                                    sentiment_analysis_algorithm_name= sentiment_analysis_algorithm_name,
                                    word_tokenization_algorithm_name=word_tokenization_algorithm_name, 
                                    pos_tagging_algorithm_name=pos_tagging_algorithm_name, 
                                    noun_phrases_algorithm_name= noun_phrases_algorithm_name, 
                                    np_clustering_algorithm_name=np_clustering_algorithm_name,
                                    total_noun_phrases = total_noun_phrases,
                                    ner_algorithm_name = ner_algorithm_name,
                                    with_celery= False)
                        
                        __instance.run()
                        insert_into_db(eatery_id, category, __instance.result, sentiment_analysis_algorithm_name, 
                                                                            tag_analysis_algorithm_name)
                        
                        return {"success": True,
				"error": False,
                                "result": __instance.result,
                                "sentences": list(), 
                        }
               
                if category == "cost":
                        result = check_if_exists(eatery_id, "cost", sentiment_analysis_algorithm_name, 
                                            tag_analysis_algorithm_name)
                        if result:
                                try:
                                        return {"success": True,
				        "error": False,
                                        "result": result,
                                        "sentences": list(), 
                                    }
                                except Exception as e:
                                        raise StandardError("{0}It Seems the data for this eatery werent inserted properly before\
                                                    \nTry flushing your database{1}".format(bcolors.FAIL, bcolors.RESET))
                        __instance = CostWordCloudApiHelper(reviews= review_list, eatery_name=eatery_name, 
                                    category=category, tag_analysis_algorithm_name=tag_analysis_algorithm_name, 
                                    sentiment_analysis_algorithm_name= sentiment_analysis_algorithm_name,
                                    word_tokenization_algorithm_name=word_tokenization_algorithm_name, 
                                    pos_tagging_algorithm_name=pos_tagging_algorithm_name, 
                                    noun_phrases_algorithm_name= noun_phrases_algorithm_name, 
                                    np_clustering_algorithm_name=np_clustering_algorithm_name,
                                    total_noun_phrases = total_noun_phrases,
                                    ner_algorithm_name = ner_algorithm_name,
                                    with_celery= False)
                        
                        __instance.run()
                        insert_into_db(eatery_id, category, __instance.result, sentiment_analysis_algorithm_name, 
                                                                            tag_analysis_algorithm_name)
                        
                        return {"success": True,
				"error": False,
                                "result": __instance.result,
                                "sentences": list(), 
                        }
               
                if category == "ambience":
                        result = check_if_exists(eatery_id, "ambience", sentiment_analysis_algorithm_name, 
                                            tag_analysis_algorithm_name)
                        if result:
                                try:
                                        return {"success": True,
				        "error": False,
                                        "result": result,
                                        "sentences": list(), 
                                    }
                                except Exception as e:
                                        raise StandardError("{0}It Seems the data for this eatery werent inserted properly before\
                                                    \nTry flushing your database{1}".format(bcolors.FAIL, bcolors.RESET))
                        __instance = AmbienceWordCloudApiHelper(reviews= review_list, eatery_name=eatery_name, 
                                    category=category, tag_analysis_algorithm_name=tag_analysis_algorithm_name, 
                                    sentiment_analysis_algorithm_name= sentiment_analysis_algorithm_name,
                                    word_tokenization_algorithm_name=word_tokenization_algorithm_name, 
                                    pos_tagging_algorithm_name=pos_tagging_algorithm_name, 
                                    noun_phrases_algorithm_name= noun_phrases_algorithm_name, 
                                    np_clustering_algorithm_name=np_clustering_algorithm_name,
                                    total_noun_phrases = total_noun_phrases,
                                    ner_algorithm_name = ner_algorithm_name,
                                    with_celery= False)
                        
                        __instance.run()
                        __result = __instance.result


                        
                        insert_into_db(eatery_id, category, __result, sentiment_analysis_algorithm_name, 
                                                                            tag_analysis_algorithm_name)
                        return {"success": True,
				"error": False,
                                "result": __result,
                                "sentences": list(), 
                                }

                if category == "food":
                        result = check_if_exists(eatery_id, "food", sentiment_analysis_algorithm_name, 
                                            tag_analysis_algorithm_name)
                        if result:
                                try:
                                        return {"success": True,
				        "error": False,
                                        "result": sorted(result, reverse=True,
                                                        key= lambda x: x.get("positive")+x.get("negative")+x.get("neutral"))[0: 35],
                                        "sentences": list(), 
                                    }
                                except Exception as e:
                                        print e
                                        raise StandardError("{0}It Seems the data for this eatery werent inserted properly before\
                                                    \nTry flushing your database{1}".format(bcolors.FAIL, bcolors.RESET))

                        __instance = FoodWordCloudApiHelper(reviews= review_list, eatery_name=eatery_name, 
                                    category=category, tag_analysis_algorithm_name=tag_analysis_algorithm_name, 
                                    sentiment_analysis_algorithm_name= sentiment_analysis_algorithm_name,
                                    word_tokenization_algorithm_name=word_tokenization_algorithm_name, 
                                    pos_tagging_algorithm_name=pos_tagging_algorithm_name, 
                                    noun_phrases_algorithm_name= noun_phrases_algorithm_name, 
                                    np_clustering_algorithm_name=np_clustering_algorithm_name,
                                    total_noun_phrases = total_noun_phrases,
                                    ner_algorithm_name = ner_algorithm_name,
                                    with_celery= False, 
                                    do_sub_classification = True)

               
                        __instance.run()
                        insert_into_db(eatery_id, category, __instance.result, sentiment_analysis_algorithm_name, 
                                                                            tag_analysis_algorithm_name)
                        return {"success": True,
				"error": False,
                                "result": __instance.result[0:35],
                                "sentences": list(), 
                        }
                

                
                        
                if category == "ambience":
                        return {"success": True,
			    	"error": False,
                                "result": __instance.clustered_nps,
                                "sentences": list(), 
                                }
                
                        
                        
                result =  [{"name": __dict.get("name"), "positive": __dict.get("positive"), 
                              "negative": __dict.get("negative"), "neutral": __dict.get("neutral")} for __dict in __instance.clustered_nps]
                
                print "\n\n\n"
                #print result
                def converting_to_percentage(__object):
                        i = (__object.get("positive")*__positive + __object.get("negative")*__negative)/(__positive+__negative)
                        __object.update({"likeness": '%.2f'%i})
                        return __object

                def convert_sentences(__object):
                        return {"sentence": __object[0],
                                "sentiment": __object[1]}
                total_positive = sum([__dict.get("positive") for __dict in  __instance.clustered_nps])
                total_negative = sum([__dict.get("negative") for __dict in  __instance.clustered_nps])
                total = total_positive + total_negative

                def make_result(__dict):
                        __dict.update({"sentences": map(convert_sentences, __dict.get("sentences"))})
                        try:
                            i_likeness = "%.2f"%(float(__dict.get("positive")*100)/( __dict.get("negative") + __dict.get("positive")))
                        except ZeroDivisionError:
                            i_likeness = '100'

                        o_likeness =  "%.2f"%(float(__dict.get("positive")*total_positive + __dict.get("negative")*total_negative)/total)
                        __dict.update({"i_likeness": i_likeness})
                        __dict.update({"o_likeness": o_likeness})


                #[__dict.update({"sentences": map(convert_sentences, __dict.get("sentences"))}) for __dict in  __instance.clustered_nps]
                
                map(make_result, __instance.clustered_nps)
                result =  __instance.clustered_nps
             
                print result[3]

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
