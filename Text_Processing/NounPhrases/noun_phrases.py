#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
Author: Kaali
Dated: 31 january, 2015
This file lists the sentences and the noun phrasesthat hould be extracted
and test several noun phrases extraction algorithms whether they are providing desired output

Another method

train_sents = [
    [('select', 'VB'), ('the', 'DT'), ('files', 'NNS')],
        [('use', 'VB'), ('the', 'DT'), ('select', 'JJ'), ('function', 'NN'), ('on', 'IN'), ('the', 'DT'), ('sockets', 'NNS')],
            [('the', 'DT'), ('select', 'NN'), ('files', 'NNS')],
            ]


tagger = nltk.TrigramTagger(train_sents, backoff=default_tagger)
Note, you can use NLTK's NGramTagger to train a tagger using an arbitrarily high number of n-grams, but typically you don't get much performance 
increase after trigrams.
grammer = r"CustomNounP:{<JJ|VB|FW>?<NN.*>*<NN.*>}"
grammer = r"CustomNounP:{<JJ|VB|FW|VBN>?<NN.*>*<NN.*>}"

                food:
                <NNP><NNS>, "Mozralle fingers"
                (u'Chicken', u'NNP'), (u'Skewer', u'NNP'), (u'bbq', u'NN'), (u'Sauce', u'NN')
                (u'Mozarella', u'NNP'), (u'Fingers', u'NNP')
                 review_ids = ['4971051', '3948891', '5767031', '6444939', '6500757', '854440']
                '4971051' 
                     (u'Ferrero', u'NNP'), (u'Rocher', u'NNP'), (u'shake', u'NN'), 
                     (u'lemon', u'JJ'), (u'iced', u'JJ'), (u'tea', u'NN'), 
                     (u'mezze', u'NN'), (u'platter', u'NN'), 
                     (u'banoffee', u'NN'), (u'cronut', u'NN'),
                '3948891', 
                    (u'China', u'NNP'), (u'Box', u'NNP'), (u'with', u'IN'), (u'Chilly', u'NNP'), (u'Paneer', u'NNP'), 
                    (u'Vada', u'NNP'), (u'pao', u'NNP'), 
                    (u'Mezze', u'NNP'), (u'Platter', u'NNP'), 
                    (u'Naga', u'NNP'), (u'Chili', u'NNP'), (u'Toast', u'NNP'), 
                    (u'Paneer', u'NNP'), (u'Makhani', u'NNP'), (u'Biryani', u'NNP'), 
                    (u'Kit', u'NN'), (u'Kat', u'NN'), (u'shake', u'NN'), 
                    (u'ferrero', u'NN'), (u'rocher', u'NN'), (u'shake', u'NN'), 
                    
                '5767031', 
                     (u'Tennessee', u'NNP'), (u'Chicken', u'NNP'), (u'Wings', u'NNP')
                     (u'vada', u'VB'), (u'Pao', u'NNP'), (u'Bao', u'NNP')
                     (u'bombay', u'VB'), (u'Bachelors', u'NNP'), (u'Sandwich', u'NNP'), 
                     (u'Mile', u'NNP'), (u'High', u'NNP'), (u'Club', u'NNP'), (u'Veg', u'NNP'), (u'Sandwich', u'NNP'),
                '6444939', 
                
                '6500757', 
                
                '854440'
        
                cost:
                '4971051' 
                    (u'prices', u'NNS'), (u'are', u'VBP'), (u'very', u'RB'), (u'cheap', u'JJ')
                '3948891', 
                
                '5767031', 
                
                '6444939', 
                
                '6500757', 
                
                '854440'
                        (u'a', u'DT'), (u'hole', u'NN'), (u'on', u'IN'), (u'pockets', u'NNS')

                ambience
                '4971051' 
                    (u'place', u'NN'), (u'is', u'VBZ'), (u'creatively', u'RB'), (u'decorated', u'VBN'),
                '3948891', 
                    (u'the', u'DT'), (u'interiors', u'NNS'), (u'are', u'VBP'), (u'done', u'VBN'), (u'in', u'IN'), (u'a', u'DT'), (u'very', u'RB'), (u'interesting', u'JJ'), (u'manner', u'NN')
                '5767031', 
                    (u'interiors', u'NNS'), (u'are', u'VBP'), (u'eye', u'NN'), (u'catching', u'VBG'), (u'and', u'CC'), (u'quirky', u'JJ')
                '6444939', 
                
                '6500757', 
                
                '854440'

                service
                '4971051' 
                    (u'serving', u'VBG'), (u'was', u'VBD'), (u'delightful', u'JJ')
                '3948891', 
                
                '5767031', 
                    (u'serve', u'VBP'), (u'drinks', u'NNS'), (u'and', u'CC'), (u'food', u'NN'), (u'in', u'IN'), (u'some', u'DT'), (u'interesting', u'JJ'), (u'glasses', u'NNS')

                '6444939', 
                
                '6500757', 
                
                '854440'
                
                overall
                '3948891', 
                    (u'the', u'DT'), (u'place', u'NN'), (u'is', u'VBZ'), (u'huge', u'JJ') 
                '5767031', 
                    (u'brimming', u'VBG'), (u'with', u'IN'), (u'people', u'NNS'),
                '6444939', 
                
                '6500757', 
                
                '854440'


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
                print "from the noun phrases class %s"%len(self.list_of_sentences)
                self.np_extractor = ("textblob_np_conll", default_np_extractor)[default_np_extractor != None]
                if not regexp_grammer:
                        self.regexp_grammer = r"CustomNounP:{<JJ|VB|FW|VBN>?<NN.*>*<NN.*>}"

                print "self.{0}()".format(self.np_extractor)
                eval("self.{0}()".format(self.np_extractor)) 
               
                self.noun_phrases = {self.np_extractor: self.noun_phrases}
                
                return 

        @need_pos_tagged(True)
        def regex_np_extractor(self):
                __parser = nltk.RegexpParser(self.regexp_grammer)
                for __sentence in self.list_of_sentences:
                        tree = __parser.parse(__sentence)
                        for subtree in tree.subtrees(filter = lambda t: t.label()=='CustomNounP'):
                                self.noun_phrases.append(" ".join([e[0] for e in subtree.leaves()]))
                return



        @need_pos_tagged(False)
	def textblob_np_conll(self):
                for __sentence in self.list_of_sentences:
		        blob = TextBlob(__sentence, np_extractor=self.conll_extractor)
                        self.noun_phrases.append(list(blob.noun_phrases))
                return
        
        @need_pos_tagged(False)
        def textblob_np_base(self):
                for __sentence in self.list_of_sentences:
		        blob = TextBlob(__sentence)
		        self.noun_phrases.append(blob.noun_phrases)
                return


        @need_pos_tagged(True)
        def regex_textblob_conll_np(self):
                """
                Gives a union of the noun phrases of regex grammer and text blob conll noun phrases
                """
                __parser = nltk.RegexpParser(self.regexp_grammer)
                for __sentence in self.list_of_sentences:
                        __noun_phrases = list()
		        blob = TextBlob(" ".join([_word[0] for _word in __sentence]),)
                        tree = __parser.parse(__sentence)
                        for subtree in tree.subtrees(filter = lambda t: t.label()=='CustomNounP'):
                                __noun_phrases.append(" ".join([e[0] for e in subtree.leaves()]))
                        __union = list(set(__noun_phrases)|set(blob.noun_phrases))
                        self.noun_phrases.append(__union)
                return

