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


"""

from Blob import ProcessingWithBlobInMemory
import os
import sys
import nltk
import inspect
db_script_path = os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
sys.path.insert(0, db_script_path)
#from get_reviews import GetReview
from textblob import TextBlob
import re
directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(directory))
from MainAlgorithms import InMemoryMainClassifier, timeit, cd, path_parent_dir, path_trainers_file, path_in_memory_classifiers
from Sentence_Tokenization import SentenceTokenizationOnRegexOnInterjections

class TestNounPhrasesAlgorithms:
        """
        Args:
                sentences: list of tuples with first element being a text and second element being a list of noun phrases extraction
        """
        def __init__(self, sentences):
                self.sent_tokenizer = SentenceTokenizationOnRegexOnInterjections()
                self.for_nouns_only_grammer = r"""CustomNounP:{<NN.*><NN>*<NN>}
                                                    CustomNounWithVBN: {<NN>?<VBN><NN>*<NN.*>}
                                                    CustomNounWithJJ: {<JJ><NN>.*<NN.*>}"""
                self.sentences = sentences


        def with_nltk(self):
                """
                returns a list of list
                with each element of the parent list as a list of noun phrases for the sentence in the original
                self.sentences
                """
                noun_phrases_list = list()
                for __sent, nouns in self.sentences:
                        __noun_phrases_list = list()
                        cp = nltk.RegexpParser(self.for_nouns_only_grammer)
                        for sentence in self.sent_tokenizer.tokenize(__sent):
                                tree = cp.parse(nltk.pos_tag(nltk.wordpunct_tokenize(sentence)))
                                for subtree in tree.subtrees(filter = lambda t: t.label()=='CustomNounP' or t.label()== 'CustomNounWithVBN' or \
                                                    t.label() == 'CustomNounWithJJ'):
                                        __noun_phrases_list.append(" ".join([e[0] for e in subtree.leaves()]))
                        noun_phrases_list.append(__noun_phrases_list)
                return noun_phrases_list


        @staticmethod
        def compare_results(__l1, __l2):
                """
                __l1 : Noun phrase that were expected
                __l2 : Noun Phrases that were being extraced by the custom algorithm

                """

                print "Noun Phrases expected {0}".format(__l1)
                print "Noun Phrases extracted {0}".format(__l2)
                result = list(set(__l1) - set(__l2))
                if bool(result):
                        print "Failed Algorithm"
                        print "Didnt succeed in capturing {0} \n".format(result)
                else:
                        print "success \n"



if __name__ == "__main__":
        sentences = [("Well the ferrero rocher shake, the kitkat shake and the chocolate bloodbath is a must have! Plus, \
            it doesn't hit your pocket!The ambience is pretty good, specially because it gives you the perfect view of the fort :) must try once!", \
            ["ferrero rocher shake", "kitkat shake", "chocolate bloodbath", "perfect view"]),

                    ("We ordered a lot of things… caesar chicken salad, chicken n cheese nachos, shawarma roll, veg pizza, penne alfredo, \
                            bbq hot dog, cottage cheese bbq, thai red curry, fried rice…for the drinks we had hazelnut coffee, cold coffee with \
                            ice cream and a mango mint shake. The mango mint shake was amazing and a really new taste for my bud. For the food…\
                            the best thing was the thin crust pizza among the appetizers. Chicken n cheese nachos were bland, even the dip was sweet\
                            and didn’t do justice to the dish.", 
                            ["caesar chicken salad", "chicken n cheese nachos", "shawarma roll", "veg pizza", "penne alfredo", "bbq hot dog",\
                            "cottage cheese bbq", "thai red curry", "fried rice", "hazelnut coffee", "cold coffee with ice cream", "mango mint shake"
                            , "thin crust pizza", "chicken n cheese nachos"])

                ]

        ins = TestNounPhrasesAlgorithms(sentences)
        for sentence, resulting_nouns in zip(sentences, ins.with_nltk()):
                TestNounPhrasesAlgorithms.compare_results(sentence[1], resulting_nouns)



