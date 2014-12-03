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
import multiprocessing 
from multiprocessing import Pool

def to_unicode_or_bust(obj, encoding='utf-8'):
	if isinstance(obj, basestring):
		if not isinstance(obj, unicode): 
			obj = unicode(obj, encoding)
	return obj                      


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

		self.csv_file = open("/home/k/c_p.csv", "wb")
		self.writer = csv.writer(self.csv_file, delimiter=',')
                
                for eatery_id in self.eateries_id():
                        __e = eatery.find_one({"eatery_id": eatery_id})
			self.writer.writerow([__e.get("eatery_name"), __e.get("area_or_city"), __e.get("eatery_address")])
                        self.writer.writerow("\n")


                        result = self.per_eatery(eatery_id)
                       
                        start_time = time.time()
                        #food_result = sorted(self.merging_similar_elements(result[0]), reverse=True, key=lambda x: x.get("frequency"))
                        food_result = sorted(result[0], reverse=True, key=lambda x: x.get("frequency"))
                        print "Total time taken %s"%(time.time() - start_time)
			for line in food_result:
				self.writer.writerow([line.get("name").encode("utf-8"), line.get("polarity"), line.get("frequency"), "food"])
                        self.writer.writerow("\n")
                        
                        start_time = time.time()
                        overall_result = sorted(result[1], reverse=True, key=lambda x: x.get("frequency"))
                        #overall_result = sorted(self.merging_similar_elements(result[1]), reverse=True, key=lambda x: x.get("frequency"))
                        print "Total time taken %s"%(time.time() - start_time)
                        for line in overall_result:
		            self.writer.writerow([line.get("name").encode("utf-8"), line.get("polarity"), line.get("frequency"), "overall"])
                        self.writer.writerow("\n")
                        
                        start_time = time.time()
                        null_result = sorted(result[2], reverse=True, key=lambda x: x.get("frequency"))
                        #null_result = sorted(self.merging_similar_elements(result[2]), reverse=True, key=lambda x: x.get("frequency"))
                        print "Total time taken %s"%(time.time() - start_time)
                        for line in null_result:
				self.writer.writerow([line.get("name").encode("utf-8"), line.get("polarity"), line.get("frequency"), "null"])
                        self.writer.writerow("\n")
                        
                        start_time = time.time()
                        cost_result = sorted(result[3], reverse=True, key=lambda x: x.get("frequency"))
                        #cost_result = sorted(self.merging_similar_elements(result[3]), reverse=True, key=lambda x: x.get("frequency"))
                        print "Total time taken %s"%(time.time() - start_time)
                        for line in cost_result:
				self.writer.writerow([line.get("name").encode("utf-8"), line.get("polarity"), line.get("frequency"), "cost"])
                        self.writer.writerow("\n")
                        
                        start_time = time.time()
                        ambience_result = sorted(result[4], reverse=True, key=lambda x: x.get("frequency"))
                        #ambience_result = sorted(self.merging_similar_elements(result[4]), reverse=True, key=lambda x: x.get("frequency"))
                        for line in ambience_result:
				self.writer.writerow([line.get("name").encode("utf-8"), line.get("polarity"), line.get("frequency"), "ambience"])
                        self.writer.writerow("\n")
                        
                        start_time = time.time()
                        service_result = sorted(result[5], reverse=True, key=lambda x: x.get("frequency"))
                        #service_result = sorted(self.merging_similar_elements(result[5]), reverse=True, key=lambda x: x.get("frequency"))
                        print "Total time taken %s"%(time.time() - start_time)
                        for line in service_result:
				self.writer.writerow([line.get("name").encode("utf-8"), line.get("polarity"), line.get("frequency"), "service"])
                        self.writer.writerow("\n")
                    

                        self.writer.writerow("\n")
                        self.writer.writerow("\n")
                        self.writer.writerow("\n")
                        print "%s eatery completed"%__e.get("eatery_name")
			
			
        
        def eateries_id(self):
                """
                This returns all the all the eateires corresponding to the sub area
                """
                
                __eateries = [post.get("eatery_id") for post in eatery.find() if post.get("eatery_sub_area") == self.area_name]
                return [_id for _id in __eateries if list(reviews.find({"eatery_id": _id}))]



        def per_eatery(self, eatery_id):
                noun_phrases_list = list()
	
	        review_result = reviews.find({"eatery_id" :eatery_id})
	
	        review_text = [to_unicode_or_bust(post.get("review_text")) for post in review_result]
	        _review_text = " .".join(review_text)

        	result = list() 

		
        	tokenized_sentences = self.sent_tokenizer.tokenize(to_unicode_or_bust(_review_text))

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
			noun_phrases_list.extend([(noun.lower(),  text[2], text[1]) for noun in self.np_instance.noun_phrase(to_unicode_or_bust(text[0]))])


		
		##Incresing and decrasing frequency of the noun phrases who are superpositive and supernegative and changing
		##their tags to positive and negative
		edited_result = list()
		for __noun_phrase_dict in noun_phrases_list:
			if __noun_phrase_dict[1] == "super-positive" or __noun_phrase_dict[1] == "super-negative":
				edited_result.append((__noun_phrase_dict[0], __noun_phrase_dict[1].split("-")[1],  __noun_phrase_dict[2]))
				#Added twice beacause super postive was given twice as weightage as positive and some goes for supernegative 
				#and negative
				edited_result.append((__noun_phrase_dict[0], __noun_phrase_dict[1].split("-")[1],  __noun_phrase_dict[2]))

			else:
				edited_result.append(__noun_phrase_dict)
    
		result = list()
                food_list, overall_list, null_list, service_list, cost_list, ambience_list =list(), list(), list(), list(), list(), list()
                food_result, overall_result, null_result, service_result, cost_result, ambience_result =list(), list(), list(), list(), list(), list()
                
                ##Seperating elements of different tag and appending them to their corresponding lists 
                [eval("%s_list"%element[2]).append(element) for element in edited_result]                

                """
                food_list = (u'sheesha', u'positive', u'food'), (u'sheesha', u'positive', u'food'), (u'good table', u'null', u'food'), 
                (u'barbecue sauce', u'negative', u'food'), ...]

                """
                


                                                                                                                                                                                                        
		for key, value in Counter(food_list).iteritems():
                        food_result.append({"name": key[0], "polarity": 1 if key[1] == 'positive' else 0 , "frequency": value, "tag": key[2]}) 
		
                for key, value in Counter(overall_list).iteritems():
                        overall_result.append({"name": key[0], "polarity": 1 if key[1] == 'positive' else 0 , "frequency": value, "tag": key[2]}) 
		
                for key, value in Counter(null_list).iteritems():
                        null_result.append({"name": key[0], "polarity": 1 if key[1] == 'positive' else 0 , "frequency": value, "tag": key[2]}) 
		
                for key, value in Counter(service_list).iteritems():
                        service_result.append({"name": key[0], "polarity": 1 if key[1] == 'positive' else 0 , "frequency": value, "tag": key[2]}) 
		
                for key, value in Counter(cost_list).iteritems():
                        cost_result.append({"name": key[0], "polarity": 1 if key[1] == 'positive' else 0 , "frequency": value, "tag": key[2]}) 
		
                for key, value in Counter(ambience_list).iteritems():
                        ambience_result.append({"name": key[0], "polarity": 1 if key[1] == 'positive' else 0 , "frequency": value, "tag": key[2]}) 
		


                return (iter(food_result), iter(overall_result), iter(null_result), iter(cost_result), iter(ambience_result), iter(service_result))

        def merging_similar_elements(self, not_original_list):
                """
                This function will calculate the minum distance between two noun phrase and if the distance is 
                less than 1 and more than .8, delete one of the element and add both their frequencies
                """

                original_list = [element for element in not_original_list]

                original_dict = {element.get("name"): {"frequency": element.get("frequency"), "polarity": element.get("polarity")} \
					for element in original_list}
		


			
                calc_simililarity = lambda __a, __b: difflib.SequenceMatcher(a=__a.get("name").lower(), b=__b.get("name").lower()).ratio() \
										if __a.get("name").lower() != __b.get("name").lower() else 0
			
			
                list_with_similarity_ratios = list()
                for test_element in original_list:
                        for another_element in copy.copy(original_list):
                                r = calc_simililarity(test_element, another_element)	
                                print "Calculating similarity between {0} and {1} with r={2}".format(test_element.get("name").encode("utf-8"), another_element.get("name").encode("utf-8"), r)
                                list_with_similarity_ratios.append(dict(test_element.items() + 
                                        {"similarity_with": another_element.get("name"), "ratio": r}.items()))

                #list_with_similarity_ratios = my_func(original_list)
		filtered_list = [element for element in list_with_similarity_ratios if element.get("ratio") <1 and element.get("ratio") > .8]



			
                for element in filtered_list:
                        try:
                                print element
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

		

