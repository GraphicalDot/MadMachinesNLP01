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
from Sentence_Tokenization_Classes import CopiedSentenceTokenizer
from Sentence_Tokenization_Classes import SentenceTokenization

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


from Algortihms import Sklearn_RandomForest
from Algortihms import SVMWithGridSearch
from colored_print import bcolors

directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(directory + "/trainers")

path_for_inmemory_classifiers = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/InMemoryClassifiers")


def timeit(method):
	def timed(*args, **kw):
		ts = time.time()
		result = method(*args, **kw)
		te = time.time()
		
		print '%s%r (%r, %r) %2.2f sec %s'%(bcolors.OKGREEN, method.__name__, args, kw, te-ts, bcolors.RESET)
		return result
	return timed




def get_all_algorithms_result(text="If only name of the algorithms are required", sentences_with_classification=True, if_names=False):
	"""
	This method will compare and delivers the accuracy of every algorithm computed in every class method which
	starts with with_
	To add any new algorithm just add that algortihm name starting with with__
	Args:
		sentences_with_classification: a list of dictionaries with sentence and its classfication
	"""
	
	print "entered into get all"
	results = list()
	

	tokenizer = SentenceTokenization()
	new_data = tokenizer.tokenize(text)
	
	classifier_cls = InMemoryMainClassifier()
	
	cls_methods_for_algortihms = [method[0] for method in inspect.getmembers(classifier_cls, predicate=inspect.ismethod) if method[0] not in ['loading_all_classifiers_in_memory', "__init__"]]
	
	if if_names:
		result = [cls_method for cls_method in cls_methods_for_algortihms]
		return result
		
		
	target = [element[1] for element in sentences_with_classification]


	for cls_method in cls_methods_for_algortihms:
		classified_sentences = eval("{0}.{1}()".format("classifier_cls", cls_method))
		predicted = [element[1] for element in classified_sentences]

		correct_classification = float(len([element for element in zip(predicted, target) if element[0] == element[1]]))

		print "{0} gives -- {1}".format(cls_method.replace("with_", ""), correct_classification/len(predicted))
		results.append({"algorithm_name": " ".join(cls_method.replace("with_", "").split("_")), 
				"accuracy": "{0:.2f}".format(correct_classification/len(predicted))})

	return results


class InMemoryMainClassifier:
	def __init__(self, tokenizer=None):
		"""
		Args:
			text: The text which needs to be classfied,
			tokenizer: This is the sentence tokenizer param which will be used to break the above text into sentences.
				The default value is None, For this default value the dafault sentence tokenizer of the nltk library will
				be used to tokenizze text into sentences,
				The other value could be tokenizer="text-sentence"
				Which then tokenize the text into sentences based on the tokenizer made in Sentence_Tokenization_Classes


		Class-Variables:
			whole_set: 
				returns a list of tuples in the form
				[(u'top floor makes it more glamours then it could be .', 'super-positive'),
				(u'ever since the first time i went there , Tropical lounge has become my favorite .', 'super-positive'),
				(u'there were a good number of free tables , and to this day i wonder why he lied to us .', 'negative'), .............]
			data: 
				List of sentences from the whole set
			
			target:
				list of corresponding tag for the sentences present in data
		"""


		start = time.time()
		self.tokenizer = tokenizer
		
		self.tag_list = ["food", "ambience", "cost", "service", "overall", "null"]
			
		
		
		if not self.tokenizer:
			self.sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
			self.data_lambda = lambda tag: np.array([(sent, tag) for sent in 
					self.sent_tokenizer.tokenize(open("{0}/manually_classified_{1}.txt".format(path, tag), 
						"rb").read(), realign_boundaries=True) if sent != ""])
			
		if self.tokenizer == "text-sentence":
			self.sent_tokenizer = SentenceTokenization()
			self.data_lambda = lambda tag: np.array([(sent, tag) for sent in 
					self.sent_tokenizer.tokenize(open("{0}/manually_classified_{1}.txt".format(path, tag), "rb").read(),) 
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
		

		#cls_methods_for_algortihms = [method.replace("_InMemoryMainClassifier", "") for method in dir(self) if method.startswith("_InMemoryMainClassifier__")]

		cls_methods_for_algortihms = [method[0] for method in inspect.getmembers(self, predicate=inspect.ismethod) if method[0] not in ['loading_all_classifiers_in_memory', "__init__"]]

		print cls_methods_for_algortihms
		with cd(path_for_inmemory_classifiers):
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

		data = numpy.array([element[0] for element in self.whole_set])
		target = numpy.array([element[1] for element in self.whole_set])
		
		classifier.fit(self.training_sentences, self.training_target_tags)
		return classifier


	@timeit
	def logistic_regression_classifier(self):
		classifier = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()), 
			('clf', SGDClassifier(loss='log', penalty='l2', alpha=1e-3, n_iter=5)),])

		data = numpy.array([element[0] for element in self.whole_set])
		target = numpy.array([element[1] for element in self.whole_set])
		
		classifier.fit(self.training_sentences, self.training_target_tags)
		return classifier


	@timeit
	def perceptron_classifier(self):
		classifier = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()), 
			('clf', Perceptron(n_iter=50)),])

		data = numpy.array([element[0] for element in self.whole_set])
		target = numpy.array([element[1] for element in self.whole_set])
		
		classifier.fit(self.training_sentences, self.training_target_tags)
		return classifier



	@timeit
	def ridge_regression_classifier(self):
		classifier = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()), 
			('clf', RidgeClassifier(tol=1e-2, solver="lsqr")),])

		data = numpy.array([element[0] for element in self.whole_set])
		target = numpy.array([element[1] for element in self.whole_set])
		
		classifier.fit(self.training_sentences, self.training_target_tags)
		return classifier


	@timeit
	def passive_agressive_classifier(self):
		classifier = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()), 
			('clf', PassiveAggressiveClassifier(n_iter=50)),])

		data = numpy.array([element[0] for element in self.whole_set])
		target = numpy.array([element[1] for element in self.whole_set])
		
		classifier.fit(self.training_sentences, self.training_target_tags)
		return classifier


	@timeit
	def random_forests_classifier(self):

		print "\n Running {0} \n".format(inspect.stack()[0][3])
		data = numpy.array([element[0] for element in self.whole_set])
		target = numpy.array([element[1] for element in self.whole_set])
		instance = Sklearn_RandomForest(self.training_sentences, self.training_target_tags)
		classifier = instance.classifier()
		

		return classifier

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
