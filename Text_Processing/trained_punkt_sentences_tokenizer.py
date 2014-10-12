#!/usr/bin/env python
#-*- coding: utf-8 -*-



import nltk
from text_sentence import Tokenizer
import re
import itertools

class SentenceTokenization:
	"""
	This class uses https://pypi.python.org/pypi/text-sentence/0.14
	text-sentence library to break a chunk of text into sentences
	
	It also has Two class methods whose working and results are menntioned below
	splitting_on_special_characters:
		This method splits the text on the basis of special characters

	splitting_on_interjections:
		This method breaks the sentences on the basis of interjections
	"""
	def __init__(self):
		self.custom_tokenizer = Tokenizer()
	
	def tokenize(self, text):
		self.splitting_on_interjections_modified_sentence = list()
		self.splitting_on_special_characters_modified_sentence = list()
		sentences = list()
		sentences.append(list())
		tokenize_text = list(self.custom_tokenizer.tokenize(text))
		for tagged_word in tokenize_text:
			if tagged_word.is_sent_end:
				sentences[-1].append(tagged_word.value)
				sentences.append(list())
	
			else:
				sentences[-1].append(tagged_word.value)
		
		split_on_interjection = self.splitting_on_interjections([" ".join(element) for element in sentences][0:-1])
		return self.splitting_on_special_characters(split_on_interjection)
	
	
	def splitting_on_interjections(self, original_text):
		"""
		This class method tokenize the provided rext on the basis of the INTERJECTIONS.
		Every word present in the INTERJECTIONS will break the sentence like /sBUT/s
		If you want to tokenize text on the basis of the additonal Interjections, Just add that interjection 
		to the INTERJECTIONS list, This method will then automatically starts tokenize the text on the basis of that
		newly added interjection also
		"""
		self.splitting_on_interjections_modified_sentence.extend(original_text)
		INTERJECTIONS = ["BUT",  "ALTHOUGH",  "THOUGH",  "HOWEVER",  "OTHERWISE"]
	
		
		def per_intejection(interjection):
			another = list()
			for sentence in self.splitting_on_interjections_modified_sentence:
				regex = re.compile(r"\s{0}\s".format(interjection), flags=re.I)
				p = regex.split(sentence)
				new_list = list()
				for new_sentence in p:
					if p.index(new_sentence) != 0:
						new_list.append("{0} {1}".format(interjection.lower(), new_sentence))
					else:
						new_list.append(new_sentence)
				another.extend(new_list)
		
			self.splitting_on_interjections_modified_sentence = another
			return 
	
		
	
		for interjection in INTERJECTIONS:
			per_intejection(interjection)
	
		return self.splitting_on_interjections_modified_sentence
	
	
	def splitting_on_special_characters(self, original_text):
		"""
		This class method works exactly like splitting_on_interjections.
		IN this case we have a list of dictionaries in which the on_repetitions key for every special characters 
		specefies whether the sentence will be tokenize on the single occurence or more than single occurence of 
		that special character.
		"""
		self.splitting_on_special_characters_modified_sentence.extend(original_text)
		SPECIAL_CHARACTERS = [
					{"char": ",", "on_repetitions": "more_than_one_repetition"},
					{"char": ":", "on_repetitions": "single"},
					{"char": "-", "on_repetitions": "more_than_one_repetition"},
					{"char": "_", "on_repetitions": "more_than_one_repetition"},
					{"char": "\\", "on_repetitions": "more_than_one_repetition"},
					{"char": "/", "on_repetitions": "more_than_one_repetition"},
					{"char": "!", "on_repetitions": "more_than_one_repetition"},
					]
	
		
		def per_character_with_spaces(character):
			another = list()
			for sentence in self.splitting_on_special_characters_modified_sentence:
				if character["on_repetitions"] == "single":
					regex = re.compile(r'\s%s{1,}\s'%character['char'])
					p = regex.split(sentence)
				else:
					regex = re.compile(r'\s%s{2,}\s'%character['char'])
					p = regex.split(sentence)
				new_list = list()
				for new_sentence in p:
					if p.index(new_sentence) != 0:
						new_list.append("{0}{1}".format(character["char"], new_sentence))
					else:
						new_list.append(new_sentence)
				another.extend(new_list)
			self.splitting_on_special_characters_modified_sentence = another
			return 
		
		def per_character_without_spaces(character):
			another = list()
			for sentence in self.splitting_on_special_characters_modified_sentence:
				if character["on_repetitions"] == "single":
					regex = re.compile(r'%s{1,}'%character['char'])
					p = regex.split(sentence)
				else:
					regex = re.compile(r'%s{2,}'%character['char'])
					p = regex.split(sentence)
				new_list = list()
				for new_sentence in p:
					if p.index(new_sentence) != 0:
						new_list.append("{0}{1}".format(character["char"], new_sentence))
					else:
						new_list.append(new_sentence)
				another.extend(new_list)
			self.splitting_on_special_characters_modified_sentence = another
			return 
	
		
	
		for character in SPECIAL_CHARACTERS:
			per_character_with_spaces(character)
			per_character_without_spaces(character)
	
		return self.splitting_on_special_characters_modified_sentence
	

