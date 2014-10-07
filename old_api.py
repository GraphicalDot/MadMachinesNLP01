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
from Text_Processing import ProcessingWithBlob, PosTags, Classifier, nltk_ngrams
import time
from datetime import timedelta
import pymongo
from collections import Counter

connection = pymongo.Connection()
db = connection.modified_canworks
eateries = db.eatery
reviews = db.review

app = Flask(__name__)


def to_unicode_or_bust(obj, encoding='utf-8'):
	if isinstance(obj, basestring):
		if not isinstance(obj, unicode):
			obj = unicode(obj, encoding)
	return obj

def crossdomain(origin=None, methods=None, headers=None, max_age=21600, attach_to_all=True, automatic_options=True):
	if methods is not None:
		methods = ', '.join(sorted(x.upper() for x in methods))
        
	if headers is not None and not isinstance(headers, basestring):
		headers = ', '.join(x.upper() for x in headers)
	
	if not isinstance(origin, basestring):
		origin = ', '.join(origin)
        
	if isinstance(max_age, timedelta):
		max_age = max_age.total_seconds()

	def get_methods():
		if methods is not None:
			return methods
		options_resp = current_app.make_default_options_response()
		return options_resp.headers['allow']

	def decorator(f):
		def wrapped_function(*args, **kwargs):
			if automatic_options and request.method == 'OPTIONS':
				resp = current_app.make_default_options_response()
			else:
				resp = make_response(f(*args, **kwargs))
				
			if not attach_to_all and request.method != 'OPTIONS':
				return resp
			
			h = resp.headers
			h['Access-Control-Allow-Origin'] = origin
			h['Access-Control-Allow-Methods'] = get_methods()
			h['Access-Control-Max-Age'] = str(max_age)
			h['Content-Type'] = "application/json"
			
			if headers is not None:
				h['Access-Control-Allow-Headers'] = headers
			return resp

		f.provide_automatic_options = False
		return update_wrapper(wrapped_function, f)
	return decorator

