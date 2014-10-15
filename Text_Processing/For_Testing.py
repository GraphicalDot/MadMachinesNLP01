#!/usr/bin/env python
#-*- coding: utf-8 -*-

import nltk
import numpy
import random
import sys
import os
from optparse import OptionParser
import inspect
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

def get_all_algorithms_result(text, sentences_with_classification):
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
	
	classifier_cls = ForTestingClassifier(text)
	
	cls_methods_for_algortihms = [method[0] for method in inspect.getmembers(classifier_cls, predicate=inspect.ismethod) 
										if method[0].startswith("with")]
	
	target = [element[1] for element in sentences_with_classification]


	for cls_method in cls_methods_for_algortihms:
		classified_sentences = eval("{0}.{1}()".format("classifier_cls", cls_method))
		predicted = [element[1] for element in classified_sentences]

		correct_classification = float(len([element for element in zip(predicted, target) if element[0] == element[1]]))

		print "{0} gives -- {1}".format(cls_method.replace("with_", ""), correct_classification/len(predicted))

class ForTestingClassifier:
	def __init__(self, text, tokenizer=None):
		self.text = text #Text which needs classification
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


if __name__ == "__main__":
	text = """Oooooffffssssss....again a big name and a flop show..never expected that.. With a so hyped name nothing great about it..Went yesterday to try the restaurant.. But at the first glance while going up the stairs it did not give a good feel..once we entered.. it was a huge place with some low sitting and very dim light..so we decided not to sit here but in there other section...As the restaurant was not full...it took the waiter almost 20 min before we called him and asked if possible plz take the order...it was my mistake that I asked the server what is this" molecular gastronomy drinks"..it took them almost 10 min asking every person from bartender to the manager to know what are those THINGS in there so called menu and even at last they were not able to explain what's it... instead I got an answer"its just written in the menu but does not mean anything"i was quite surprised.. But thought let it go...Then I asked the server about some continental dishes in prawns but they said its not available but he can ask the chef to prepare..but my bad luck still followed and I got Chinese dish Instead of a continental one..and when i told I can't have Chinese dish it was replied its a conti dish with bell pepper and some spices.. I forced to call the chef who was generous enough to change the dish for us..Even we asked for a chicken veloute soup which was again not available.. I mean no prawns and no soup how they are running the damm show..And then we ordered beer which was chilled ..virgin mojito which was flat and Peri Peri chicken PIZZA WHICH WAS OKOK...Just a suggestion training's should be given to the staff..they are good at service and are polite but there knowledge lacks big time .."""
	
	
	sentences_with_classification =	[(u'oooooffffssssss ....', "overall"), 
			(u'again a big name and a flop show ..', "overall"),
			(u'never expected that ..', "null"),
			(u'with a so hyped name nothing great about it ..', "overall"),
			(u'went yesterday to try the restaurant ..', "null"),
			(u'but at the first glance while going up the stairs it did not give a good feel ..', "ambience"), 
			(u'once we entered ..', "null"),
			(u'it was a huge place with some low sitting and very dim light ..', "ambience"), 
			(u'so we decided not to sit here', "null"),
			('but in there other section ...', "null" ),
			(u'as the restaurant was not full ...', "overall"),
			(u'it took the waiter almost 20 min before we called him and asked if possible plz take the order ...', "service"),
			(u'it was my mistake that i asked the server what is this " molecular gastronomy drinks " ..', "service"),
			(u"it took them almost 10 min asking every person from bartender to the manager to know what are those things in there so called menu and even at last they were not able to explain what's it ...", "service"), 
			(u'instead i got an answer " its just written in the menu', "service"),
			('but does not mean anything " i was quite surprised ..', "null"),
			(u'but thought let it go ...', "null"),
			(u'then i asked the server about some continental dishes in prawns',"service" ), 
			('but they said its not available', "overall"),
			('but he can ask the chef to prepare ..', "service"), 
			(u'but my bad luck still followed and i got Chinese dish Instead of a continental one ..', "food" ), 
			(u"and when i told i can't have Chinese dish it was replied its a conti dish with bell pepper and some spices ..", "food"),
			(u'i forced to call the chef who was generous enough to change the dish for us ..', "service"),
			(u'even we asked for a chicken veloute soup which was again not available ..', "service"),
			(u'i mean no prawns and no soup how they are running the damm show ..', "food"),
			(u'and then we ordered beer which was chilled ..', "food"),
			(u'virgin mojito which was flat and Peri Peri chicken pizza which was okok ...', "food"), 
			(u"just a suggestion training's should be given to the staff ..", "service"),
			(u'they are good at service and are polite', "service"),
			('but there knowledge lacks big time ..' "service"),]
	
	
	
	
	get_all_algorithms_result(text, sentences_with_classification)
