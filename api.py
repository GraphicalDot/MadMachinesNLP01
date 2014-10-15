#!/usr/bin/env python
#-*- coding: utf-8 -*-

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
from bson.json_util import dumps
from Text_Processing import ProcessingWithBlob, PosTags, Classifier, nltk_ngrams, ForTestingClassifier
import time
from datetime import timedelta
import pymongo
from collections import Counter
from functools import wraps

connection = pymongo.Connection()
db = connection.modified_canworks
eateries = db.eatery
reviews = db.review

app = Flask(__name__)
api = restful.Api(app)

def to_unicode_or_bust(obj, encoding='utf-8'):
	if isinstance(obj, basestring):
		if not isinstance(obj, unicode):
			obj = unicode(obj, encoding)
	return obj




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


def to_unicode_or_bust(obj, encoding='utf-8'):
	if isinstance(obj, basestring):
		if not isinstance(obj, unicode):
			obj = unicode(obj, encoding)
	return obj



class ProcessText(restful.Resource):
	@cors
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
		args = process_text_parser.parse_args()
		text = args["text"]
		algorithm = args["algorithm"]

		if not bool(text):
			return jsonify({
				"error": True,
				"success": False,
				"error_code": 101,
				"messege": "Text field cannot be left empty"
				})

		if not bool(algorithm):
			return jsonify({
				"error": True,
				"success": False,
				"error_code": 302,
				"messege": "Algorithm field cannot be left empty"
				})


		text_classfication = ForTestingClassifier(to_unicode_or_bust(text))	
		noun_phrase = list()
		result = list() 

		polarity=lambda x: "positive" if float(x)>= 0 else "negative"

		classified_sentences = eval("{0}.with_{1}()".format("text_classfication", algorithm.lower()))

		##with svm returns a list in the following form
		##[(sentence, tag), (sentence, tag), ................]
		#for chunk in text_classfication.with_svm():
		
		
		for chunk in classified_sentences:
			element = dict()
			instance = ProcessingWithBlob(chunk[0])
			element["sentence"] = chunk[0]
			element["polarity"] = {"name": polarity('%.1f'%instance.sentiment_polarity()), "value": '%.1f'%instance.sentiment_polarity()}
			element["noun_phrases"] = list(instance.noun_phrase())
			element["tag"] = chunk[1]
			result.append(element)
			noun_phrase.extend(list(instance.noun_phrase()))

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
	
	
	
		reviews.update({'review_id': __id}, {"$set":{ "is_classified": True}}, upsert=False)
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
	def post(self):
		args = get_word_cloud_parser.parse_args()
		__format = '%Y-%m-%d'
		eatery_id = args["eatery_id"]
		category = args["category"].split("__")[1].lower()
		start_epoch = time.mktime(time.strptime(args["start_date"], __format))
		end_epoch = time.mktime(time.strptime(args["end_date"], __format))
	
	
		print category, eatery_id, request.form["start_date"], request.form["end_date"], start_epoch, end_epoch
		
		polarity=lambda x: "positive" if float(x)>= 0 else "negative"
		
		noun_phrases_list = list()
	
		review_result = reviews.find({"eatery_id" :eatery_id, "converted_epoch": {"$gt":  start_epoch, "$lt" : end_epoch}})
	
	
	
		for review in review_result:
	
			text_classfication = Classifier(to_unicode_or_bust(review.get("review_text")))
			filtered_tag_text = [text[0] for text in text_classfication.with_svm() if text[1] == category]
			for text in filtered_tag_text:
				instance = ProcessingWithBlob(to_unicode_or_bust(text))
				noun_phrases_list.extend([(noun.lower(),  polarity(instance.sentiment_polarity())) for noun in instance.noun_phrase()])
	
	
	
		result = list()
		for key, value in Counter(noun_phrases_list).iteritems():
			result.append({"name": key[0], "polarity": key[1], "frequency": value}) 
		
		return {"success": True,
				"error": True,
				"result": result,
		}
	

class GetValidFilesCount(restful.Resource):
	@cors
	def get(self):
		"""
		This function counts the number of lines present in the valid files
		It checks how much updation has been done to the valid fieles by the canworks guys
		"""
		result = list()
		path = os.path.dirname(os.path.abspath(__file__))	
		file_path = os.path.join(path + "/trainers")
		file_list =  [os.path.join(file_path + "/" + file) for file in os.listdir(file_path)]
		
		for file in file_list:
			result.append((file, subprocess.check_output(["wc", "-l", file]).split(" ")[0]))
		return {"success": True,
				"error": True,
				"result": result,
		}






class cd:
        def __init__(self, newPath):
                self.newPath = newPath

        def __enter__(self):
                self.savedPath = os.getcwd()
                os.chdir(self.newPath)

        def __exit__(self, etype, value, traceback):
                os.chdir(self.savedPath)
		
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


if __name__ == '__main__':
    app.run(port=8000, debug=True)
