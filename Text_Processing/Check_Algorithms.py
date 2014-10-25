#!/usr/bin/env python
#-*- coding: utf-8 -*-

import random
import pymongo
import itertools
from For_Testing import get_all_algorithms_result
class CheckAlgorithmsAccuracy:

	def __init__(self):
		"""
		This is the class which will be used to check the accuracy of the algorithms,
		All the test data will be pulled from the reviews which have the flag is_classified True in the database,
		Which means that these reviews has already been classified by the admins.

		So all the sentences are pulled like this..
		So if a review has a some sentences under food, These are the sentences which had been classified wrongly by the algorithms 
		and should be under food category if properly classified
		"""

		self.test_data = self.__build_test_data
		self.tag_list = ["food", "service", "ambience", "cost", "null", "overall"]


	def __build_test_data(self):
		"""
		This is the method which actully build the test data from the mongodb
		"""

		classified_reviews = [post for post in reviews.find() if post.get("is_classified")]
		test_data = lambda tag: [(sentence, tag) for sentence in 
				list(itertools.chain(*[post.get(tag) for post in classified_reviews if post.get(tag)]))]

		
		whole_set = list(itertools.chain(*[test_data(tag) for tag in self.tag_list]))
		
		#shuffling the whole set 10 times to get more clear pisture while testing with algorithms
		[random.shuffle(whole_set) for i in range(10)]
		
		return whole_set


	def puke_results(self):
		 classifier_cls = ForTestingClassifier(text)
		 cls_methods_for_algortihms = [method[0] for method in inspect.getmembers(classifier_cls, predicate=inspect.ismethod) 
				 if method[0].startswith("with")]                                                                                                                  





