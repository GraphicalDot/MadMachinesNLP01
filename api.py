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
from static_data import static_data
from api_helpers import merging_similar_elements



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





##GetWordCloud
get_word_cloud_parser = reqparse.RequestParser()
get_word_cloud_parser.add_argument('eatery_id', type=str,  required=True, location="form")
get_word_cloud_parser.add_argument('category', type=str,  required=True, location="form")





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




class EateriesList(restful.Resource):
	@cors
	def get(self):
		result = list(eateries.find({"area_or_city": "ncr" }, fields= {"eatery_id": True, "_id": False, "eatery_name": True}))
		
                return {"success": False,
			"error": True,
			"result": result,
			}





class GetWordCloud(restful.Resource):
	@cors
	@timeit
        def post(self):
		start = time.time()


		args = get_word_cloud_parser.parse_args()
		__format = '%Y-%m-%d'
		eatery_id = args["eatery_id"]
		category = args["category"]
		
                if not reviews.find({"eatery_id": eatery_id}):
                        return {"error": True,
                                "success": False,
                                "error_messege": "The eatery id  {0} is not present".format(eatery_id), 
                                }

                if category not in ["service", "food", "ambience", "null", "overall", "cost"]:
                        return {"error": True,
                                "success": False,
                                "error_messege": "This is a n invalid tag %s"%category, 
                                }
                        


		noun_phrases_list = list()


                #This is mongodb query for the arguments given int he post request, And the result is a list of reviews
		review_result = reviews.find({"eatery_id" :eatery_id})
	
            
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

		"""
		#final_result = sorted(merging_similar_elements(sorted_result), reverse=True, key=lambda x: x.get("frequency"))
                
                for element in final_result:
                    print element 
                
                """
                final_result = sorted(sorted_result, reverse=True, key=lambda x: x.get("frequency"))

		
                return {"success": True,
				"error": True,
				"result": final_result[0:15],
		}
	



api.add_resource(EateriesList, '/eateries_list')
api.add_resource(GetWordCloud, '/get_word_cloud')


if __name__ == '__main__':
        #load_classifiers_in_memory()
	app.run(port=8000, debug=True)
