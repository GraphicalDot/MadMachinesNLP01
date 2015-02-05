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



import copy
import re
import csv
import codecs
from textblob import TextBlob 
from flask import Flask
from flask import request, jsonify
from flask.ext import restful
from flask.ext.restful import reqparse
from flask import make_response, request, current_app
from functools import update_wrapper
from flask import jsonify
import hashlib
import subprocess
import shutil
import json
import os
import StringIO
import difflib
from bson.json_util import dumps
from Text_Processing import NounPhrases, nltk_ngrams, get_all_algorithms_result, RpRcClassifier, \
		bcolors, CopiedSentenceTokenizer, SentenceTokenizationOnRegexOnInterjections, get_all_algorithms_result, \
		path_parent_dir, path_trainers_file, path_in_memory_classifiers, timeit, cd, SentimentClassifier, \
		TagClassifier
from Text_Processing import WordTokenize, PosTaggers


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
from api_helpers import merging_similar_elements
import base64
import requests
from PIL import Image

connection = pymongo.Connection()
db = connection.modified_canworks
eateries = db.eatery
reviews = db.review

#This is for android apps, may not be required later
android_db = connection.android_app
android_users = android_db.users
users_pic = android_db.pics
#####


app = Flask(__name__)
app.config['DEBUG'] = True
api = restful.Api(app,)




def load_classifiers_in_memory():
        instance = RpRcClassifier()
	instance.loading_all_classifiers_in_memory()
	
        #Loading all the classifiers in the memory for tags classification
	instance = TagClassifier()
	instance.loading_all_classifiers_in_memory()
        
	instance = SentimentClassifier()
	instance.loading_all_classifiers_in_memory()

def to_unicode_or_bust(obj, encoding='utf-8'):
	if isinstance(obj, basestring):
		if not isinstance(obj, unicode):
			obj = unicode(obj, encoding)
	return obj




#fb_login
fb_login_parser = reqparse.RequestParser()
fb_login_parser.add_argument("fb_id", type=str, required=True, location="form")
fb_login_parser.add_argument("email", type=str, required=False, location="form")
fb_login_parser.add_argument("gender", type=str, required=True, location="form")
fb_login_parser.add_argument("user_name", type=str, required=True, location="form")
fb_login_parser.add_argument("date_of_birth", type=str, required=True, location="form")
fb_login_parser.add_argument("location", type=str, required=True, location="form")
fb_login_parser.add_argument("user_friends", type=str, required=False, location="form", action="append")



#post_comment
post_comment_parser = reqparse.RequestParser()
post_comment_parser.add_argument("fb_id", type=str, required=True, location="form")
post_comment_parser.add_argument("comment", type=str, required=True, location="form")


#suggest_name
suggest_name_parser = reqparse.RequestParser()
suggest_name_parser.add_argument("fb_id", type=str, required=True, location="form")
suggest_name_parser.add_argument("name_suggestion", type=str, required=True, location="form")


#post_picture
post_pic_parser = reqparse.RequestParser()
post_pic_parser.add_argument("fb_id", type=str, required=True, location="form")
post_pic_parser.add_argument("image_name", type=str, required=True, location="form")
post_pic_parser.add_argument("image_string", type=str, required=True, location="form")


#get_pics
get_pics_parser = reqparse.RequestParser()
get_pics_parser.add_argument("dish_name", type=str, required=True, location="args")


##GetStartDateForRestaurant
get_start_date_for_restaurant_parser = reqparse.RequestParser()
get_start_date_for_restaurant_parser.add_argument('eatery_id', type=str,  required=True, location="form")
word_cloud_with_dates_parser = reqparse.RequestParser() 


##GetWordCloud
get_word_cloud_parser = reqparse.RequestParser()
get_word_cloud_parser.add_argument('eatery_id', type=str,  required=True, location="form")
get_word_cloud_parser.add_argument('category', type=str,  required=True, location="form")
get_word_cloud_parser.add_argument('start_date', type=str,  required=True, location="form")
get_word_cloud_parser.add_argument('end_date', type=str,  required=True, location="form") 





def cors(func, allow_origin=None, allow_headers=None, max_age=None):
	if not allow_origin:
                allow_origin = "*"
                		
	if not allow_headers:
		allow_headers = "content-type, accept"
		
	if not max_age:
		max_age = 60

	@wraps(func)
	def wrapper(*args, **kwargs):
		response = func(*args, **kwargs)
		cors_headers = {
				"Access-Control-Allow-Origin": allow_origin,
				"Access-Control-Allow-Methods": func.__name__.upper(),
				"Access-Control-Allow-Headers": allow_headers,
				"Access-Control-Max-Age": max_age,
				}
		if isinstance(response, tuple):
			if len(response) == 3:
				headers = response[-1]
			else:
				headers = {}
			headers.update(cors_headers)
			return (response[0], response[1], headers)
		else:
			return response, 200, cors_headers
	return wrapper


class FBLogin(restful.Resource):
	@cors
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


class PostComment(restful.Resource):
	@cors
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
                        