class Consumer(multiprocessing.Process):
        def __init__(self, task_queue, result_queue):
                multiprocessing.Process.__init__(self)
                self.task_queue = task_queue
                self.result_queue = result_queue

        def run(self):
                proc_name = self.name
                while True:
                        next_task = self.task_queue.get()
                        if next_task is None:
                                # Poison pill means shutdown
                                print '%s: Exiting' % proc_name
                                self.task_queue.task_done()
                                break
                        #print '%s: %s' % (proc_name, next_task)
                        answer = next_task()
                        self.task_queue.task_done()
                        self.result_queue.put(answer)
                return


class Task(object):
        def __init__(self, a, b):
                self.__a = a
                self.__b = b
    
        def __call__(self):
                if self.__a.get("name").lower() != self.__b.get("name").lower():
                        r  = difflib.SequenceMatcher(a=self.__a.get("name").lower(), b=self.__b.get("name").lower()).ratio()
                else:
                        r = 0
                return dict(self.__a.items() + {"similarity_with": self.__b.get("name"), "ratio": r}.items())



        def __str__(self):
            return 'similarity between %s and %s'%(self.__a.get("name"), self.__b.get("name"))


def my_func(original_list):
        # Establish communication queues
        tasks = multiprocessing.JoinableQueue()
        results = multiprocessing.Queue()
        aresults = multiprocessing.Queue()
        a_list = list()
    
        # Start consumers
        num_consumers = multiprocessing.cpu_count()
        print 'Creating %d consumers' % num_consumers
        consumers = [Consumer(tasks, results) for i in xrange(num_consumers)]
        
        
        for w in consumers:
                w.start()
    
    
        for i in original_list:
                for j in original_list:
                        tasks.put(Task(i, j))
    
    
        for i in xrange(num_consumers):
                tasks.put(None)

        # Wait for all of the tasks to finish
        tasks.join()
    
        # Start printing results
        while not results.empty():
                result = results.get()
                #print 'Result:', result
                a_list.append(result)


        return a_list


if __name__ == '__main__':
        Writinghundereds()
