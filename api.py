#!/usr/bin/env python
#-*- coding: utf-8 -*-

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
from Text_Processing import ProcessingWithBlob, PosTags, nltk_ngrams, get_all_algorithms_result, RpRcClassifier, \
		bcolors, CopiedSentenceTokenizer, SentenceTokenizationOnRegexOnInterjections, get_all_algorithms_result, \
		path_parent_dir, path_trainers_file, path_in_memory_classifiers, timeit, cd, SentimentClassifier, \
		TagClassifier, ProcessingWithBlobInMemory

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

DATA = [       {"name": "friends", 
            "children": [{"name": "beer", "polarity": 0, "frequency": 2,}, {"name": "cost effective", "polarity": 1, "frequency": 12,},
                {"name": "Big Chill", "polarity": 0, "frequency": 8,}, {"name": "outdoor", "polarity": 0, "frequency": 2,},
                {"name": "pubs", "polarity": 0, "frequency": 5,}, {"name": "rock music", "polarity": 1, "frequency": 6,},
                {"name": "cocktails", "polarity": 1, "frequency": 7,}, {"name": "mocktails", "polarity": 1, "frequency": 11,},
                {"name": "7 degree Brahuas", "polarity": 1, "frequency": 9,}, ], 
                "polarity": 1,
                "frequency": 5},
        {"name": "family",
        "children": [{"name": "live music", "polarity": 1, "frequency": 3,}, {"name": "valet parking", "polarity": 0, "frequency": 4,},
                {"name": "decor", "polarity": 1, "frequency": 5,}, {"name": "lighting", "polarity": 0, "frequency": 4,},
                {"name": "vegetarian", "polarity": 1, "frequency": 10,}, {"name": "mughlai", "polarity": 0, "frequency": 2,},
                {"name": "Haldiram", "polarity": 0, "frequency": 2,}, {"name": "Punjabi by Nature", "polarity": 0, "frequency": 12,},
                {"name": "service", "polarity": 1, "frequency": 2,}, {"name": "7 degree Brahuas", "polarity": 0, "frequency": 8,},],
                "polarity": 1,
                "frequency": 15},
        {"name": "beer cafes",
        "children": [{"name": "happy hours", "polarity": 1, "frequency": 13,}, {"name": "rock music", "polarity": 0, "frequency": 4,},
                {"name": "outdoor", "polarity": 1, "frequency": 5,}, {"name": "smoking zone", "polarity": 0, "frequency": 4,},
                {"name": "valet for money", "polarity": 1, "frequency": 10,}, {"name": "vapour", "polarity": 0, "frequency": 2,},
                {"name": "starters", "polarity": 0, "frequency": 2,}, {"name": "brewery", "polarity": 0, "frequency": 12,},
                {"name": "lemp", "polarity": 1, "frequency": 2,},],
                "polarity": 1,
                "frequency": 9},
        {"name": "italian",
        "children": [{"name": "Big Chill", "polarity": 1, "frequency": 3,},
                {"name": "California pizza Kitchen", "polarity": 0, "frequency": 14,},
                {"name": "clay oven baked pizza", "polarity": 1, "frequency": 5,}, {"name": "cheese", "polarity": 0, "frequency": 14,},
                {"name": "rissotto", "polarity": 1, "frequency": 10,},
                {"name": "ravioli", "polarity": 0, "frequency": 6,}, {"name": "fondue", "polarity": 0, "frequency": 4,},
                {"name": "Home Delivery", "polarity": 0, "frequency": 12,}, {"name": "amici", "polarity": 1, "frequency": 12,},],
                "polarity": 1,
                "frequency": 5},
        {"name": "Amici",
        "children": [{"name": "Cheese pizza", "polarity": 1, "frequency": 3,}, {"name": "lassagne", "polarity": 0, "frequency": 4,},
                {"name": "ambience", "polarity": 1, "frequency": 5,}, {"name": "seating arrangement", "polarity": 0, "frequency": 4,},
                {"name": "painted wall", "polarity": 1, "frequency": 10,}, {"name": "service", "polarity": 0, "frequency": 2,},
                {"name": "cost", "polarity": 0, "frequency": 2,}, {"name": "Parking", "polarity": 0, "frequency": 12,},
                {"name": "location", "polarity": 1, "frequency": 2,},],
                "polarity": 0,
                "frequency": 6},
        ]