class SuggestName(restful.Resource):
	@cors
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



            
class PostPicture(restful.Resource):
	@cors
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
            
class GetPics(restful.Resource):
	@cors
	def get(self):
                args = get_pics_parser.parse_args()
                args["dish_name"]
                return {"error": False,
                        "success": True,
                        "result": result,}








class LimitedEateriesList(restful.Resource):
	@cors
	def get(self):
                """
                This gives only the limited eatery list like the top on the basis of the reviews count
                """
                result = list(eateries.find({"eatery_area_or_city": "ncr"}, fields= {"eatery_id": True, "_id": False, "eatery_name": True}).limit(15).sort("eatery_total_reviews", -1))
		
                return {"success": True,
			"error": False,
			"result": result,
			}

                
class EateriesList(restful.Resource):
	@cors
	def get(self):
                result = list(eateries.find({"eatery_area_or_city": "ncr"}, fields= {"eatery_id": True, "_id": False, "eatery_name": True}).limit(200).sort("eatery_total_reviews", -1))
		
                return {"success": True,
			"error": False,
			"result": result,
			}



class GetStartDateForRestaurant(restful.Resource):
	@cors
	def post(self):
		args = get_start_date_for_restaurant_parser.parse_args()
		eatery_id = args["eatery_id"]
		sorted_list_by_epoch = list(reviews.find({"eatery_id" :eatery_id}).sort("converted_epoch", 1))
		start_date = sorted_list_by_epoch[0].get('readable_review_day')
		start_month = sorted_list_by_epoch[0].get('readable_review_month')
		start_year = sorted_list_by_epoch[0].get('readable_review_year')
		
		end_date = sorted_list_by_epoch[-1].get('readable_review_day')
		end_month = sorted_list_by_epoch[-1].get('readable_review_month')
		end_year = sorted_list_by_epoch[-1].get('readable_review_year')
		
		
		
		
		return {"success": True,
				"error": True,
				"result": {"start": "{0}-{1}-{2}".format(start_year, start_month, start_date), 
					"end": "{0}-{1}-{2}".format(end_year, end_month, end_date)},
		}


