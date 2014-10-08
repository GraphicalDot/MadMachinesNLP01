#!/usr/bin/env python
#-*- coding: utf-8 -*-



import nltk
from text_sentence import Tokenizer
import re

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
	for tagged_word in list(t.tokenize(text)):
		if tagged_word.is_sent_end:
			sentences[-1].append(tagged_word.value)
			sentences.append(list())

		else:
			sentences[-1].append(tagged_word.value)
	
	return [" ".join(element) for element in sentences][0:-1]



def splitting_on_interjections(sentence):
	modified_sentence = list()
	modified_sentence.append(sentence)
	INTERJECTIONS = ["BUT",  "ALTHOUGH",  "THOUGH",  "HOWEVER",  "OTHERWISE"]
	for interjection in INTERJECTIONS:
			regex = re.compile(r"{0}".format(inter), flags=re.I)
			regex.split(sentence)
	return 



