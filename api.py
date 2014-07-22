#!/usr/bin/env python
#-*- coding: utf-8 -*-


from flask import Flask
from flask import request, jsonify
from flask.ext import restful
from flask.ext.restful import reqparse
import hashlib
import subprocess
import shutil
import json
import os
from bson.json_util import dumps
from Text_Processing import ProcessingWithBlob, PosTags, Classifier




app = Flask(__name__)
api = restful.Api(app)
# '/register_user' arguments parser
text_parser = reqparse.RequestParser()

text_parser.add_argument('text', type=str, required=True, location='form')

class ProcessText(restful.Resource):

    def post(self):
		"""
		This returns 


		"""
		args = text_parser.parse_args()
		text = args["text"]
		print text
		if not bool(text):
			return {
				"error": True,
				"success": False,
				"error_code": 101,
				"messege": "Text field cannot be left empty"
				}


		text_classfication = Classifier(text)	
		result = list() 
		for chunk in text_classfication.with_svm():
			element = dict()
			instance = ProcessingWithBlob(chunk[0])
			element["sentence"] = chunk[0]
			element["polarity"] = instance.sentiment_polarity()
			element["noun_phrases"] = list(instance.noun_phrase())
			element["tag"] = chunk[1]
			result.append(element)

		return {
				"result": result,
				"success": True,
				"error": False,
				"overall_sentiment": ProcessingWithBlob.new_blob_polarity(text)
				}


class cd:
        """Context manager for changing the current working directory"""
        def __init__(self, newPath):
                self.newPath = newPath

        def __enter__(self):
                self.savedPath = os.getcwd()
                os.chdir(self.newPath)

        def __exit__(self, etype, value, traceback):
                os.chdir(self.savedPath)
		

api.add_resource(ProcessText , '/v1/process_text')



if __name__ == '__main__':
    app.run(port=8000, debug=True)

