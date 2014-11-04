#!/usr/bin/env python
#-*- coding: utf-8 -*-

import nltk
import numpy
import random
import sys
import os
from optparse import OptionParser
import inspect
import itertools
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



directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(directory)
from Algortihms import Sklearn_RandomForest
from Algortihms import SVMWithGridSearch


directory = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
path = os.path.join(directory + "/trainers")


class RepeatRecommendClassifier:
	def __init__(self, list_for_text_with_tags):
		"""
		Args:
			list_for_text_with_tags: The text which needs to be classfied
				This text will be in the form of a list of tuples with first element of every tuple representing the text,
					and second element representing the tag.
					[u"having expectations from this place it didn't quite live up to it ..", 
					u"maybe that is why the rating isn't 3 .", 
					u'i had lunch buffet so i would talk only about that .', 
					u'beginning with the soup , the bowl had black marks on its rim ..']


		Class-Variables:
			whole_set: 
				returns a list of tuples in the form
				[(u'top floor makes it more glamours then it could be .', 'repeated_customer'),
				(u'ever since the first time i went there , Tropical lounge has become my favorite .', 'recommended_customer'),
				(u'there were a good number of free tables , and to this day i wonder why he lied to us .', 'recommended_customer'), .............]
			data: 
				List of sentences from the whole set
			
			target:
				list of corresponding tag for the sentences present in data
		"""

		self.test = [element[0] for element in list_for_text_with_tags]

		self.tag_list = ["repeated_customer", "recommended_customer", "null"]
		
		self.sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
		self.data_lambda = lambda tag: [(sent, tag) for sent in 
					self.sent_tokenizer.tokenize(open("{0}/manually_classified_{1}.txt".format(path, tag), "rb").read(), realign_boundaries=True)
					if sent != ""]
			
		
		#joining list of lists returned by self.data, Every tag will have their own list, Itertools will join these lists into a single list	
		self.whole_set = list(itertools.chain(*[self.data_lambda(tag) for tag in self.tag_list]))
		
		#Shuffling the list formed ten times to get better results.
		[random.shuffle(self.whole_set) for i in range(0, 10)]
		
		self.data = numpy.array([element[0] for element in self.whole_set])
		self.target = numpy.array([element[1] for element in self.whole_set])
		



	def return_treated_text(self, tags):
		return [(element[0][0], element[0][1], element[1]) for element in zip(self.list_of_tuples_for_text, tags)]




	def naive_bayes_classifier(self):
		pass


	def __multinomial_nb_classifier(self):
		"""
		This method returns a classfier trained with multinomial naive bayes using cost, services and ambience as three categories
		fit_prior : boolean
			Whether to learn class prior probabilities or not. If false, a uniform prior will be used.
		class_prior : array-like, size (n_classes,)
			Prior probabilities of the classes. If specified the priors are not adjusted according to the data.
		"""
		print "\n Running {0} \n".format(inspect.currentframe())
		
		classifier = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()), 
			('clf', MultinomialNB(class_prior=None, fit_prior=False)),])
		
		data = numpy.array([element[0] for element in self.whole_set])
		target = numpy.array([element[1] for element in self.whole_set])
		
		classifier.fit(data, target)
		return classifier


	def with_multinomial_naive_bayes(self):
		"""
		This with the help of self.multinomial_nb classify the self.text and returns an numpy array with predicted tags
		"""
		
		print "\n Running {0} \n".format(inspect.stack()[0][3])
		
		classifier = self.__multinomial_nb_classifier()

		predicted = classifier.predict(self.test)

		return predicted


	def __svm_classifier(self):
		classifier = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()), 
			('clf', SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, n_iter=5)),])

		data = numpy.array([element[0] for element in self.whole_set])
		target = numpy.array([element[1] for element in self.whole_set])
		
		classifier.fit(data, target)
		return classifier

	def with_support_vector_machines(self):
		print "\n Running {0} \n".format(inspect.stack()[0][3])

		classifier = self.__svm_classifier()
		#new_data = self.sent_tokenizer.tokenize(self.text, realign_boundaries= True)
		
		##With the new class created in CustomSentenceTokenizer , the new sentence tokenizer
		#tokenizer = SentenceTokenizer()
		#new_data = [" ".join(word_tokenized_sentence) for word_tokenized_sentence in tokenizer.segment_text(self.text)]

		#With the new class made from text-sentence library
	
		predicted = classifier.predict(self.test)

		return predicted


	def __logistic_regression_classifier(self):
		classifier = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()), 
			('clf', SGDClassifier(loss='log', penalty='l2', alpha=1e-3, n_iter=5)),])

		data = numpy.array([element[0] for element in self.whole_set])
		target = numpy.array([element[1] for element in self.whole_set])
		
		classifier.fit(data, target)
		return classifier

	def with_logistic_regression(self):
		print "\n Running {0} \n".format(inspect.stack()[0][3])

		classifier = self.__logistic_regression_classifier()
		#new_data = self.sent_tokenizer.tokenize(self.text, realign_boundaries= True)
		
		##With the new class created in CustomSentenceTokenizer , the new sentence tokenizer
		#tokenizer = SentenceTokenizer()
		#new_data = [" ".join(word_tokenized_sentence) for word_tokenized_sentence in tokenizer.segment_text(self.text)]

		#With the new class made from text-sentence library
	
		predicted = classifier.predict(self.test)

		return predicted

	def __perceptron_classifier(self):
		classifier = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()), 
			('clf', Perceptron(n_iter=50)),])

		data = numpy.array([element[0] for element in self.whole_set])
		target = numpy.array([element[1] for element in self.whole_set])
		
		classifier.fit(data, target)
		return classifier

	def with_perceptron(self):

		print "\n Running {0} \n".format(inspect.stack()[0][3])
		classifier = self.__perceptron_classifier()
		#new_data = self.sent_tokenizer.tokenize(self.text, realign_boundaries= True)
		
		##With the new class created in CustomSentenceTokenizer , the new sentence tokenizer
		#tokenizer = SentenceTokenizer()
		#new_data = [" ".join(word_tokenized_sentence) for word_tokenized_sentence in tokenizer.segment_text(self.text)]

		#With the new class made from text-sentence library
	
		predicted = classifier.predict(self.test)

		return predicted


	def __ridge_regression_classifier(self):
		classifier = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()), 
			('clf', RidgeClassifier(tol=1e-2, solver="lsqr")),])

		data = numpy.array([element[0] for element in self.whole_set])
		target = numpy.array([element[1] for element in self.whole_set])
		
		classifier.fit(data, target)
		return classifier

	def with_ridge_regression(self):
		print "\n Running {0} \n".format(inspect.stack()[0][3])

		classifier = self.__ridge_regression_classifier()
		#new_data = self.sent_tokenizer.tokenize(self.text, realign_boundaries= True)
		
		##With the new class created in CustomSentenceTokenizer , the new sentence tokenizer
		#tokenizer = SentenceTokenizer()
		#new_data = [" ".join(word_tokenized_sentence) for word_tokenized_sentence in tokenizer.segment_text(self.text)]

		#With the new class made from text-sentence library
	
		predicted = classifier.predict(self.test)

		return predicted

	def __passive_agressive_classifier(self):
		classifier = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()), 
			('clf', PassiveAggressiveClassifier(n_iter=50)),])

		data = numpy.array([element[0] for element in self.whole_set])
		target = numpy.array([element[1] for element in self.whole_set])
		
		classifier.fit(data, target)
		return classifier

	def with_passive_agressive(self):
		print "\n Running {0} \n".format(inspect.stack()[0][3])

		classifier = self.__passive_agressive_classifier()
		#new_data = self.sent_tokenizer.tokenize(self.text, realign_boundaries= True)
		
		##With the new class created in CustomSentenceTokenizer , the new sentence tokenizer
		#tokenizer = SentenceTokenizer()
		#new_data = [" ".join(word_tokenized_sentence) for word_tokenized_sentence in tokenizer.segment_text(self.text)]

		#With the new class made from text-sentence library
	
		predicted = classifier.predict(self.test)

		return predicted


	def with_random_forests(self):

		print "\n Running {0} \n".format(inspect.stack()[0][3])
		data = numpy.array([element[0] for element in self.whole_set])
		target = numpy.array([element[1] for element in self.whole_set])
		classifier = Sklearn_RandomForest(data, target)
		

		predicted = classifier.predict_with_chi_test(self.test)
		return [element[1] for element in predicted]

	def with_svm_grid_search(self):
		print "\n Running {0} \n".format(inspect.stack()[0][3])
		classifier = SVMWithGridSearch(self.data, self.target)
		#tokenizer = SentenceTokenization()
		#new_data = tokenizer.tokenize(self.text)
		predicted = classifier.predict(self.test)
		return [element[1] for element in predicted]


"""

if __name__ == "__main__":
	
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
	
	
	___class = RepeatRecommendClassifier(list_for_text_with_tags=sentences_with_classification)
	print ___class.whole_set
	print ___class.with_logistic_regression()
	print ___class.with_multinomial_naive_bayes()
	print ___class.with_support_vector_machines()

"""
