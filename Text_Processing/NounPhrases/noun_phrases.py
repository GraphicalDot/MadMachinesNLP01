#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
Author: Kaali
Dated: 31 january, 2015
This file lists the sentences and the noun phrasesthat hould be extracted
and test several noun phrases extraction algorithms whether they are providing desired output

Another method
"""
##TODO: Make sure that while shifting on new servers, a script has to be wriiten to install java and stanforn pos tagger files
##http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html



import os
import sys
import inspect
import nltk
import re
from functools import wraps
from nltk.tag.hunpos import HunposTagger
from textblob.np_extractors import ConllExtractor
from textblob import TextBlob
from nltk.tag.stanford import POSTagger
db_script_path = os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
sys.path.insert(0, db_script_path)
#from get_reviews import GetReview
directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(directory))
from MainAlgorithms import InMemoryMainClassifier, timeit, cd, path_parent_dir, path_trainers_file, path_in_memory_classifiers
stanford_file_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.join(stanford_file_path))


def need_pos_tagged(pos_tagged):  
        def tags_decorator(func):
                @wraps(func)
                def func_wrapper(self, *args, **kwargs):
                        if pos_tagged and type(self.list_of_sentences[0]) != list :
                                raise StandardError("The pos tagger you are trying run needs pos tagged list of sentences\
                                        Please try some other pos tagger which doesnt require word tokenized sentences")
                        func(self, *args, **kwargs)
                return func_wrapper 
        return tags_decorator  



class NounPhrases:
        def __init__(self, list_of_sentences, default_np_extractor=None, regexp_grammer=None):
		"""
                Args:
                        list_of_sentences: A list of lists with each element is a list of sentences which is pos tagged
                        Example:
                                [[('I', 'PRP'), ('went', 'VBD'), ('there', 'RB'), ('for', 'IN'), ('phirni', 'NN')], [], [], ...]

                        default_np_extractor:
                                    if a list been passed then the noun phrases from various np_extractors will be appended
                                    if a string is passed, only the noun phrases from that np extractor will be appended
                                    Options
                                        regex_np_extractor
                                        regex_textblob_conll_np
                                        textblob_np_conll
                                        textblob_np_base
                """
                self.noun_phrases = list()
                self.conll_extractor = ConllExtractor()
                self.list_of_sentences = list_of_sentences
                self.np_extractor = ("textblob_np_conll", default_np_extractor)[default_np_extractor != None]
                eval("self.{0}()".format(self.np_extractor)) 
               
                self.noun_phrases = {self.np_extractor: self.noun_phrases}
                
                return 


        @need_pos_tagged(False)
	def textblob_np_conll(self):
                for __sentence in self.list_of_sentences:
		        __sentence = " ".join([element[0] for element in __sentence])
                        blob = TextBlob(__sentence, np_extractor=self.conll_extractor)
                        self.noun_phrases.append(list(blob.noun_phrases))
                return
        
        @need_pos_tagged(False)
        def textblob_np_base(self):
                for __sentence in self.list_of_sentences:
		        blob = TextBlob(__sentence)
		        self.noun_phrases.append(blob.noun_phrases)
                return



