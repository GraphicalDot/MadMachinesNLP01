#!/usr/bin/env python
#-*- coding: utf-8 -*-



import nltk
from text_sentence import Tokenizer
import re
import itertools


def sentence_tokenizer():
	language_punkt_vars = nltk.tokenize.punkt.PunktLanguageVars
	language_punkt_vars.sent_end_chars=('։','՞','՜','.')

	trainer = nltk.tokenize.punkt.PunktTrainer(traindata, language_punkt_vars)

	trainer.INCLUDE_ALL_COLLOCS = True 
	trainer.INCLUDE_ABBREV_COLLOCS = True
	params = trainer.get_params()
	sbd = nltk.tokenize.punkt.PunktSentenceTokenizer(params)
	return sbd




def with_text_sentence(text):
	t = Tokenizer()
	sentences = list()
	sentences.append(list())
	tokenize_text = list(t.tokenize(text))
	for tagged_word in tokenize_text:
		if tagged_word.is_sent_end:
			sentences[-1].append(tagged_word.value)
			sentences.append(list())

		else:
			print tagged_word.value
			sentences[-1].append(tagged_word.value)
	
	split_on_interjection = splitting_on_interjections([" ".join(element) for element in sentences][0:-1])
	return splitting_on_special_characters(split_on_interjection)


def splitting_on_interjections(original_text):
	splitting_on_interjections.modified_sentence = list()
	splitting_on_interjections.modified_sentence.extend(original_text)
	INTERJECTIONS = ["BUT",  "ALTHOUGH",  "THOUGH",  "HOWEVER",  "OTHERWISE"]

	
	def per_intejection(interjection):
		another = list()
		for sentence in splitting_on_interjections.modified_sentence:
			regex = re.compile(r"{0}".format(interjection), flags=re.I)
			p = regex.split(sentence)
			new_list = list()
			for new_sentence in p:
				if p.index(new_sentence) != 0:
					new_list.append("{0}{1}".format(interjection.lower(), new_sentence))
				else:
					new_list.append(new_sentence)
			another.extend(new_list)
	
		splitting_on_interjections.modified_sentence = another
		return 

	

	for interjection in INTERJECTIONS:
		per_intejection(interjection)

	return splitting_on_interjections.modified_sentence


def splitting_on_special_characters(original_text):
	splitting_on_special_characters.modified_sentence = list()
	splitting_on_special_characters.modified_sentence.extend(original_text)
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
		for sentence in splitting_on_special_characters.modified_sentence:
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
		splitting_on_special_characters.modified_sentence = another
		return 
	
	def per_character_without_spaces(character):
		another = list()
		for sentence in splitting_on_special_characters.modified_sentence:
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
		splitting_on_special_characters.modified_sentence = another
		return 

	

	for character in SPECIAL_CHARACTERS:
		per_character_with_spaces(character)
		per_character_without_spaces(character)

	return splitting_on_special_characters.modified_sentence