@app.route('/process_text', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*', headers='Content-Type')
def return_processed_text():
		text = request.form["text"]
		if not bool(text):
			return jsonify({
				"error": True,
				"success": False,
				"error_code": 101,
				"messege": "Text field cannot be left empty"
				})


		text_classfication = Classifier(to_unicode_or_bust(text))	
		noun_phrase = list()
		result = list() 

		polarity=lambda x: "positive" if float(x)>= 0 else "negative"


		##with svm returns a list in the following form
		##[(sentence, tag), (sentence, tag), ................]
		for chunk in text_classfication.with_svm():
			print chunk
			element = dict()
			instance = ProcessingWithBlob(chunk[0])
			element["sentence"] = chunk[0]
			element["polarity"] = {"name": polarity('%.1f'%instance.sentiment_polarity()), "value": '%.1f'%instance.sentiment_polarity()}
			print {"name": polarity('%.1f'%instance.sentiment_polarity()), "value": '%.1f'%instance.sentiment_polarity()}, "\n\n"
			element["noun_phrases"] = list(instance.noun_phrase())
			element["tag"] = chunk[1]
			result.append(element)
			noun_phrase.extend(list(instance.noun_phrase()))

		return jsonify({
				"result": result,
				"success": True,
				"error": False,
				"overall_sentiment": '%.2f'%ProcessingWithBlob.new_blob_polarity(to_unicode_or_bust(text)),
				"noun_phrase": noun_phrase,
				})

@app.route('/update_model', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*', headers='Content-Type')
def update_model():
	sentence = request.form["sentence"]
	tag = request.form["tag"]
	review_id = request.form["review_id"]

	path = (os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/trainers/valid_%s.txt"%tag))
	
	if not os.path.exists(path):
		return jsonify({"success": False,
				"error": True,
				"messege": "The tag {0} you mentioned doesnt exist in the learning model, ask admin to create this file".format(tag),
				"error_code": 201,
			})



	reviews.update({"review_id": review_id}, {"$push": {tag: sentence}}, upsert=False)
	with open(path, "a") as myfile:
		myfile.write(sentence)
		myfile.write("\n")

	return jsonify({"success":  True,
		"error": False,
		"messege": "The sentence --{0}-- with the changed tag --{1}-- with id --{2} has been uploaded".format(sentence, tag, review_id),
		})


@app.route('/update_review_error', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*', headers='Content-Type')
def update_review_error():
	sentence = request.form["sentence"]
	error = request.form["is_error"]
	review_id = request.form["review_id"]
	error_messege = request.form["error_messege"]
	
	if int(error) != 2:
		return jsonify({"success": False,
				"error": True,
				"messege": "Only error sentences can be tagged, 'void' is an invalid tag",
				"error_code": 207,
			})

	path = (os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/trainers/valid_%s.txt"%'error'))
	if not os.path.exists(path):
		return jsonify({"success": False,
				"error": True,
				"messege": "some error occurred",
				"error_code": 210,
			})



	reviews.update({"review_id": review_id}, {"$push": {"error": {"sentence": sentence, "error_messege": error_messege}}}, upsert=False)
	with open(path, "a") as myfile:
		myfile.write(sentence)
		myfile.write("\n")

	return jsonify({"success":  True,
		"error": False,
		"messege": "The sentence --{0}-- with the error messege --{1}-- with id --{2} has been uploaded".format(sentence, error_messege, review_id),
		})


@app.route('/upload_interjection_error', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*', headers='Content-Type')
def upload_interjection_error():
	sentence = request.form["sentence"]
	error = request.form["is_error"]
	review_id = request.form["review_id"]
	
	if int(error) != 3:
		return jsonify({"success": False,
				"error": True,
				"messege": "Only interjection sentences can be tagged, 'void' is an invalid tag",
				"error_code": 207,
			})

	path = (os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/trainers/valid_%s.txt"%'interjection'))
	if not os.path.exists(path):
		return jsonify({"success": False,
				"error": True,
				"messege": "File doenst exists for interjection",
				"error_code": 210,
			})



	reviews.update({"review_id": review_id}, {"$push": {"interjection": {"sentence": sentence}}}, upsert=False)
	with open(path, "a") as myfile:
		myfile.write(sentence)
		myfile.write("\n")

	return jsonify({"success":  True,
		"error": False,
		"messege": "The sentence --{0}-- with id --{1} has been uploaded for interjection erros".format(sentence, review_id),
		})


@app.route('/update_customer', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*', headers='Content-Type')
def update_customer():
	sentence = request.form["sentence"]
	option_value = request.form["option_value"]
	option_text = "_".join(request.form["option_text"].split())
	review_id = request.form["review_id"]

	if int(option_value) != 2 and int(option_value) != 3:
		return jsonify({"success": False,
				"error": True,
				"messege": "Only repeated customer or recommended customer sentences can be tagged, 'void' is an invalid tag",
				"error_code": 206,
			})
	
	path = (os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/trainers/valid_%s.txt"%option_text))

	if not os.path.exists(path):
		return jsonify({"success": False,
				"error": True,
				"messege": "File for {0} doesnt exists in the backend, Please contact your asshole admin".format(option_text),
				"error_code": 205,
			})



	with open(path, "a") as myfile:
		myfile.write(sentence)
		myfile.write("\n")



	reviews.update({"review_id": review_id}, {"$push": {"{0}s".format(option_text): sentence}})
	return jsonify({"success":  True,
		"error": False,
		"messege": "The sentence --{0}-- with review id --{1} has been uploaded for {2}".format(sentence, review_id, option_text),
		})



@app.route('/eateries_list', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*', headers='Content-Type')
def eateries_list():
	city = request.form["city"]
	result = list(eateries.find({"area_or_city": city }, fields= {"eatery_id": True, "_id": False, "eatery_name": True}))
	return jsonify({"success": False,
				"error": True,
				"result": result,
		})



	
@app.route('/eateries_details', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*', headers='Content-Type')
def eateries_details():
	id = request.form["eatery_id"]
	result = eateries.find_one({"eatery_id": id}, fields= {"_id": False})
	is_classified_reviews = list(reviews.find({"eatery_id": id, "is_classified": True}, fields= {"_id": False}))
	not_classified_reviews = list(reviews.find({"eatery_id": id, "is_classified": False}, fields= {"_id": False}))

	return jsonify({"success": False,
				"error": True,
				"result": result,
				"classified_reviews": is_classified_reviews,
				"unclassified_reviews": not_classified_reviews,
				})





@app.route('/update_review_classification', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*', headers='Content-Type')
def update_review_classification():
	id = request.form["review_id"]
	if not reviews.find_one({'review_id': id}):
		return jsonify({"success": False,
				"error": True,
				"messege": "The review doesnt exists",
		})
		return 

	if reviews.find_one({'review_id': id}).get("is_classified"):
		return jsonify({"success": False,
				"error": True,
				"messege": "The reviews has already been marked classified, Please refresh the page",
		})



	reviews.update({'review_id': id}, {"$set":{ "is_classified": True}}, upsert=False)
	return jsonify({"success": True,
				"error": False,
				"messege": "The reviews has been marked classified",
		})

	
	
@app.route('/get_review_details', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*', headers='Content-Type')
def get_review_details():
	id = request.form["review_id"]
	if not reviews.find_one({'review_id': id}):
		return jsonify({"success": False,
				"error": True,
				"messege": "The review doesnt exists",
		})
	
	result = reviews.find_one({'review_id': id}, fields={"_id": False})
	return jsonify({"success": True,
				"error": False,
				"result": result,
		})

@app.route('/get_ngrams', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*', headers='Content-Type')
def get_ngrams():
	sentence = request.form["sentence"]
	grams = request.form["grams"]
	if not sentence:
		return jsonify({"success": False,
				"error": True,
				"messege": "The text field cannot be left empty",
		})
	
	if not grams:
		return jsonify({"success": False,
				"error": True,
				"messege": "The grams field cannot be left empty",
		})

	if grams == "void":
		return jsonify({"success": False,
				"error": True,
				"messege": "The grams field cannot be equals to void",
		})


	return jsonify({"success": True,
				"error": False,
				"result": nltk_ngrams(sentence, grams),
		})


@app.route('/upload_noun_phrases', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*', headers='Content-Type')
def upload_noun_phrases():
	noun_phrase = request.form["noun_phrase"]
	review_id = request.form["review_id"]
	sentence = request.form["sentence"]
	if not reviews.find_one({'review_id': review_id}):
		return jsonify({"success": False,
				"error": True,
				"messege": "The review doesnt exists",
		})

	if not noun_phrase:
		return jsonify({"success": False,
				"error": True,
				"messege": "The Noun phrase field cannot be left empty",
		})
	
	reviews.update({"review_id": review_id}, {"$push": {"noun_phrases": {"sentence": sentence, "phrase": noun_phrase}}}, upsert=False)
	return jsonify({"success": True,
				"error": False,
				"messege": "noun phrase --{0}-- for sentence --{1}-- with review id --<{2}>--has been uploaded".format(noun_phrase, sentence, review_id),
		})



@app.route('/get_reviews_count', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*', headers='Content-Type')
def get_reviews_count():
	"""
	({(u'ncr', False): 20607, (u'mumbai', False): 14770, (u'bangalore', False): 12534, (u'kolkata', False): 10160, (u'chennai', False): 8283, (u'pune', False): 7107, (u'hyderabad', False): 6525, (u'ahmedabad', False): 5936, (u'chandigarh', False): 3446, (u'jaipur', False): 3269, (u'guwahati', False): 1244, (u'ncr', True): 1})
	
	
	[{'city': 'ncr', 'classfied': 1, 'unclassfied': 20607}, {'city': 'mumbai', 'classfied': 0, 'unclassfied': 14770},
	{'city': 'bangalore', 'classfied': 0, 'unclassfied': 12534}, {'city': 'kolkata', 'classfied': 0, 'unclassfied': 10160},
	{'city': 'chennai', 'classfied': 0, 'unclassfied': 8283}, {'city': 'pune', 'classfied': 0, 'unclassfied': 7107},
	{'city': 'hyderabad', 'classfied': 0, 'unclassfied': 6525}, {'city': 'ahmedabad', 'classfied': 0, 'unclassfied': 5936},
	{'city': 'chandigarh', 'classfied': 0, 'unclassfied': 3446}, {'city': 'jaipur', 'classfied': 0, 'unclassfied': 3269},
	{'city': 'guwahati', 'classfied': 0, 'unclassfied': 1244}]
	
	"""
	dictionary = Counter([(post.get("area_or_city"), post.get("is_classified")) for post in reviews.find()])
	cities = ['ncr', 'mumbai', 'bangalore', 'kolkata', 'chennai', 'pune', 'hyderabad', 'ahmedabad', 'chandigarh', 'jaipur', 'guwahati']	
	result = [{"city": city, "classified": dictionary[(city, True)], "unclassified": dictionary[(city, False)]} for city in cities]

	return jsonify({"success": True,
			"error": True,
			"result": result,
	})


@app.route('/get_start_date_for_restaurant', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*', headers='Content-Type')
def get_start_date_for_restaurant():
	eatery_id = request.form["eatery_id"]
	sorted_list_by_epoch = list(reviews.find({"eatery_id" :eatery_id}).sort("converted_epoch", 1))
	start_date = sorted_list_by_epoch[0].get('readable_review_day')
	start_month = sorted_list_by_epoch[0].get('readable_review_month')
	start_year = sorted_list_by_epoch[0].get('readable_review_year')
	
	end_date = sorted_list_by_epoch[-1].get('readable_review_day')
	end_month = sorted_list_by_epoch[-1].get('readable_review_month')
	end_year = sorted_list_by_epoch[-1].get('readable_review_year')
	
	
	
	
	return jsonify({"success": True,
			"error": True,
			"result": {"start": "{0}-{1}-{2}".format(start_year, start_month, start_date), 
				"end": "{0}-{1}-{2}".format(end_year, end_month, end_date)},
	})
	


@app.route('/get_word_cloud_with_dates', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*', headers='Content-Type')
def get_word_cloud_with_dates():
	__format = '%Y-%m-%d'
	eatery_id = request.form["eatery_id"]
	category = request.form["category"].split("__")[1].lower()
	start_epoch = time.mktime(time.strptime(request.form["start_date"], __format))
	end_epoch = time.mktime(time.strptime(request.form["end_date"], __format))


	print category, eatery_id, request.form["start_date"], request.form["end_date"], start_epoch, end_epoch
	
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

	return jsonify({"success": True,
			"error": True,
			"result": result
	})

@app.route('/get_word_cloud', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*', headers='Content-Type')
def get_word_cloud():
	__format = '%Y-%m-%d'
	eatery_id = request.form["eatery_id"]
	category = request.form["category"].split("__")[1].lower()
	start_epoch = time.mktime(time.strptime(request.form["start_date"], __format))
	end_epoch = time.mktime(time.strptime(request.form["end_date"], __format))


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



	print Counter(noun_phrases_list)
	result = list()
	for key, value in Counter(noun_phrases_list).iteritems():
		result.append({"name": key[0], "polarity": key[1], "frequency": value}) 
	
	print result
	return jsonify({"success": True,
			"error": True,
			"result": result,
	})

@app.route('/get_valid_files_count', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*', headers='Content-Type')
def get_valid_files_count():
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
	return jsonify({"success": True,
			"error": True,
			"result": result,
	})






class cd:
        """Context manager for changing the current working directory"""
        def __init__(self, newPath):
                self.newPath = newPath

        def __enter__(self):
                self.savedPath = os.getcwd()
                os.chdir(self.newPath)

        def __exit__(self, etype, value, traceback):
                os.chdir(self.savedPath)
		

#api.add_resource(ProcessText , '/v1/process_text')



if __name__ == '__main__':
    app.run(port=8000, debug=True)

