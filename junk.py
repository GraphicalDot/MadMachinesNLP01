#!/usr/bin/env python

import pymongo
import sys
import codecs
import csv
connection = pymongo.Connection()
db = connection.modified_canworks
eatery = db.eatery
reviews = db.review

import numpy
import random
import itertools
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
import copy
import re
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
from collections import Counter
from functools import wraps
import itertools
import random
from sklearn.externals import joblib
import multiprocessing as mp
from multiprocessing import Pool

def to_unicode_or_bust(obj, encoding='utf-8'):
	if isinstance(obj, basestring):
		if not isinstance(obj, unicode): 
			obj = unicode(obj, encoding)
	return obj                      



"""
def return_eateries_list():
	__a = list()
	for post in eatery.find():
		__a.append([post.get("eatery_id"), post.get("eatery_name"), post.get("area_or_city"), reviews.find({"eatery_id": post.get("eatery_id")}).count()])
	return sorted(__a, reverse=True, key=lambda x: x[3])



def reviews_list_every_eatery(__input_list, number_of_restaurants):
	__a = list()
	for eatery_object in __input_list[0: number_of_restaurants]:
		__reviews = list(reviews.find({"eatery_id": eatery_object[0]}))
		eatery_object.append(__reviews)
		__a.append(eatery_object)
	return __a


def editing_review_time(__input_list):
	__a = list()
	for eatery_object in __input_list:
		eatery_review_times = [post.get("review_time") for post in eatery_object[4]]
		__a.append([eatery_object[0], eatery_object[1], eatery_object[2], eatery_object[3], eatery_review_times])
	return __a


def manipulate_review_time(__input_list):
	__abc = list()
	for eatery_object in __input_list:
		new_list = sorted(eatery_object[4], reverse=True)
		__p = list()
		__p.append(list())
		__p[0].append(new_list[0])
		for element in new_list:
			if __p[-1][-1].split(" ")[0].split("-")[1] != element.split(" ")[0].split("-")[1]:
				__p.append(list())__p[-1].append(element)
			else:
				__p[-1].append(element)
		__abc.append([eatery_object[0], eatery_object[1], eatery_object[2], eatery_object[3], __p])
	return __abc

def final_output(__input_list):
	__abcd = list()
	for eatery_object in __input_list:
		__a = list()
		for element in eatery_object[4]:
			__str = element[0].split(" ")[0]
			__a.append([__str,  "{0}/{1}".format(__str.split("-")[1], __str.split("-")[0][2:]),  len(element)])
		__abcd.append([eatery_object[0], eatery_object[1], eatery_object[2], eatery_object[3], __a])
	return __abcd		


def new_file_for_tag_manipulation(file_name):

	tag_list = ["food", "service", "null", "overall", "ambience", "cost", "positive"]
	__food = __service = __overall = __ambience = __cost = __null = list()

	for element in tag_list:
		total_length = reviews.count()
		print "Writing {0} sentences".format(element)
		index = 0

		for post in reviews.find():
			if bool(post.get(element)):
		eval("__{0}".format(element)).extend([[to_unicode_or_bust(sentence), element, post.get("review_id")] for sentence in post.get(element)])
			index += 1

	csvfile = codecs.open(file_name, 'wb')
	writer = csv.writer(csvfile, delimiter=" ")

	for tag in tag_list:
		writer.writerow(" ")
		for __entry in eval("__{0}".format(tag)):
			try:
				writer.writerow(to_unicode_or_bust(__entry))
			except:
				print __entry

	csvfile.close()


def make_new_files_from_csvfile(csv_path, target_path):
	csvfile = codecs.open(csv_path, 'rb')
	reader = csv.reader(csvfile, delimiter=',')
	data, sorted_data = list(), list()
	for row in reader:
		data.append(row)

	for row in data:
		sorted_data.append([row[1], row[5]])

	tag_list = ["food", "service", "null", "overall", "ambience", "cost"]
	
	first_name = "manually_classified"

	for element in sorted_data:
		if element[1] in tag_list:
			with open("{0}/manually_classified_{1}.txt".format(target_path, element[1]), "a") as myfile:
				    myfile.write(element[0])
				    myfile.write("\n")


def writing_reviews_to_csv(target_path, count):
	path = "/home/k/Programs/Canworks/Canworks/trainers"
	reviews_list = list()
	for post in reviews.find({"is_classified": False}).limit(int(count)):
		reviews_list.append([post.get("review_text"), post.get("review_id")])


	
	sent_tokenizer = SentenceTokenization() 
	tag_list = ["food", "ambience", "cost", "service", "overall", "null"]

	sentiment_list = ["super-positive", "positive", "negative", "super-negative", "null"]
	
	data_lambda = lambda tag: [(sent, tag) for sent in sent_tokenizer.tokenize(open("{0}/manually_classified_{1}.txt".format(path, tag), "rb").read(),) 
			if sent != ""] 

	whole_tag_set = list(itertools.chain(*[data_lambda(tag) for tag in tag_list]))
	whole_sentiment_set = list(itertools.chain(*[data_lambda(tag) for tag in sentiment_list]))

	[random.shuffle(whole_tag_set) for i in range(0, 10)]
	[random.shuffle(whole_sentiment_set) for i in range(0, 10)]


	tag_data = numpy.array([element[0] for element in whole_tag_set])
	tag_target = numpy.array([element[1] for element in whole_tag_set])
	
	sentiment_data = numpy.array([element[0] for element in whole_sentiment_set])
	sentiment_target = numpy.array([element[1] for element in whole_sentiment_set])
	
	
	tag_classifier = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()),
			('clf', SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, n_iter=5)),])
	
	sentiment_classifier = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()),
			('clf', SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, n_iter=5)),])

	tag_classifier.fit(tag_data, tag_target)
	sentiment_classifier.fit(sentiment_data, sentiment_target)
	

	whole_text = list()

	for text in reviews_list:
		new_data = sent_tokenizer.tokenize(text[0])
		for element in new_data:
			whole_text.append([element, text[1]])
	


	predicted_tags = tag_classifier.predict([element[0] for element in whole_text])
	predicted_sentiment = sentiment_classifier.predict([element[0] for element in whole_text])
	
	
	result_for_tags = [[element[0][1], element[0][0].encode("utf-8"), element[1]] for element in zip(whole_text, predicted_tags)]
	result_for_sentiment = [[element[0][1], element[0][0].encode("utf-8"), element[1]] for element in zip(whole_text, predicted_sentiment)]
	
	reviews_tags_csvfile = codecs.open("{0}/reviews_tags.csv".format(target_path), 'wb')
	reviews_sentiment_csvfile = codecs.open("{0}/reviews_sentiment.csv".format(target_path), 'wb')
	
	
	tag_writer = csv.writer(reviews_tags_csvfile, delimiter=",")
	sentiment_writer = csv.writer(reviews_sentiment_csvfile, delimiter=",")
iiw

	for __a in result_for_tags:
		tag_writer.writerow(__a)
	
	for __a in result_for_sentiment:
		sentiment_writer.writerow(__a)
		
	

	reviews_tags_csvfile.close()
	reviews_sentiment_csvfile.close()

	
       
"""

