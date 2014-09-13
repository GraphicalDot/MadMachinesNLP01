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
from Text_Processing import ProcessingWithBlob, PosTags, Classifier
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


		text_classfication = Classifier(text.decode("utf-8"))	
		noun_phrase = list()
		result = list() 

		polarity=lambda x: "postive" if float(x)>= 0 else "negative"

		for chunk in text_classfication.with_svm():
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
				"overall_sentiment": '%.2f'%ProcessingWithBlob.new_blob_polarity(text),
				"noun_phrase": noun_phrase,
				})

@app.route('/update_model', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*', headers='Content-Type')
def update_model():
	text = request.form["text"]
	tag = request.form["tag"]

	path = (os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/trainers/valid_%s.txt"%tag))
	
	print "Ihis is the path that is being opened%s"%path

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
		return 
	
	result = reviews.find_one({'review_id': id}, fields={"_id": False})
	return jsonify({"success": True,
				"error": False,
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

