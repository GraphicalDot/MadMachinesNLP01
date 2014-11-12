#!/usr/bin/env python
#-*- coding: utf-8 -*-
import sys
import os
import time
import inspect
import itertools
import numpy as np
from sklearn.externals import joblib





#Changing path to the main directory where all the modules are lying
directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(directory))
from MainAlgorithms import InMemoryMainClassifier, timeit, cd, path_parent_dir, path_trainers_file, path_in_memory_classifiers




class SentimentClassifier(InMemoryMainClassifier):
	def __init__(self):
		super(InMemoryMainClassifier, self).__init__()
		self.tag_list = ["super-positive", "positive", "negative", "super-negative", "null"] 
			

	@timeit
	def loading_all_classifiers_in_memory(self):
		
		cls_methods_for_algortihms = [method[0] for method in inspect.getmembers(self, predicate=inspect.ismethod) if method[0] not in ['loading_all_classifiers_in_memory', "__init__"]]

		print cls_methods_for_algortihms
		with cd(path_in_memory_classifiers):
			for class_method in cls_methods_for_algortihms:
				instance = InMemoryMainClassifier()
				classifier = eval("{0}.{1}()".format("instance", class_method))
				joblib_name_for_classifier = "{0}_sentiment.lib".format(class_method)
				print classifier, joblib_name_for_classifier
	
				joblib.dump(classifier, joblib_name_for_classifier) 


