#!/usr/bin/env python
#-*- coding: utf-8 -*-

import nltk
import numpy
import random
import sys
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from CustomSentenceTokenizer import SentenceTokenizer 
from  trained_punkt_sentences_tokenizer import 	SentenceTokenization

from sklearn.feature_selection import SelectKBest, chi2
from sklearn.linear_model import RidgeClassifier
from sklearn.svm import LinearSVC
from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import Perceptron
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.naive_bayes import BernoulliNB, MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neighbors import NearestCentroid

from Algortihms import Sklearn_RandomForest

directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(directory + "/trainers")


class ForTestingClassifier:
	def __init__(self, text, tokenizer=None):
		self.text = text
		self.tokenizer = tokenizer
		if not self.tokenizer:
			self.sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
		
			self.ambience_data = self.sent_tokenizer.tokenize(open("{0}/valid_{1}.txt".format(path, "ambience"), "rb").read(), realign_boundaries=True)
			self.services_data = self.sent_tokenizer.tokenize(open("{0}/valid_{1}.txt".format(path, "service"), "rb").read(), realign_boundaries=True)
			self.costing_data = self.sent_tokenizer.tokenize(open("{0}/valid_{1}.txt".format(path, "cost"), "rb").read(), realign_boundaries=True)
			self.food_data = self.sent_tokenizer.tokenize(open("{0}/valid_{1}.txt".format(path, "food"), "rb").read(), realign_boundaries=True)
			self.null_data = self.sent_tokenizer.tokenize(open("{0}/valid_{1}.txt".format(path, "null"), "rb").read(), realign_boundaries=True)
			self.overall_data = self.sent_tokenizer.tokenize(open("{0}/valid_{1}.txt".format(path, "overall"), "rb").read(), realign_boundaries=True)
		if self.tokenizer == "text-sentence":
			self.sent_tokenizer = SentenceTokenization()
			self.ambience_data = self.sent_tokenizer.tokenize(open("{0}/valid_{1}.txt".format(path, "ambience"), "rb").read())
			self.services_data = self.sent_tokenizer.tokenize(open("{0}/valid_{1}.txt".format(path, "service"), "rb").read())
			self.costing_data = self.sent_tokenizer.tokenize(open("{0}/valid_{1}.txt".format(path, "cost"), "rb").read())
			self.food_data = self.sent_tokenizer.tokenize(open("{0}/valid_{1}.txt".format(path, "food"), "rb").read())
			self.null_data = self.sent_tokenizer.tokenize(open("{0}/valid_{1}.txt".format(path, "null"), "rb").read())
			self.overall_data = self.sent_tokenizer.tokenize(open("{0}/valid_{1}.txt".format(path, "overall"), "rb").read())
		
		#self.ambience_documents = [(nltk.wordpunct_tokenize(sent), "ambience") for sent in self.ambience_data if sent != ""]
		self.ambience_documents = [(sent, "ambience") for sent in self.ambience_data if sent != ""]
		self.services_documents = [(sent, "service") for sent in self.services_data if sent != ""]
		self.costing_documents = [(sent, "cost") for sent in self.costing_data if sent != ""]
		self.food_documents = [(sent, "food") for sent in self.food_data if sent != ""]
		self.null_documents = [(sent, "null") for sent in self.null_data if sent != ""]
		self.overall_documents = [(sent, "overall") for sent in self.overall_data if sent != ""]
		self.whole_set = self.ambience_documents + self.services_documents + self.costing_documents + self.food_documents + self.null_documents + self.overall_documents
		random.shuffle(self.whole_set)

	def document_features(document):
		document_words = set(document) [3]
		features = {}
		for word in word_features:
			features['contains(%s)' % word] = (word in document_words)
		return features

	def naive_bayes_classifier(self):
		pass

	def multinomial_nb_classifier(self):
		"""
		This method returns a claqssfier trained with multinomial naive bayes using cost, services and ambience as three categories
		fit_prior : boolean
			Whether to learn class prior probabilities or not. If false, a uniform prior will be used.
		class_prior : array-like, size (n_classes,)
			Prior probabilities of the classes. If specified the priors are not adjusted according to the data.
		"""
		classifier = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()), 
			('clf', MultinomialNB(class_prior=None, fit_prior=False)),])
		
		data = numpy.array([element[0] for element in self.whole_set])
		target = numpy.array([element[1] for element in self.whole_set])
		
		classifier.fit(data, target)
		return classifier


	def with_multinb(self):
		"""
		This with the help of self.multinomial_nb classify the self.text and returns an numpy array with predicted tags
		"""
		count_vect = CountVectorizer()
		tokenizer = SentenceTokenization()
		new_data = tokenizer.tokenize(self.text)
		
		classifier = self.multinomial_nb_classifier()

		predicted = classifier.predict(new_data)

		return zip(new_data, predicted)


	def svm_classifier(self):
		classifier = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()), 
			('clf', SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, n_iter=5)),])

		data = numpy.array([element[0] for element in self.whole_set])
		target = numpy.array([element[1] for element in self.whole_set])
		
		classifier.fit(data, target)
		return classifier

	def with_svm(self):

		classifier = self.svm_classifier()
		#new_data = self.sent_tokenizer.tokenize(self.text, realign_boundaries= True)
		
		##With the new class created in CustomSentenceTokenizer , the new sentence tokenizer
		#tokenizer = SentenceTokenizer()
		#new_data = [" ".join(word_tokenized_sentence) for word_tokenized_sentence in tokenizer.segment_text(self.text)]

		#With the new class made from text-sentence library
	
		tokenizer = SentenceTokenization()
		new_data = tokenizer.tokenize(self.text)
		predicted = classifier.predict(new_data)

		return zip(new_data, predicted)


	def logistic_regression_classifier(self):
		classifier = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()), 
			('clf', SGDClassifier(loss='log', penalty='l2', alpha=1e-3, n_iter=5)),])

		data = numpy.array([element[0] for element in self.whole_set])
		target = numpy.array([element[1] for element in self.whole_set])
		
		classifier.fit(data, target)
		return classifier

	def with_logisticregression(self):

		classifier = self.logistic_regression_classifier()
		#new_data = self.sent_tokenizer.tokenize(self.text, realign_boundaries= True)
		
		##With the new class created in CustomSentenceTokenizer , the new sentence tokenizer
		#tokenizer = SentenceTokenizer()
		#new_data = [" ".join(word_tokenized_sentence) for word_tokenized_sentence in tokenizer.segment_text(self.text)]

		#With the new class made from text-sentence library
	
		tokenizer = SentenceTokenization()
		new_data = tokenizer.tokenize(self.text)
		predicted = classifier.predict(new_data)

		return zip(new_data, predicted)

	def perceptron_classifier(self):
		classifier = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()), 
			('clf', Perceptron(n_iter=50)),])

		data = numpy.array([element[0] for element in self.whole_set])
		target = numpy.array([element[1] for element in self.whole_set])
		
		classifier.fit(data, target)
		return classifier

	def with_perceptron(self):

		classifier = self.perceptron_classifier()
		#new_data = self.sent_tokenizer.tokenize(self.text, realign_boundaries= True)
		
		##With the new class created in CustomSentenceTokenizer , the new sentence tokenizer
		#tokenizer = SentenceTokenizer()
		#new_data = [" ".join(word_tokenized_sentence) for word_tokenized_sentence in tokenizer.segment_text(self.text)]

		#With the new class made from text-sentence library
	
		tokenizer = SentenceTokenization()
		new_data = tokenizer.tokenize(self.text)
		predicted = classifier.predict(new_data)

		return zip(new_data, predicted)


	def ridge_regression_classifier(self):
		classifier = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()), 
			('clf', RidgeClassifier(tol=1e-2, solver="lsqr")),])

		data = numpy.array([element[0] for element in self.whole_set])
		target = numpy.array([element[1] for element in self.whole_set])
		
		classifier.fit(data, target)
		return classifier

	def with_ridgegression(self):

		classifier = self.ridge_regression_classifier()
		#new_data = self.sent_tokenizer.tokenize(self.text, realign_boundaries= True)
		
		##With the new class created in CustomSentenceTokenizer , the new sentence tokenizer
		#tokenizer = SentenceTokenizer()
		#new_data = [" ".join(word_tokenized_sentence) for word_tokenized_sentence in tokenizer.segment_text(self.text)]

		#With the new class made from text-sentence library
	
		tokenizer = SentenceTokenization()
		new_data = tokenizer.tokenize(self.text)
		predicted = classifier.predict(new_data)

		return zip(new_data, predicted)

	def passive_agressive_classifier(self):
		classifier = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()), 
			('clf', PassiveAggressiveClassifier(n_iter=50)),])

		data = numpy.array([element[0] for element in self.whole_set])
		target = numpy.array([element[1] for element in self.whole_set])
		
		classifier.fit(data, target)
		return classifier

	def with_passiveagressive(self):

		classifier = self.passive_agressive_classifier()
		#new_data = self.sent_tokenizer.tokenize(self.text, realign_boundaries= True)
		
		##With the new class created in CustomSentenceTokenizer , the new sentence tokenizer
		#tokenizer = SentenceTokenizer()
		#new_data = [" ".join(word_tokenized_sentence) for word_tokenized_sentence in tokenizer.segment_text(self.text)]

		#With the new class made from text-sentence library
	
		tokenizer = SentenceTokenization()
		new_data = tokenizer.tokenize(self.text)
		predicted = classifier.predict(new_data)

		return zip(new_data, predicted)


	def with_randomforests(self):

		data = numpy.array([element[0] for element in self.whole_set])
		target = numpy.array([element[1] for element in self.whole_set])
		classifier = Sklearn_RandomForest(data, target)
		
		tokenizer = SentenceTokenization()
		new_data = tokenizer.tokenize(self.text)

		return classifier.predict_with_chi_test(new_data)



