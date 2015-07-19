#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import sys
import time

from itertools import ifilter
from sklearn.externals import joblib
from collections import Counter                
from topia.termextract import extract
from query_clustering import QueryClustering


parent_dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir_path)

from Text_Processing.Sentence_Tokenization.Sentence_Tokenization_Classes import SentenceTokenizationOnRegexOnInterjections
from GlobalConfigs import connection, eateries, reviews, yelp_eateries, yelp_reviews
from Text_Processing.NounPhrases.noun_phrases import NounPhrases

from GlobalAlgorithmNames import TAG_CLASSIFIER_LIB, SENTI_CLASSIFIER_LIB, FOOD_SB_TAG_CLASSIFIER_LIB,\
            COST_SB_TAG_CLASSIFIER_LIB, SERV_SB_TAG_CLASSIFIER_LIB, AMBI_SB_TAG_CLASSIFIER_LIB, FOOD_SUB_TAGS,\
            COST_SUB_TAGS, SERV_SUB_TAGS, AMBI_SUB_TAGS, NOUN_PHSE_ALGORITHM_NAME




topia_extractor = extract.TermExtractor()
class QueryResolution(object):
        def __init__(self, text=None):
                self.text = text
                if not text:
                    self.text = "The ambience was breathtaking. The view was breathtaking"
                    #self.text = "Green Apple Mojito – The bar at HRC is huge and we decided to order the Green Apple Mojito from the ‘Summer’s of the Legends’ Menu. The drink was made from green apples along with Mint. The taste was refreshing. 8/10 Red Hot Chili Fried – Crispy fries with sweet and chili sauce. The fries are topped with cheddar cheese. The dish is served with a portion of tangy salsa dip and cheesy dip. The cheesy dip was so-so and didn’t have any particular flavors. The portion size of this dish was huge and a little more sweet and chili sauce would have been  icing on the cake. 8/10"
                
                self.tokenized_sents, self.food_sents, self.serv_sents,\
                self.cost_sents, self.ambi_sents = [], [], [], [], []


                self.food_sub_sents, self.serv_sub_sents, self.ambi_sub_sents,\
                self.cost_sub_sents = [], [], [], []
                self.result = {}



        def run(self):
                self.sentence_tokenization()
                self.classification()
                self.food_sub_classification()
                self.ambience_sub_classification()
                self.cost_sub_classification()
                self.service_sub_classification()
                self.initiate_dictionaries()
                self.noun_phrase_extraction()
                self.populate_result()
                sentences = {"food": self.food_sub_sents, "ambience": self.ambi_sub_sents, "cost": self.cost_sub_sents, 
                                "service": self.serv_sub_sents}
                self.result.update({"sentences": sentences})
                return self.result


        def sentence_tokenization(self):
                """
                Deals with the sentence tokenization for the self.text
                """
                sent_tokenizer = SentenceTokenizationOnRegexOnInterjections()
                self.tokenized_sents = sent_tokenizer.tokenize(self.text)
                return 

        def classification(self):
                """
                deals with the main classification of the sentences
                """
                result = zip(self.tokenized_sents, TAG_CLASSIFIER_LIB.predict(self.tokenized_sents))
                print "Query tag classification result \n"
                print result
                print "Query tag classification finished \n"

                self.food_sents = [(sent, tag) for (sent, tag) in result if tag == "food"]
                self.ambi_sents = [(sent, tag) for (sent, tag) in result if tag == "ambience"]
                self.cost_sents = [(sent, tag) for (sent, tag) in result if tag == "cost"]
                self.serv_sents = [(sent, tag) for (sent, tag) in result if tag == "service"]
                return 

                
        def food_sub_classification(self):
                if not self.food_sents:
                        self.food_sub_sents = []
                        return 
                only_food_sent, food_tags = zip(*self.food_sents)
                self.food_sub_sents = zip(only_food_sent, FOOD_SB_TAG_CLASSIFIER_LIB.predict(only_food_sent))
                return 
        
        def cost_sub_classification(self):
                """
                """
                if not self.cost_sents:
                        self.cost_sub_sents = []
                        return 
                only_cost_sent, cost_tags = zip(*self.cost_sents)
                self.cost_sub_sents = zip(only_cost_sent, COST_SB_TAG_CLASSIFIER_LIB.predict(only_cost_sent))
                return 
        
        def ambience_sub_classification(self):
                """
                """
                if not self.ambi_sents:
                        self.ambience_sub_sents = []
                        return 
                only_ambi_sent, ambi_tags = zip(*self.ambi_sents)
                self.ambi_sub_sents = zip(only_ambi_sent, AMBI_SB_TAG_CLASSIFIER_LIB.predict(only_ambi_sent))
                return 
        
        def service_sub_classification(self):
                """
                """
                if not self.serv_sents:
                        self.serv_sub_sents = []
                        return 
                only_serv_sent, serv_tags = zip(*self.serv_sents)
                self.serv_sub_sents = zip(only_serv_sent, SERV_SB_TAG_CLASSIFIER_LIB.predict(only_serv_sent))
                return 


        def initiate_dictionaries(self):

                self.food_dictionary = dict.fromkeys(FOOD_SUB_TAGS, [])
                [self.food_dictionary.update({__sub_tag: [sent for (sent, tag) in ifilter(lambda x: x[1] == __sub_tag, self.food_sub_sents)]})\
                                                                                                        for __sub_tag in FOOD_SUB_TAGS]
                
                self.ambi_dictionary = dict.fromkeys(AMBI_SUB_TAGS, [])
                [self.ambi_dictionary.update({__sub_tag: [sent for (sent, tag) in ifilter(lambda x: x[1] == __sub_tag, self.ambi_sub_sents)]})\
                                                                                                            for __sub_tag in AMBI_SUB_TAGS]
                
                self.cost_dictionary = dict.fromkeys(COST_SUB_TAGS, [])
                [self.cost_dictionary.update({__sub_tag: [sent for (sent, tag) in ifilter(lambda x: x[1] == __sub_tag, self.cost_sub_sents)]})\
                                                                                                            for __sub_tag in COST_SUB_TAGS]
                
                self.serv_dictionary = dict.fromkeys(SERV_SUB_TAGS, [])
                [self.serv_dictionary.update({__sub_tag: [sent for (sent, tag) in ifilter(lambda x: x[1] == __sub_tag, self.serv_sub_sents)]}) \
                                                                                                            for __sub_tag in SERV_SUB_TAGS]
                return 


        def noun_phrase_extraction(self):
                """
                self.all_food_with_nps = [[sent, tag, sentiment, sub_tag, nps] for ((sent, tag, sentiment, sub_tag,), nps) in 
                        zip(self.all_food, __nouns.noun_phrases[NOUN_PHSE_ALGORITHM_NAME])] 
                map(lambda __list: __list.append(self.review_time), self.all_food_with_nps) 
                """

                for __sub_food_tag in ["dishes", "place-food", "sub-food"]:
                        if self.food_dictionary.get(__sub_food_tag):
                                sentences = self.food_dictionary.get(__sub_food_tag)
                                self.food_dictionary.update({__sub_food_tag: self.clustering(sentences)})
                return 


        def clustering(self, sentences_list):
                nouns = topia_extractor(" ".join(sentences_list)) 
                noun_phrases = Counter([e[0] for e in nouns]).keys()
                ins = QueryClustering(noun_phrases, sub_category="dishes", sentences= sentences_list)
                return ins.run()
                

        def populate_result(self):
                """
                self.ambi_dictionary.pop("ambience-null")
                self.serv_dictionary.pop("service-null")
                """
                self.result.update({"ambience": filter(lambda x: self.ambi_dictionary[x], AMBI_SUB_TAGS)})
                self.result.update({"cost": filter(lambda x: self.cost_dictionary[x], COST_SUB_TAGS)})
                self.result.update({"service": filter(lambda x: self.serv_dictionary[x], SERV_SUB_TAGS)})

                [self.food_dictionary.pop(key) for key in filter(lambda x: not self.food_dictionary[x], self.food_dictionary.keys())]
                if self.food_dictionary.has_key("null-food"):
                        self.food_dictionary.pop("null-food")
                self.result.update({"food": self.food_dictionary})
                return

if __name__ == "__main__":
        ins = QueryResolution(None)
        print ins.run()
