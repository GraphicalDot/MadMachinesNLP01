#-*- coding: utf-8 -*-
from nltk.util import ngrams


def nltk_ngrams(sentence, grams):
	gram_dict = {"Unigram": 1, "Bigram": 2, "Trigram": 3, "Quadgram": 4}
	result = ngrams(sentence.split(), gram_dict[grams])
	return [(" ").join(str(i) for i in e) for e in result]


