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
import cStringIO
import base64




app = Flask(__name__)
api = restful.Api(app)
# '/register_user' arguments parser
reguser_parser = reqparse.RequestParser()

reguser_parser.add_argument('mac_id', type=str, required=True, location='form')
reguser_parser.add_argument('first_name', type=str, required=True, location='form')
reguser_parser.add_argument('second_name', type=str, required=False, location='form')
reguser_parser.add_argument('email_id', type=str, required=True, location='form')
reguser_parser.add_argument('platform', type=str, required=True, location='form')
reguser_parser.add_argument('modules', type=str, required=True, location='form')
reguser_parser.add_argument('country', type=str, required=True, location='form')
reguser_parser.add_argument('payment_receipt_image', type=str, required=True, location='form')



#zip_parser.add_argument('check_module', type=str, required=False, location='args')




class NounPhrases(restful.Resource):

    def post(self):
		"""
		This returns 


		"""
		args = reguser_parser.parse_args()
		users = collection("users")
		
		
		if users.find_one({"email_id": args["email_id"], "mac_id": args["mac_id"], "modules": args["modules"]}):
			return {
				"error": False,
				"success": True,
				"messege": "Registration has already been done"
				}
		
		try:	
			if args["email_id"] not in connection.list_verified_email_addresses()['ListVerifiedEmailAddressesResponse']['ListVerifiedEmailAddressesResult']['VerifiedEmailAddresses']:
				connection.verify_email_address(args["email_id"])
		
		except boto.exception.BotoServerError:
			return {
				"error": False,
				"success": True,
				"messege": "The email provided is not valid, Please provide a valid email address"
				}


		string = args.get("email_id").lower() + args.get("mac_id").lower() + args.get("first_name").lower() + args.get("modules")
		hash = hashlib.md5(string).hexdigest()
		key = hash[-10:]
		args["hash"] = hash
		args["key"] = key
		args["approved"] = False
		args["key_email_sent"] = False	
		
		if not users.find_one({"email_id": args["email_id"], "mac_id": args["mac_id"], "modules": args["modules"]}):
			try:
				image_output = cStringIO.StringIO()
				image_output.write(base64.decodestring(args["payment_receipt_image"]))
				image_output.seek(0)	
				im = Image.open(image_output)
				payment_receipt_path = "%s/%s.%s"%(IMAGE_PATH, key, im.format)
				im.save(payment_receipt_path)
			except IOError:
				return {
					"error": False,
					"success": True,
					"messege": "The image uploaded is not a valid image file, please upload correct image file",
					}


			args["payment_receipt_path"]  = ("%s/")%URL + "/".join(payment_receipt_path.split("/")[-2:])
			#args["payment_receipt_path"] = payment_receipt_path
			users.insert(args, safe=True)
		
			#sending an email for verification
			
			##TODO: send an email through ses
			return {
				"error": False,
				"success": True,
				"messege": "Registration has been completed, A mail has been sent to the email you mentioned and your key is %s"%key,}





class cd:
        """Context manager for changing the current working directory"""
        def __init__(self, newPath):
                self.newPath = newPath

        def __enter__(self):
                self.savedPath = os.getcwd()
                os.chdir(self.newPath)

        def __exit__(self, etype, value, traceback):
                os.chdir(self.savedPath)
		

api.add_resource(NounPhrases '/v1/noun_phrases')



if __name__ == '__main__':
    app.run(port=8000, debug=True)

