#!/usr/bin/env python
#-*- coding: utf-8 -*-

import nltk
import numpy
import random
import sys
import os
import time
from optparse import OptionParser
import inspect
import itertools
import numpy as np

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline

from sklearn.feature_selection import SelectKBest, chi2
from sklearn.linear_model import RidgeClassifier
from sklearn.svm import LinearSVC
from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import Perceptron
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.naive_bayes import BernoulliNB, MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neighbors import NearestCentroid
from sklearn.externals import joblib

from paths import path_in_memory_classifiers, path_trainers_file, path_parent_dir



#Changing path to the main directory where all the modules are lying
sys.path.append(os.path.join(path_parent_dir))
from Sentence_Tokenization import SentenceTokenizationOnRegexOnInterjections, CopiedSentenceTokenizer
from Algortihms import Sklearn_RandomForest
from Algortihms import SVMWithGridSearch
from colored_print import bcolors



def timeit(method):
        def timed(*args, **kw):
                ts = time.time()
                result = method(*args, **kw)
                te = time.time()

                print '%s%r (%r, %r) %2.2f sec %s'%(bcolors.OKGREEN, method.__name__, args, kw, te-ts, bcolors.RESET)
                return result
        return timed



class InMemoryMainClassifier(object):
	def __init__(self, tokenizer=None):
		"""
		BY Default 
			Sentence tokenizer present in the nltk library is used to tokenize the sentences

		"""
		
		start = time.time()
		self.tokenizer = tokenizer
		
		self.tag_list = ["food", "ambience", "cost", "service", "overall", "null"]
			
		
		
		if not self.tokenizer:
			self.sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
			self.data_lambda = lambda tag: np.array([(sent, tag) for sent in 
					self.sent_tokenizer.tokenize(open("{0}/manually_classified_{1}.txt".format(path_trainers_file, tag), 
						"rb").read(), realign_boundaries=True) if sent != ""])
			
		if self.tokenizer == "text-sentence":
			self.sent_tokenizer = SentenceTokenization()
			self.data_lambda = lambda tag: np.array([(sent, tag) for sent in 
					self.sent_tokenizer.tokenize(open("{0}/manually_classified_{1}.txt".format(path_trainers_file, tag), "rb").read(),) 
					if sent != ""])
			
		
		#joining list of lists returned by self.data, Every tag will have their own list, Itertools will join these lists into a single list	
		self.whole_set = list(itertools.chain(*[self.data_lambda(tag) for tag in self.tag_list]))
		
		#Shuffling the list formed ten times to get better results.
		[random.shuffle(self.whole_set) for i in range(0, 10)]
		
	
		self.training_sentences, self.training_target_tags = zip(*self.whole_set)

		print "{0} Total time taken to intialize class Main_Classification FUNCTION--<{1}{2}".format(bcolors.OKGREEN, time.time()-start, bcolors.RESET) 	


	@timeit
	def loading_all_classifiers_in_memory(self):
		instance = InMemoryMainClassifier()
		
		cls_methods_for_algortihms = [method[0] for method in inspect.getmembers(self, predicate=inspect.ismethod) if method[0] not in ['loading_all_classifiers_in_memory', "__init__"]]

		print cls_methods_for_algortihms
		with cd(path_in_memory_classifiers):
			for class_method in cls_methods_for_algortihms:
				instance = InMemoryMainClassifier()
				classifier = eval("{0}.{1}()".format("instance", class_method))
				joblib_name_for_classifier = "{0}_tag.lib".format(class_method)
				print classifier, joblib_name_for_classifier
	
				joblib.dump(classifier, joblib_name_for_classifier) 


	@timeit
	def multinomial_nb_classifier(self):
		"""
		This method returns a claqssfier trained with multinomial naive bayes using cost, services and ambience as three categories
		fit_prior : boolean
			Whether to learn class prior probabilities or not. If false, a uniform prior will be used.
		class_prior : array-like, size (n_classes,)
			Prior probabilities of the classes. If specified the priors are not adjusted according to the data.
		"""
		print "\n Running {0} \n".format(inspect.currentframe())
		
		classifier = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()), 
			('clf', MultinomialNB(class_prior=None, fit_prior=False)),])
		
		classifier.fit(self.training_sentences, self.training_target_tags)
		return classifier


	@timeit
	def svm_classifier(self):
		classifier = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()), 
			('clf', SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, n_iter=5)),])

		classifier.fit(self.training_sentences, self.training_target_tags)
		return classifier


	@timeit
	def logistic_regression_classifier(self):
		classifier = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()), 
			('clf', SGDClassifier(loss='log', penalty='l2', alpha=1e-3, n_iter=5)),])

		classifier.fit(self.training_sentences, self.training_target_tags)
		return classifier


	@timeit
	def perceptron_classifier(self):
		classifier = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()), 
			('clf', Perceptron(n_iter=50)),])
		
		classifier.fit(self.training_sentences, self.training_target_tags)
		return classifier



	@timeit
	def ridge_regression_classifier(self):
		classifier = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()), 
			('clf', RidgeClassifier(tol=1e-2, solver="lsqr")),])

		
		classifier.fit(self.training_sentences, self.training_target_tags)
		return classifier


	@timeit
	def passive_agressive_classifier(self):
		classifier = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()), 
			('clf', PassiveAggressiveClassifier(n_iter=50)),])

		classifier.fit(self.training_sentences, self.training_target_tags)
		return classifier


	"""
	@timeit
	def random_forests_classifier(self):

		print "\n Running {0} \n".format(inspect.stack()[0][3])
		instance = Sklearn_RandomForest(self.training_sentences, self.training_target_tags)
		classifier = instance.classifier()
		

		return classifier
	"""
	
	@timeit
	def svm_grid_search_classifier(self):
		print "\n Running {0} \n".format(inspect.stack()[0][3])
		instance = SVMWithGridSearch(self.training_sentences, self.training_target_tags)
		classifier = instance.classifier()
		return classifier




class cd:
	def __init__(self, newPath):
		self.newPath = newPath

	def __enter__(self):
		self.savedPath = os.getcwd()
		os.chdir(self.newPath)
		
	def __exit__(self, etype, value, traceback):
		os.chdir(self.savedPath)
