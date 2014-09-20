#!/usr/bin/env python
#-*- coding: utf-8 -*-


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



connection = pymongo.Connection()
db = connection.modified_canworks
eateries = db.eatery
reviews = db.review

app = Flask(__name__)



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


		text_classfication = Classifier(text.encode("utf-8"))	
		noun_phrase = list()
		result = list() 

		polarity=lambda x: "postive" if float(x)>= 0 else "negative"


		##with svm returns a list in the following form
		##[(sentence, tag), (sentence, tag), ................]
		for chunk in text_classfication.with_svm():
			print chunk
			element = dict()
			instance = ProcessingWithBlob(chunk[0])
			element["sentence"] = chunk[0]
			element["polarity"] = {"name": polarity('%.1f'%instance.sentiment_polarity()), "value": '%.1f'%instance.sentiment_polarity()}
			element["noun_phrases"] = list(instance.noun_phrase())
			element["tag"] = chunk[1]
			result.append(element)
			noun_phrase.extend(list(instance.noun_phrase()))

		return jsonify({
				"result": result,
				"success": True,
				"error": False,
				"overall_sentiment": '%.2f'%ProcessingWithBlob.new_blob_polarity(text.encode("utf-8")),
				"noun_phrase": noun_phrase,
				})

@app.route('/update_model', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*', headers='Content-Type')
def update_model():
	text = request.form["text"]
	tag = request.form["tag"]

	path = (os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/trainers/valid_%s.txt"%tag))
	
	if not os.path.exists(path):
		return jsonify({"success": False,
				"error": True,
				"messege": "The tag you mentioned doesnt exist in the learning model",
				"error_code": 201,
			})



	with open(path, "a") as myfile:
		myfile.write(text)
		myfile.write("\n")

	return jsonify({"success":  True,
		"error": False,
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
	text = request.form["text"]
	repeated = request.form["is_repeated"]
	review_id = request.form["review_id"]

	if int(repeated) != 2:
		return jsonify({"success": False,
				"error": True,
				"messege": "Only repeated customer sentences can be tagged, 'void' is an invalid tag",
				"error_code": 206,
			})


	path = (os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/trainers/valid_%s.txt"%'repeated_customer'))

	if not os.path.exists(path):
		return jsonify({"success": False,
				"error": True,
				"messege": "Some error occurred",
				"error_code": 205,
			})



	with open(path, "a") as myfile:
		myfile.write(text)
		myfile.write("\n")



	reviews.update({"review_id": review_id}, {"$push": {"repeated_customers": text}})
	return jsonify({"success":  True,
		"error": False,
		})



@app.route('/eateries_list', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*', headers='Content-Type')
def eateries_list():
	result = list(eateries.find(fields= {"eatery_id": True, "_id": False, "eatery_name": True}))

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
	text = request.form["text"]
	grams = request.form["grams"]
	if not text:
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
				"result": nltk_ngrams(text, grams),
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