class GetWordCloud(restful.Resource):
	@cors
	@timeit
        def post(self):
		args = get_word_cloud_parser.parse_args()
		print args
                start = time.time()
		__format = '%Y-%m-%d'
		eatery_id = args["eatery_id"]
		category = args["category"].lower()
		
		try:
			start_epoch = time.mktime(time.strptime(args["start_date"], __format))
			end_epoch = time.mktime(time.strptime(args["end_date"], __format))
		except Exception:
			return {"success": False,
				"error": "Dude!!, Please wait for the dates to be updated",
			}
	


		print "start epoch is -->%s and end_apoch is -->%s"%(start_epoch, end_epoch) 
                if not reviews.find({"eatery_id": eatery_id}):
                        return {"error": True,
                                "success": False,
                                "error_messege": "The eatery id  {0} is not present".format(eatery_id), 
                                }



                #name of the eatery
                eatery_name = eateries.find_one({"eatery_id": eatery_id}).get("eatery_name")

                if category not in ["service", "food", "ambience", "null", "overall", "cost"]:
                        return {"error": True,
                                "success": False,
                                "error_messege": "This is a n invalid tag %s"%category, 
                                }
                        


		noun_phrases_list = list()
		print type(start_epoch), type(end_epoch)


                #This is mongodb query for the arguments given int he post request, And the result is a list of reviews
		print "total reviews %s "%reviews.find({"eatery_id" :eatery_id}).count()
		review_result = reviews.find({"eatery_id" :eatery_id, "converted_epoch": {"$gt":  start_epoch, "$lt" : end_epoch}})  
            	print "the length with start date and the end date %s"%review_result.count()

		review_text = [to_unicode_or_bust(post.get("review_text")) for post in review_result]
		review_text = " .".join(review_text)

		
		with cd(path_in_memory_classifiers):
			tag_classifier = joblib.load('svm_grid_search_classifier_tag.lib')
			#tag_classifier = joblib.load('svm_linear_kernel_classifier_tag.lib')
			sentiment_classifier = joblib.load('svm_grid_search_classifier_sentiment.lib')
		
		noun_phrase = list()
		result = list() 

		sent_tokenizer = SentenceTokenizationOnRegexOnInterjections()
		
		
		test_sentences = sent_tokenizer.tokenize(to_unicode_or_bust(review_text))

		##with svm returns a list in the following form
		##[(sentence, tag), (sentence, tag), ................]
		#for chunk in text_classfication.with_svm():
		
		#Getting Sentiment analysis
		__predicted_tags = tag_classifier.predict(test_sentences)
		__predicted_sentiment = sentiment_classifier.predict(test_sentences)


		index = 0

		#classified_sentences = [('but in the afternoon , it is usually unoccupied .', 'null'),
		#(u'the food is fine , hard - to - eat in some cases .', 'food')]

		#__predicted_sentiment = ["null", "negative" ]

		print "\n\n %s \n\n"%(time.time() - start)

		new_time = time.time()
		filtered_tag_text = [text for text in zip(test_sentences, __predicted_tags, __predicted_sentiment) if text[1] == category]
	

		instance = ProcessingWithBlobInMemory()
		__k = lambda text: noun_phrases_list.extend([(noun.lower(),  text[2]) for noun in instance.noun_phrase(to_unicode_or_bust(text[0]))])	
		


                def check_lavenshtein_similarity(category, noun_phrase):
                        #This function checks if the noun phrase is neary same with the category or not
                        #for example the noun phrase "amazing ambiance" should be same sa "ambience"
                        #So the "amazing ambiance" should be split and the word similarity shall be checked with each
                        #split string otherwise whole string would give low string similarity ratio like .5 which would
                        #misinterpret "amazing ambiance" different from "ambience" 
                        for __noun in noun_phrase.split(" "):
                                ratio = difflib.SequenceMatcher(a=category, b=__noun).ratio()
                                if ratio > .8:
                                        return True
                               
                                
                                #The next lines of code checks for the presence of restaurant name in the noun_phrase
                                #If the restaurant is a name like "andhra bhawan" it qalso checks for that by splitting
                                #the string into two string and checks for the sequence matching for both
                                for __string in eatery_name.split(" "):
                                    __ratio = difflib.SequenceMatcher(a=__string, b=__noun).ratio()
                                    if __ratio > .6:
                                        return True

                #instance.noun_phrase(to_unicode_or_bust(text[0])) gives a list of noun phrases with the help of text blob library
		for text in filtered_tag_text:
			noun_phrases_list.extend([(noun.lower(),  text[2]) for noun in instance.noun_phrase(to_unicode_or_bust(text[0]))
                            if not check_lavenshtein_similarity(category, noun)
                            ])


		
		##Incresing and decrasing frequency of the noun phrases who are superpositive and supernegative and changing
		##their tags to positive and negative
		edited_result = list()
		for __noun_phrase_dict in noun_phrases_list:
			if __noun_phrase_dict[1] == "super-positive" or __noun_phrase_dict[1] == "super-negative":
				edited_result.append((__noun_phrase_dict[0], __noun_phrase_dict[1].split("-")[1]))
				#Added twice beacause super postive was given twice as weightage as positive and some goes for supernegative 
				#and negative
				edited_result.append((__noun_phrase_dict[0], __noun_phrase_dict[1].split("-")[1]))

			else:
				edited_result.append(__noun_phrase_dict)

		result = list()

		for key, value in Counter(edited_result).iteritems():
			result.append({"name": key[0], "polarity": 1 if key[1] == 'positive' else 0 , "frequency": value}) 
		

		"""
		with open("/home/k/word_cloud.csv", "wb") as csv_file:
			writer = csv.writer(csv_file, delimiter=',')
			for line in result:
				writer.writerow([line.get("name").encode("utf-8"), line.get("polarity"), line.get("frequency")])
		"""

		sorted_result = sorted(result, reverse=True, key=lambda x: x.get("frequency"))

		"""
		#final_result = sorted(merging_similar_elements(sorted_result), reverse=True, key=lambda x: x.get("frequency"))
                
                for element in final_result:
                    print element 
                
                """
                final_result = sorted(sorted_result, reverse=True, key=lambda x: x.get("frequency"))

                print   [(e, "\n")  for e in final_result[0: 20]]	
                return {"success": True,
				"error": False,
				"result": final_result[0:15],
		}
	

class TestWhole(restful.Resource):
	@cors
	@timeit
        def get(self):
                review_text = [to_unicode_or_bust(post.get("review_text")) for post in reviews.find({"eatery_id": "4571"})]
		review_text = " .".join(review_text)
                sent_tokenizer = SentenceTokenizationOnRegexOnInterjections()
                __word_tokenize = WordTokenize(sent_tokenizer.tokenize(review_text)) #using punkt_n_treebank_tokenizer
                word_tokenized_list =  __word_tokenize.word_tokenized_list
                
                __pos_tagger = PosTaggers(word_tokenized_list.get("punkt_n_treebank")[82:100]) #using default standford pos tagger
                __pos_tagged_sentences =  __pos_tagger.pos_tagged_sentences
                
                print __pos_tagged_sentences
                
                __noun_phrases = NounPhrases(__pos_tagged_sentences.get("stan_pos_tagger"))
                print __noun_phrases.noun_phrases
                
                return        


api.add_resource(EateriesList, '/eateries_list')
api.add_resource(LimitedEateriesList, '/limited_eateries_list')
api.add_resource(GetWordCloud, '/get_word_cloud')
api.add_resource(FBLogin, '/fb_login')
api.add_resource(PostComment, '/post_comment')
api.add_resource(SuggestName, '/name_suggestion')
api.add_resource(PostPicture, '/post_pic')
api.add_resource(GetPics, '/get_pics')
api.add_resource(GetStartDateForRestaurant, '/get_start_date_for_restaurant') 
api.add_resource(TestWhole, '/test') 

if __name__ == '__main__':
        #load_classifiers_in_memory()
	app.run(port=8000, debug=True)