connection = pymongo.Connection()
db = connection.modified_canworks
eateries = db.eatery
reviews = db.review


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



##ProcessText
different_algorithms_parser = reqparse.RequestParser()
different_algorithms_parser.add_argument('text', type=to_unicode_or_bust, required=True, location="form")
different_algorithms_parser.add_argument('sentences_with_classification', type=to_unicode_or_bust, required=True, location="form", action="append")




##ProcessText
process_text_parser = reqparse.RequestParser()
process_text_parser.add_argument('text', type=to_unicode_or_bust, required=True, location="form")
process_text_parser.add_argument('algorithm', type=str, required=True, location="form")

##UpdateModel
update_model_parser = reqparse.RequestParser()
update_model_parser.add_argument('sentence', type=to_unicode_or_bust, required=True, location="form")
update_model_parser.add_argument('tag', type=str, required=True, location="form")
update_model_parser.add_argument('review_id', type=str, required=True, location="form")

##UpdateReviewError
update_review_error_parser = reqparse.RequestParser()
update_review_error_parser.add_argument('sentence', type=to_unicode_or_bust, required=True, location="form")
update_review_error_parser.add_argument('is_error', type=str, required=True, location="form")
update_review_error_parser.add_argument('review_id', type=str, required=True, location="form")
update_review_error_parser.add_argument('error_messege', type=str, required=True, location="form")


##UploadInterjectionError
upload_interjection_error_parser = reqparse.RequestParser()
upload_interjection_error_parser.add_argument('sentence', type=str,  required=True, location="form")
upload_interjection_error_parser.add_argument('is_error', type=str,  required=True, location="form")
upload_interjection_error_parser.add_argument('review_id', type=str,  required=True, location="form")

##UpdateCustomer
update_customer_parser = reqparse.RequestParser()
update_customer_parser.add_argument('sentence', type=str,  required=True, location="form")
update_customer_parser.add_argument('option_value', type=str,  required=True, location="form")
update_customer_parser.add_argument('option_text', type=str,  required=True, location="form")
update_customer_parser.add_argument('review_id', type=str,  required=True, location="form")

##EateriesList
eateries_list_parser = reqparse.RequestParser()
eateries_list_parser.add_argument('city', type=str,  required=True, location="form")
	
##EateriesDetails
eateries_details_parser = reqparse.RequestParser()
eateries_details_parser.add_argument('eatery_id', type=str,  required=True, location="form")


##UpdateReviewClassification
update_review_classification_parser = reqparse.RequestParser()
update_review_classification_parser.add_argument('review_id', type=str,  required=True, location="form")

	
##GetReviewDetails
get_review_details_parser = reqparse.RequestParser()
get_review_details_parser.add_argument('review_id', type=str,  required=True, location="form")

##GetNgramsParser
get_ngrams_parser = reqparse.RequestParser()
get_ngrams_parser.add_argument('sentence', type=str,  required=True, location="form")
get_ngrams_parser.add_argument('grams', type=str,  required=True, location="form")

	
##UploadNounPhrases
upload_noun_phrases_parser = reqparse.RequestParser()
upload_noun_phrases_parser.add_argument('noun_phrase', type=str,  required=True, location="form")
upload_noun_phrases_parser.add_argument('review_id', type=str,  required=True, location="form")
upload_noun_phrases_parser.add_argument('sentence', type=str,  required=True, location="form")
	
##GetStartDateForRestaurant
get_start_date_for_restaurant_parser = reqparse.RequestParser()
get_start_date_for_restaurant_parser.add_argument('eatery_id', type=str,  required=True, location="form")
word_cloud_with_dates_parser = reqparse.RequestParser()


##WordCloudWithDates
word_cloud_with_dates_parser.add_argument('eatery_id', type=str,  required=True, location="form")
word_cloud_with_dates_parser.add_argument('category', type=str,  required=True, location="form")
word_cloud_with_dates_parser.add_argument('start_date', type=str,  required=True, location="form")
word_cloud_with_dates_parser.add_argument('end_date', type=str,  required=True, location="form")


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



