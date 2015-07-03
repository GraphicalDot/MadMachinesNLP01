#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import sys
from sklearn.externals import joblib
from Text_Processing.Sentence_Tokenization.Sentence_Tokenization_Classes import SentenceTokenizationOnRegexOnInterjections
from GlobalConfigs import connection, eateries, reviews, yelp_eateries, yelp_reviews


from ProductionEnvironmentApi.text_processing_api import PerReview, EachEatery, DoClusters
from ProductionEnvironmentApi.text_processing_db_scripts import MongoScriptsReviews, MongoScriptsEateries,\
        MongoScriptsDoClusters, MongoScripts

from ProductionEnvironmentApi.prod_heuristic_clustering import ProductionHeuristicClustering
from ProductionEnvironmentApi.join_two_clusters import ProductionJoinClusters
from ProductionEnvironmentApi.elasticsearch_db import ElasticSearchScripts
from Text_Processing.NounPhrases.noun_phrases import NounPhrases

from GlobalAlgorithmNames import TAG_CLASSIFIER_LIB, SENTI_CLASSIFIER_LIB, FOOD_SB_TAG_CLASSIFIER_LIB,\
            COST_SB_TAG_CLASSIFIER_LIB, SERV_SB_TAG_CLASSIFIER_LIB, AMBI_SB_TAG_CLASSIFIER_LIB, FOOD_SUB_TAGS,\
            COST_SUB_TAGS, SERV_SUB_TAGS, AMBI_SUB_TAGS

class QueryResolution(object):
        def __init__(self, text):
                self.text = "Green Apple Mojito – The bar at HRC is huge and we decided to order the Green Apple Mojito from the ‘Summer’s of the Legends’ Menu. The drink was made from green apples along with Mint. The taste was refreshing. 8/10 Red Hot Chili Fried – Crispy fries with sweet and chili sauce. The fries are topped with cheddar cheese. The dish is served with a portion of tangy salsa dip and cheesy dip. The cheesy dip was so-so and didn’t have any particular flavors. The portion size of this dish was huge and a little more sweet and chili sauce would have been\
                        icing on the cake. 8/10"
                self.tokenized_sents, self.food_sents, self.serv_sents,\
                self.cost_sents, self.ambi_sents = [], [], [], [], []


                self.food_sub_sents, self.serv_sub_sents, self.ambi_sub_sents,\
                self.cost_sub_sents = [], [], [], []

                self.sentence_tokenization()
                self.classification()
                self.food_sub_classification()
                self.ambience_sub_classification()
                self.cost_sub_classification()
                self.service_sub_classification()
                self.initiate_dictionaries()


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
                food_dictionary = dict.fromkeys(FOOD_SUB_TAGS, [])
                print food_dictionary
                print self.food_sub_sents
                for sent, sub_tag in self.food_sub_sents:
                    print sent, sub_tag     
                    sentences = food_dictionary.get(sub_tag)
                    sentences.append(sent)
                    print sub_tag, sentences
               
                """
                        sentences = food_dictionary.get(sub_tag)
                        sentences.append(sent)
                        food_dictionary.update({sub_tag: sentences})
                        print food_dictionary          
                """
                for key, value in food_dictionary.iteritems():
                    print key, value, "\n"

                #cost_dictionary = dict.fromkeys(COST_SUB_TAGS)
                #service_dictionary = dict.fromkeys(SERV_SUB_TAGS)
                #ambience_dictionary = dict.fromkeys(AMBI__SUB_TAGS)


        def noun_phrase_extraction(self):
                """
                """
                __nouns = NounPhrases([e[0] for e in self.all_food], default_np_extractor=NOUN_PHSE_ALGORITHM_NAME)
                self.all_food_with_nps = [[sent, tag, sentiment, sub_tag, nps] for ((sent, tag, sentiment, sub_tag,), nps) in 
                        zip(self.all_food, __nouns.noun_phrases[NOUN_PHSE_ALGORITHM_NAME])] 
                map(lambda __list: __list.append(self.review_time), self.all_food_with_nps) 


            
if __name__ == "__main__":
        QueryResolution(None)