class Writinghundereds:

        def __init__(self, find_similarity=True):
                """
                This is the class used to write top 100 noun phrases to a csv file corresponding to a particular 
                eatery.

                find_similarity = True, 
                    which means club all the nounn phrases together after calculating their similarity distane 
                    which should be more than .8 and less thn 1.

                """
                areas = list(set([post.get("eatery_sub_area") for post in eatery.find()]))
                areas_dict = dict(zip(range(len(areas)), areas))
                for element in areas_dict.iteritems():
                        print element

                selected_area = raw_input("Enter th enumber of the area you want to get printed to csv ..." )

                print selected_area
                try:
                    area = areas_dict[int(selected_area)]
                except Exception:
                    raise StandardError("you didnt choose valid area, Go fuck yourself")


                self.area_name = area
                self.similarity = find_similarity
	
                with cd(path_in_memory_classifiers):
                    self.tag_classifier = joblib.load('svm_classifier_tag.lib')
                    self.sentiment_classifier = joblib.load('svm_classifier_sentiment.lib')
		
		self.sent_tokenizer = SentenceTokenizationOnRegexOnInterjections()
		self.np_instance = ProcessingWithBlobInMemory()
       


                for eatery_id in self.eateries_id()[5:6]:
                        result = self.per_review(eatery_id)
                        print result
                        print len(result)
                        final_result = sorted(self.merging_similar_elements(result), reverse=True, key=lambda x: x.get("frequency"))
                        print final_result
                    


		"""
		with open("/home/k/word_cloud.csv", "wb") as csv_file:
			writer = csv.writer(csv_file, delimiter=',')
			for line in result:
				writer.writerow([line.get("name").encode("utf-8"), line.get("polarity"), line.get("frequency")])
		"""
        def eateries_id(self):
                """
                This returns all the all the eateires corresponding to the sub area
                """
                
                return  [post.get("eatery_id") for post in eatery.find() if post.get("eatery_sub_area") == self.area_name]



        def per_review(self, eatery_id):
                noun_phrases_list = list()
	
	        review_result = reviews.find({"eatery_id" :eatery_id})
	
	        review_text = [to_unicode_or_bust(post.get("review_text")) for post in review_result]
	        review_text = " .".join(review_text)

        	result = list() 

		
        	tokenized_sentences = self.sent_tokenizer.tokenize(to_unicode_or_bust(review_text))

        	##with svm returns a list in the following form
        	##[(sentence, tag), (sentence, tag), ................]
        	#for chunk in text_classfication.with_svm():
		
        	#Getting Sentiment analysis
        	__predicted_tags = self.tag_classifier.predict(tokenized_sentences)
        	__predicted_sentiment = self.sentiment_classifier.predict(tokenized_sentences)


                index = 0

                #classified_sentences = [('but in the afternoon , it is usually unoccupied .', 'null'),
                #(u'the food is fine , hard - to - eat in some cases .', 'food')]

                #__predicted_sentiment = ["null", "negative" ]

		
		__k = lambda text: noun_phrases_list.extend([(noun.lower(),  text[2]) for noun in self.np_instance.noun_phrase(to_unicode_or_bust(text[0]))])	
		
		for text in zip(tokenized_sentences, __predicted_tags, __predicted_sentiment):
			noun_phrases_list.extend([(noun.lower(),  text[2]) for noun in self.np_instance.noun_phrase(to_unicode_or_bust(text[0]))])


		
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
		


		sorted_result = sorted(result, reverse=True, key=lambda x: x.get("frequency"))
                return sorted_result

        def merging_similar_elements(self, original_list):
                """
                This function will calculate the minum distance between two noun phrase and if the distance is 
                less than 1 and more than .8, delete one of the element and add both their frequencies
                """

                original_dict = {element.get("name"): {"frequency": element.get("frequency"), "polarity": element.get("polarity")} \
					for element in original_list}
			
			
                calc_simililarity = lambda __a, __b: difflib.SequenceMatcher(a=__a.get("name").lower(), b=__b.get("name").lower()).ratio() \
										if __a.get("name").lower() != __b.get("name").lower() else 0
			
			
                list_with_similarity_ratios = list()


                """
                for test_element in original_list:
                        for another_element in copy.copy(original_list):
                                r = calc_simililarity(test_element, another_element)	
                                list_with_similarity_ratios.append(dict(test_element.items() + 
                                        {"similarity_with": another_element.get("name"), "ratio": r}.items()))
                """

                

                def custom_func(test_element):
                        for another_element in copy.copy(original_list):
                                r = calc_simililarity(test_element, another_element)	
                                list_with_similarity_ratios.append(dict(test_element.items() + 
                                        {"similarity_with": another_element.get("name"), "ratio": r}.items()))


                with Pool(processes=4) as pool:
                        result = pool.apply_async(custom_func, original_list)
                        print result.get() 
                

		filtered_list = [element for element in list_with_similarity_ratios if element.get("ratio") <1 and element.get("ratio") > .8]



			
                for element in filtered_list:
                        try:
                                frequency = original_dict[element.get("name")]["frequency"] + \
							original_dict[element.get("similarity_with")]["frequency"]
							
				del original_dict[element.get("similarity_with")]
				original_dict[element.get("name")]["frequency"] = frequency
					
			except Exception as e:
				pass

			"""0
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

		










if __name__ == "__main__":
        Writinghundereds()