class AlgorithmsComparison(restful.Resource):
	@cors
	def post(self):
		args = different_algorithms_parser.parse_args()
		text = args["text"]
		sentences_with_classification = args["sentences_with_classification"]
	
		print type(sentences_with_classification)
		print len(sentences_with_classification)
		sentences_with_classification = json.loads(sentences_with_classification[0])
		sentences_with_classification = [(element[0].replace("\n", "").replace("\t", ""), element[1]) 
								for element in sentences_with_classification[0: -1]]
	
		print sentences_with_classification
		result = get_all_algorithms_result(text, sentences_with_classification)
	
		return{ 
				"result": result,
				"success": True,
				"error": False,
				}

class OnlyAlgortihmsNames(restful.Resource):
	@cors
	def get(self):
		result = get_all_algorithms_result(if_names=True)
		return{ 
				"result": result,
				"success": True,
				"error": False,
				}




class ProcessText(restful.Resource):
	@cors
	@timeit
	def post(self):
		"""
		This api end point returns the text after processing or classfying with algorithm syupplied in the arguments.
		The algorithms which is now implemented are 
			HMM models
			Maxent Models
			Multinomial Naive bayes 
			Logistic regression models
			Support vector machines models
		"""

		start = time.time()

		args = process_text_parser.parse_args()
		text = args["text"]
		algorithm = args["algorithm"]

		print "this is the fucking algorithm name %s"%algorithm
		if not bool(text):
			return {
				"error": True,
				"success": False,
				"error_code": 101,
				"messege": "Text field cannot be left empty"
				}

		if not bool(algorithm):
			return {
				"error": True,
				"success": False,
				"error_code": 302,
				"messege": "Algorithm field cannot be left empty"
				}

	
		tokenizer = SentenceTokenizationOnRegexOnInterjections()
		tokenized_sentences = tokenizer.tokenize(to_unicode_or_bust(text))
		#predicted = classifier.predict(new_data)
		
		with cd(path_in_memory_classifiers):
			tag_classifier = joblib.load('{0}_tag.lib'.format(algorithm))
			sentiment_classifier = joblib.load('{0}_sentiment.lib'.format(algorithm))
			rp_rc_classifier = joblib.load('{0}_rp_rc.lib'.format(algorithm))
		
		__predicted_tags = tag_classifier.predict(tokenized_sentences)
		__predicted_sentiment = sentiment_classifier.predict(tokenized_sentences)
		__predicted_customers = rp_rc_classifier.predict(tokenized_sentences)



		noun_phrase, result = list(), list()
			
		print zip(tokenized_sentences, __predicted_tags, __predicted_sentiment, __predicted_customers)
		
		print "\n\n%s \n\n"%(time.time() - start)
		instance = ProcessingWithBlobInMemory()
		index = 0
		for chunk in zip(tokenized_sentences, __predicted_tags, __predicted_sentiment, __predicted_customers):
			nouns = instance.noun_phrase(to_unicode_or_bust(chunk[0]))
			element = dict()
			element["sentence"] = chunk[0]
			element["polarity"] = {"name": chunk[2], "value": '0.0'}
			element["noun_phrases"] = list(nouns)
			element["tag"] = chunk[1]
			element["customer_type"] = chunk[3]
			result.append(element)
			noun_phrase.extend(list(nouns))
			index += 1
	
		return {
				"result": result,
				"success": True,
				"error": False,
				"overall_sentiment": '%.2f'%ProcessingWithBlob.new_blob_polarity(to_unicode_or_bust(text)),
				"noun_phrase": noun_phrase,
				}




class UpdateModel(restful.Resource):
	@cors
	def post(self):
		args = update_model_parser.parse_args()
		sentence = args["sentence"]
		tag = args["tag"]
		review_id = args["review_id"]

		path = (os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/trainers/valid_%s.txt"%tag))
	
		if not os.path.exists(path):
			return {"success": False,
					"error": True,
					"messege": "The tag {0} you mentioned doesnt exist in the learning model, ask admin to create this file".format(tag),
					"error_code": 201,
				}



		reviews.update({"review_id": review_id}, {"$push": {tag: sentence}}, upsert=False)
		with open(path, "a") as myfile:
			myfile.write(sentence)
			myfile.write("\n")
	
		return {"success":  True,
			"error": False,
			"messege": "The sentence --{0}-- with the changed tag --{1}-- with id --{2} has been uploaded".format(sentence, tag, review_id),
			}
	
class UpdateReviewError(restful.Resource):
	@cors
	def post(self):
		args = update_review_error_parser.parse_args()
		sentence = args["sentence"]
		error = args["is_error"]
		review_id = args["review_id"]
		error_messege = args["error_messege"]

		if int(error) != 2:
			return {"success": False,
					"error": True,
					"messege": "Only error sentences can be tagged, 'void' is an invalid tag",
					"error_code": 207,
				}
	
		path = (os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/trainers/valid_%s.txt"%'error'))
		if not os.path.exists(path):
			return {"success": False,
					"error": True,
					"messege": "some error occurred",
					"error_code": 210,
				}
	
	
	
		reviews.update({"review_id": review_id}, {"$push": {"error": {"sentence": sentence, "error_messege": error_messege}}}, upsert=False)
		with open(path, "a") as myfile:
			myfile.write(sentence)
			myfile.write("\n")
	
		return {"success":  True,
			"error": False,
			"messege": "The sentence --{0}-- with the error messege --{1}-- with id --{2} has been uploaded".format(sentence, error_messege, review_id),
			}
	

class UploadInterjectionError(restful.Resource):
	@cors
	def post(self):
		args = upload_interjection_error_parser.parse_args()
		sentence = args["sentence"]
		error = args["is_error"]
		review_id = args["review_id"]
		if int(error) != 3:
			return {"success": False,
					"error": True,
					"messege": "Only interjection sentences can be tagged, 'void' is an invalid tag",
					"error_code": 207,
					}

		path = (os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/trainers/valid_%s.txt"%'interjection'))
		if not os.path.exists(path):
			return {"success": False,
					"error": True,
					"messege": "File doenst exists for interjection",
					"error_code": 210,
				}



		reviews.update({"review_id": review_id}, {"$push": {"interjection": {"sentence": sentence}}}, upsert=False)
		with open(path, "a") as myfile:
			myfile.write(sentence)
			myfile.write("\n")
	
		return {"success":  True,
			"error": False,
			"messege": "The sentence --{0}-- with id --{1} has been uploaded for interjection erros".format(sentence, review_id),
			}


class UpdateCustomer(restful.Resource):
	@cors
	def post(self):
		args = update_customer_parser.parse_args()
		sentence = args["sentence"]
		option_value = args["option_value"]
		option_text = "_".join(args["option_text"].split())
		review_id = args["review_id"]

		if int(option_value) != 2 and int(option_value) != 3:
			return {"success": False,
					"error": True,
					"messege": "Only repeated customer or recommended customer sentences can be tagged, 'void' is an invalid tag",
					"error_code": 206,
				}
	
		path = (os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/trainers/valid_%s.txt"%option_text))
	
		if not os.path.exists(path):
			return {"success": False,
					"error": True,
					"messege": "File for {0} doesnt exists in the backend, Please contact your asshole admin".format(option_text),
					"error_code": 205,
				}



		with open(path, "a") as myfile:
			myfile.write(sentence)
			myfile.write("\n")
	
	
	
		reviews.update({"review_id": review_id}, {"$push": {"{0}s".format(option_text): sentence}})
		return {"success":  True,
			"error": False,
			"messege": "The sentence --{0}-- with review id --{1} has been uploaded for {2}".format(sentence, review_id, option_text),
			}



class EateriesList(restful.Resource):
	@cors
	def post(self):
		args = eateries_list_parser.parse_args()
		city = args["city"]
		result = list(eateries.find({"area_or_city": city }, fields= {"eatery_id": True, "_id": False, "eatery_name": True}))
		return {"success": False,
			"error": True,
			"result": result,
			}



class EateriesDetails(restful.Resource):
	@cors
	def post(self):
		args = eateries_details_parser.parse_args()
		__id = args["eatery_id"]
	
		result = eateries.find_one({"eatery_id": __id}, fields= {"_id": False})
		is_classified_reviews = list(reviews.find({"eatery_id": __id, "is_classified": True}, fields= {"_id": False}))
		not_classified_reviews = list(reviews.find({"eatery_id": __id, "is_classified": False}, fields= {"_id": False}))
	
		return {"success": False,
			"error": True,
			"result": result,
			"classified_reviews": is_classified_reviews,
			"unclassified_reviews": not_classified_reviews,
			}




class UpdateReviewClassification(restful.Resource):
	@cors
	def post(self):
		args = update_review_classification_parser.parse_args()
		__id = args["review_id"]

		if not reviews.find_one({'review_id': __id}):
			return {"success": False,
					"error": True,
					"messege": "The review doesnt exists",
			}

		if reviews.find_one({'review_id': __id}).get("is_classified"):
			return {"success": False,
					"error": True,
					"messege": "The reviews has already been marked classified, Please refresh the page",
			}
	
	
	
		reviews.update({'review_id': __id}, {"$set":{ "is_classified": True, "classified_at": time.time()}}, upsert=False)
		return {"success": True,
					"error": False,
					"messege": "The reviews has been marked classified",
			}

	
	
class GetReviewDetails(restful.Resource):
	@cors
	def post(self):
		args = get_review_details_parser.parse_args()
		__id = args["review_id"]

		if not reviews.find_one({'review_id': __id}):
			return {"success": False,
					"error": True,
					"messege": "The review doesnt exists",
			}
			
		result = reviews.find_one({'review_id': __id}, fields={"_id": False})
		return {"success": True,
					"error": False,
					"result": result,
			}



class GetNgramsParser(restful.Resource):
	@cors
	def post(self):
		args = get_ngrams_parser.parse_args()
		sentence = args["sentence"]
		grams = args["grams"]
		if not sentence:
			return {"success": False,
					"error": True,
					"messege": "The text field cannot be left empty",
			}
		
		if not grams:
			return {"success": False,
					"error": True,
					"messege": "The grams field cannot be left empty",
			}
	
		if grams == "void":
			return {"success": False,
					"error": True,
					"messege": "The grams field cannot be equals to void",
			}


		return {"success": True,
					"error": False,
					"result": nltk_ngrams(sentence, grams),
			}



class UploadNounPhrases(restful.Resource):
	@cors
	def post(self):
		args = upload_noun_phrases_parser.parse_args()
		noun_phrase = args["noun_phrase"]
		review_id = args["review_id"]
		sentence = args["sentence"]
		if not reviews.find_one({'review_id': review_id}):
			return {"success": False,
					"error": True,
					"messege": "The review doesnt exists",
			}
	
		if not noun_phrase:
			return {"success": False,
					"error": True,
					"messege": "The Noun phrase field cannot be left empty",
			}
		
		reviews.update({"review_id": review_id}, {"$push": {"noun_phrases": {"sentence": sentence, "phrase": noun_phrase}}}, upsert=False)
		return {"success": True,
					"error": False,
					"messege": "noun phrase --{0}-- for sentence --{1}-- with review id --<{2}>--has been uploaded".format(noun_phrase, sentence, review_id),
			}

class GetReviewCount(restful.Resource):
	@cors
	def get(self):
		"""
		({(u'ncr', False): 20607, (u'mumbai', False): 14770, (u'bangalore', False): 12534, (u'kolkata', False): 10160, (u'chennai', False): 8283, (u'pune', False): 7107, (u'hyderabad', False): 6525, (u'ahmedabad', False): 5936, (u'chandigarh', False): 3446, (u'jaipur', False): 3269, (u'guwahati', False): 1244, (u'ncr', True): 1})
	
	
		[{'city': 'ncr', 'classfied': 1, 'unclassfied': 20607}, {'city': 'mumbai', 'classfied': 0, 'unclassfied': 14770},
		{'city': 'bangalore', 'classfied': 0, 'unclassfied': 12534}, {'city': 'kolkata', 'classfied': 0, 'unclassfied': 10160},
		{'city': 'chennai', 'classfied': 0, 'unclassfied': 8283}, {'city': 'pune', 'classfied': 0, 'unclassfied': 7107},
		{'city': 'hyderabad', 'classfied': 0, 'unclassfied': 6525}, {'city': 'ahmedabad', 'classfied': 0, 'unclassfied': 5936},
		{'city': 'chandigarh', 'classfied': 0, 'unclassfied': 3446}, {'city': 'jaipur', 'classfied': 0, 'unclassfied': 3269},
		{'city': 'guwahati', 'classfied': 0, 'unclassfied': 1244}]
		"""
		dictionary = Counter([(post.get("area_or_city"), post.get("is_classified")) for post in reviews.find(fields={"_id": False})])
		cities = ['ncr', 'mumbai', 'bangalore', 'kolkata', 'chennai', 'pune', 'hyderabad', 'ahmedabad', 'chandigarh', 'jaipur', 'guwahati']	
		result = [{"city": city, "classified": dictionary[(city, True)], "unclassified": dictionary[(city, False)]} for city in cities]
	
		total_classified = sum([entry.get("classified") for entry in result])
		total_unclassified = sum([entry.get("unclassified") for entry in result])

		result.append({"city": "Total", "classified": total_classified, "unclassified": total_unclassified})
		return {"success": True,
				"error": True,
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
	



class WordCloudWithDates(restful.Resource):
	@cors
	def post(self):
		args = word_cloud_with_dates_parser.parse_args()
		__format = '%Y-%m-%d'
		eatery_id = args["eatery_id"]
		category = args["category"].split("__")[1].lower()
		start_epoch = time.mktime(time.strptime(args["start_date"], __format))
		end_epoch = time.mktime(time.strptime(args["end_date"], __format))


	
		polarity=lambda x: "positive" if float(x)>= 0 else "negative"
		
	
		review_result = list(reviews.find({"eatery_id" :eatery_id, "converted_epoch": {"$gt":  start_epoch, "$lt" : end_epoch}}))
	
		noun_phrases_dictionary = dict.fromkeys([review.get("review_time").split(" ")[0] for review in review_result], list())
	
		for review in review_result:
			date = review.get("review_time").split(" ")[0]
			text_classfication = Classifier(to_unicode_or_bust(review.get("review_text")))
			filtered_tag_text = [text[0] for text in text_classfication.with_svm() if text[1] == category]
			for text in filtered_tag_text:
				instance = ProcessingWithBlob(to_unicode_or_bust(text))
				#per_review.extend([(noun.lower(),  polarity(instance.sentiment_polarity())) for noun in instance.noun_phrase()])
				noun_phrases_dictionary[date] = noun_phrases_dictionary[date] + [(noun.lower(),  polarity(instance.sentiment_polarity())) for noun in instance.noun_phrase()]
	
	
	
		#The abobve noun phrase dictionary is in the form of {"2014-9-10": ["phrases", "phrases", ....], ..., ... }
		#This should be converted into the form of list of dictionaries with "Date" key corresponds to date and "[hrase" key corresponds to the 
		#phrases asccociated with this date
	
		result = [{"date": key, "phrases": noun_phrases_dictionary[key]} for key in noun_phrases_dictionary.keys()]
	
		return {"success": True,
				"error": True,
				"result": result
		}


class GetWordCloud(restful.Resource):
	@cors
	@timeit
	def post(self):
		return {"success": True,
				"error": True,
				"result": DATA,
		}
		start = time.time()


		args = get_word_cloud_parser.parse_args()
		__format = '%Y-%m-%d'
		eatery_id = args["eatery_id"]
		category = args["category"].split("__")[1].lower()
		
		try:
			start_epoch = time.mktime(time.strptime(args["start_date"], __format))
			end_epoch = time.mktime(time.strptime(args["end_date"], __format))
		except Exception:
			return {"success": False,
				"error": "Dude!!, Please wait for the dates to be updated",
			}
	
		
		
		noun_phrases_list = list()
	
		review_result = reviews.find({"eatery_id" :eatery_id, "converted_epoch": {"$gt":  start_epoch, "$lt" : end_epoch}})
	
		review_text = [to_unicode_or_bust(post.get("review_text")) for post in review_result]
		review_text = " .".join(review_text)

		
		with cd(path_in_memory_classifiers):
			tag_classifier = joblib.load('svm_grid_search_classifier_tag.lib')
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
		
		for text in filtered_tag_text:
			noun_phrases_list.extend([(noun.lower(),  text[2]) for noun in instance.noun_phrase(to_unicode_or_bust(text[0]))])


		
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



		def merging_similar_elements(original_list):
			"""
			This function will calculate the minum distance between two noun phrase and if the distance is 
			less than 1 and more than .8, delete one of the element and add both their frequencies
			"""

			original_dict = {element.get("name"): {"frequency": element.get("frequency"), "polarity": element.get("polarity")} \
					for element in original_list}
			
			
			calc_simililarity = lambda __a, __b: difflib.SequenceMatcher(a=__a.get("name").lower(), b=__b.get("name").lower()).ratio() \
										if __a.get("name").lower() != __b.get("name").lower() else 0
			
			
			list_with_similarity_ratios = list()
			for test_element in original_list:
				for another_element in copy.copy(original_list):
					r = calc_simililarity(test_element, another_element)	
					list_with_similarity_ratios.append(dict(test_element.items() +  
							{"similarity_with": another_element.get("name"), "ratio": r}.items()))

			

			filtered_list = [element for element in list_with_similarity_ratios if element.get("ratio") <1 and element.get("ratio") > .8]



			
			for element in filtered_list:
				try:
					frequency = original_dict[element.get("name")]["frequency"] + \
							original_dict[element.get("similarity_with")]["frequency"]
							
					del original_dict[element.get("similarity_with")]
					original_dict[element.get("name")]["frequency"] = frequency
					
				except Exception as e:
					pass

			"""
			##This is when you want to subtract and add frequency based on the polarity
			for element in filtered_list:
				try:
					if original_dict[element.get("similarity_with")]["polarity"] == 0:
						frequency = original_dict[element.get("name")]["frequency"] - original_dict[element.get("similarity_with")]["frequency"]
					else:
						frequency = original_dict[element.get("name")]["frequency"] + original_dict[element.get("similarity_with")]["frequency"]

					del original_dict[element.get("similarity_with")]
					original_dict[element.get("name")]["frequency"] = frequency
					
				except Exception as e:
					pass
			"""
			result = list()

	
			for k, v in original_dict.iteritems():
				l = {"name": k.upper()}
				l.update(v)
				result.append(l)

			
			return  result

		
		final_result = sorted(merging_similar_elements(sorted_result), reverse=True, key=lambda x: x.get("frequency"))

                print final_result
		return {"success": True,
				"error": True,
				"result": final_result[0:100],
		}
	
	
class GetValidFilesCount(restful.Resource):
	@timeit
	@cors
	def get(self):
		"""
		This function counts the number of lines present in the valid files
		It checks how much updation has been done to the valid fieles by the canworks guys
		"""
		result = list()
		file_list =  [os.path.join(file_path + "/" + file) for file in os.listdir(path_trainers_file)]
		
		for file in file_list:
			result.append((file, subprocess.check_output(["wc", "-l", file]).split(" ")[0]))
		return {"success": True,
				"error": True,
				"result": result,
		}






		
api.add_resource(ProcessText, '/process_text')
api.add_resource(UpdateModel, '/update_model')
api.add_resource(UpdateReviewError, '/update_review_error')
api.add_resource(UploadInterjectionError, '/upload_interjection_error')
api.add_resource(UpdateCustomer, '/update_customer')
api.add_resource(EateriesList, '/eateries_list')
api.add_resource(EateriesDetails, '/eateries_details')
api.add_resource(UpdateReviewClassification, '/update_review_classification')
api.add_resource(GetReviewDetails, '/get_review_details')
api.add_resource(GetNgramsParser, '/get_ngrams')
api.add_resource(UploadNounPhrases, '/upload_noun_phrases')
api.add_resource(GetReviewCount, '/get_reviews_count')
api.add_resource(GetStartDateForRestaurant, '/get_start_date_for_restaurant')
api.add_resource(WordCloudWithDates, '/get_word_cloud_with_dates')
api.add_resource(GetWordCloud, '/get_word_cloud')
api.add_resource(GetValidFilesCount, '/get_valid_files_count')
api.add_resource(AlgorithmsComparison, '/compare_algorithms')
api.add_resource(OnlyAlgortihmsNames, '/get_all_algorithms_name')


if __name__ == '__main__':
	#load_classifiers_in_memory()
	app.run(port=8000, debug=True)
