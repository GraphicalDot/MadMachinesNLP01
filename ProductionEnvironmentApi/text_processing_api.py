#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
Author: kaali
Dated: 15 April, 2015
Purpose:
    This file has been written to list all the sub routines that might be helpful in generating result for 
    get_word_cloud api

"""
import time
import os
from sys import path
import itertools
import warnings
from sklearn.externals import joblib
from collections import Counter
from text_processing_db_scripts import MongoScripts, MongoScriptsEateries, MongoScriptsReviews, MongoScriptsDoClusters
from prod_heuristic_clustering import ProductionHeuristicClustering
from join_two_clusters import ProductionJoinClusters

parent_dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path.append(parent_dir_path)

from Text_Processing.Sentence_Tokenization.Sentence_Tokenization_Classes import SentenceTokenizationOnRegexOnInterjections
from Text_Processing.NounPhrases.noun_phrases import NounPhrases
from Text_Processing.Word_Tokenization.word_tokenizer import WordTokenize
from Text_Processing.PosTaggers.pos_tagging import PosTaggers
from Text_Processing.MainAlgorithms.paths import path_parent_dir, path_in_memory_classifiers
from Text_Processing.NER.ner import NERs
from Text_Processing.colored_print import bcolors
from Text_Processing.MainAlgorithms.Algorithms_Helpers import get_all_algorithms_result
from Text_Processing.MainAlgorithms.In_Memory_Main_Classification import timeit, cd
from encoding_helpers import SolveEncoding



from GlobalAlgorithmNames import TAGS
#Algortihms of the form .lib
from GlobalAlgorithmNames import TAG_CLASSIFIER, SENTI_CLASSIFIER, FOOD_SB_TAG_CLASSIFIER,\
        COST_SB_TAG_CLASSIFIER, SERV_SB_TAG_CLASSIFIER, AMBI_SB_TAG_CLASSIFIER 
      
#Name of the algortihms      
from GlobalAlgorithmNames import NOUN_PHSE_ALGORITHM_NAME, TAG_CLASSIFY_ALG_NME, SENTI_CLSSFY_ALG_NME,\
        FOOD_SB_CLSSFY_ALG_NME, SERV_SB_CLSSFY_ALG_NME, AMBI_SB_CLSSFY_ALG_NME, COST_SB_CLSSFY_ALG_NME

##Actual libraries loaded by joblib.load
from GlobalAlgorithmNames import TAG_CLASSIFIER_LIB, SENTI_CLASSIFIER_LIB, FOOD_SB_TAG_CLASSIFIER_LIB,\
        COST_SB_TAG_CLASSIFIER_LIB , SERV_SB_TAG_CLASSIFIER_LIB, AMBI_SB_TAG_CLASSIFIER_LIB 


from GlobalAlgorithmNames import SENTIMENT_TAGS,  AMBI_SUB_TAGS, SERV_SUB_TAGS, COST_SUB_TAGS, FOOD_SUB_TAGS


class EachEatery:
        def __init__(self, eatery_id):
                self.eatery_id = eatery_id
                self.mongo_eatery_instance = MongoScriptsEateries(self.eatery_id)
        
        def return_non_processed_reviews(self, start_epoch=None, end_epoch=None):
                """
                If there is a change in algortihms or a new eatery to be processed
                we run processing all the reviews independent of the start_epoch and
                end_epoch, which means whenever there is change all the revviews will
                be present in processed_reviews list of eatery unless celery fails to
                process all, in case of some internal error
                This method treats an existing eatery with old algorithms set and an all together 
                New eatery as equal, In both the cases eatery will be update by set_new_algorithms
                method
                """
                if not self.mongo_eatery_instance.check_algorithms():
                        self.mongo_eatery_instance.empty_processed_reviews_list()
                        self.mongo_eatery_instance.set_new_algorithms() ##This will insert the eatery if not present
                        self.mongo_eatery_instance.empty_noun_phrases()
                        self.mongo_eatery_instance.empty_old_considered_ids()
            
                        return MongoScriptsReviews.return_all_reviews_with_text(self.eatery_id)

                else:
                        all_reviews = MongoScriptsReviews.return_all_reviews(self.eatery_id) 
                        all_processed_reviews = self.mongo_eatery_instance.get_proccessed_reviews()

                        ##This if True means that the database has some new reviews added to it, 
                        ##which needs processing, so MongoScriptsReviews.reviews_with_text 
                        #returns (review_id, review_text) for every review_id
                        if bool(set.symmetric_difference(set(all_processed_reviews), set(all_reviews))):
                                warnings.warn("{0} we encountered new reviews in the database {1}".format(\
                                        bcolors.FAIL, bcolors.RESET))
                                
                                try:
                                        reviews_ids = list(set.symmetric_difference(set(all_reviews), set(all_processed_reviews)))
                                        return MongoScriptsReviews.reviews_with_text(reviews_ids)
                                #This means that all_processed_reviews is empty, which means all the reviews
                                ##needs processing 
                                except TypeError as e:
                                        warnings.warn("{0} It seems none of the review has been processed yet {1}".format(\
                                        bcolors.FAIL, bcolors.RESET))
                
                                        return MongoScriptsReviews.reviews_with_text(all_reviews)
                        
                        
                        warnings.warn("{0} No New reviews to be considered {1}".format(\
                                        bcolors.OKBLUE, bcolors.RESET))
                        return False 

class PerReview:
        sent_tokenizer = SentenceTokenizationOnRegexOnInterjections()
        def __init__(self, review_id, review_text, review_time, eatery_id):
                
                self.review_id, self.review_text, self.review_time, self.eatery_id = review_id, \
                        review_text, review_time, eatery_id

        def print_execution(func):
                "This decorator dumps out the arguments passed to a function before calling it"
                argnames = func.func_code.co_varnames[:func.func_code.co_argcount]
                fname = func.func_name
                def wrapper(*args,**kwargs):
                        start_time = time.time()
                        print "{0} Now {1} have started executing {2}".format(bcolors.OKBLUE, func.func_name, bcolors.RESET)
                        result = func(*args, **kwargs)
                        print "{0} Total time taken by {1} for execution is --<<{2}>>--{3}\n".format(bcolors.OKGREEN, func.func_name, 
                                (time.time() - start_time), bcolors.RESET)
                        
                        return result
                return wrapper
        
        def get_args(self):
                print self.__dict__
        

        @print_execution
        def run(self):
                """
                It returns the result
                """

                result = self.__get_review_result()
                print "this is the result %s"%result
                if not bool(result):
                        print "{0}Result for the review_id --<<{1}>>-- has alredy been found{2}".format(bcolors.OKBLUE, \
                                self.review_id, bcolors.RESET)
                        return 


                if result.get("rerun_food_sub_tag_classification"):

                        print "{0}Doing FOOD sub classification again for review_id --<<{1}>>-- {2}".format(bcolors.OKBLUE, \
                                self.review_id, bcolors.RESET)
                        self.food = MongoScripts.get_tag_sentences(self.review_id, "food")
                        self.__food_sub_tag_classification()
                        self.__extract_noun_phrases() #makes self.noun_phrases
                        MongoScripts.update_food_sub_tag_sentences(self.review_id, self.all_food_with_nps)
               

                if result.get("rerun_cost_sub_tag_classification"):
                        print "{0}Doing COST sub classification again for review_id --<<{1}>>-- {2}".format(bcolors.OKBLUE, \
                                self.review_id, bcolors.RESET)
                        self.cost = MongoScripts.get_tag_sentences(self.review_id, "cost")
                        
                        self.__cost_sub_tag_classification()
                        MongoScripts.update_cost_sub_tag_sentences(self.review_id, self.all_cost)


                if result.get("rerun_service_sub_tag_classification"):
                        print "{0}Doing SERVICE sub classification again for review_id --<<{1}>>-- {2}".format(bcolors.OKBLUE, \
                                self.review_id, bcolors.RESET)
                        self.service = MongoScripts.get_tag_sentences(self.review_id, "service")
                        self.__service_sub_tag_classification()
                        MongoScripts.update_service_sub_tag_sentences(self.review_id, self.all_service)

                if result.get("rerun_ambience_sub_tag_classification"):
                        print "{0}Doing AMBIENCE sub classification again for review_id --<<{1}>>-- {2}".format(bcolors.OKBLUE, \
                                self.review_id, bcolors.RESET)
                        self.ambience = MongoScripts.get_tag_sentences(self.review_id, "ambience")
                        self.__ambience_sub_tag_classification()
                        MongoScripts.update_ambience_sub_tag_sentences(self.review_id, self.all_ambience)
                        

                if result.get("rerun_noun_phrases"):
                        print "{0}Doing noun phrases again for review_id --<<{1}>>-- {2}".format(bcolors.OKBLUE, \
                                self.review_id, bcolors.RESET)
                        
                        self.food = MongoScripts.get_tag_sentences(self.review_id, "food")
                        self.__food_sub_tag_classification()
                        self.__extract_noun_phrases() #makes self.noun_phrases
                        MongoScripts.update_noun_phrases(review_id, self.all_food_with_nps)
        


                if result.get("rerun_all_algorithms"):
                        print "{0} No results found for review id --<<{1}>>--{2}".format(bcolors.FAIL, \
                                self.review_id, bcolors.RESET)
                        self.__sent_tokenize_review() #Tokenize reviews, makes self.reviews_ids, self.sentences
                        self.__predict_tags()          #Predict tags, makes self.predict_tags
                        self.__predict_sentiment() #makes self.predicted_sentiment

                        self.all_sent_tag_sentiment = zip(self.sentences, self.tags, self.sentiments)
                
                        self.__filter_on_category() #generates self.food, self.cost, self.ambience, self.service
                

                        self.__food_sub_tag_classification()
                        self.__service_sub_tag_classification()
                        self.__cost_sub_tag_classification()
                        self.__ambience_sub_tag_classification()

                        self.__extract_noun_phrases() #makes self.noun_phrases
                        self.__update_review_result()
                
                MongoScripts.update_processed_reviews_list(self.eatery_id, self.review_id)
                return 

        

        @print_execution
        def __food_sub_tag_classification(self):
                """
                This deals with the sub classification of fodd sub tags
                """
                self.food_sub_tags = FOOD_SB_TAG_CLASSIFIER_LIB.predict([__e[0] for __e in self.food])
                self.all_food = [[sent, tag, sentiment, sub_tag] for ((sent, tag, sentiment), sub_tag)\
                        in zip(self.food, self.food_sub_tags)]

                return  

        @print_execution
        def __service_sub_tag_classification(self):
                """
                This deals with the sub classification of fodd sub tags
                """
                self.service_sub_tags = SERV_SB_TAG_CLASSIFIER_LIB.predict([__e[0] for __e in self.service])
                self.all_service = [[sent, tag, sentiment, sub_tag] for ((sent, tag, sentiment), sub_tag) \
                        in zip(self.service, self.service_sub_tags)]
                
                map(lambda __list: __list.append(self.review_time), self.all_service)
                return 

        @print_execution
        def __cost_sub_tag_classification(self):
                """
                This deals with the sub classification of cost sub tags
                
                self.all_cost = [(sent, "cost", sentiment, "cost-overall",), .....]
                """

                self.cost_sub_tags = COST_SB_TAG_CLASSIFIER_LIB.predict([__e[0] for __e in self.cost])
                self.all_cost = [[sent, tag, sentiment, sub_tag] for ((sent, tag, sentiment), sub_tag) \
                        in zip(self.cost, self.cost_sub_tags)]
                
                map(lambda __list: __list.append(self.review_time), self.all_cost)
                return

        @print_execution
        def __ambience_sub_tag_classification(self):
                """
                This deals with the sub classification of fodd sub tags
                """
                self.ambience_sub_tags = AMBI_SB_TAG_CLASSIFIER_LIB.predict([__e[0] for __e in self.ambience])
                self.all_ambience = [[sent, tag, sentiment, sub_tag] for ((sent, tag, sentiment), sub_tag) \
                        in zip(self.ambience, self.ambience_sub_tags)]
                
                map(lambda __list: __list.append(self.review_time), self.all_ambience)
                return 




        @print_execution
        def __sent_tokenize_review(self):
                """
                Tokenize self.reviews tuples of the form (review_id, review) to sentences of the form (review_id, sentence)
                and generates two lists self.review_ids and self.sentences
                """
                self.sentences = self.sent_tokenizer.tokenize(self.review_text)
                return
                       

        @print_execution
        def __predict_tags(self):
                """
                Predict tags of the sentence which were being generated by self.sent_tokenize_reviews
                """
                self.tags = TAG_CLASSIFIER_LIB.predict(self.sentences)
                return

        @print_execution
        def __predict_sentiment(self):
                """
                Predict sentiment of self.c_sentences which were made by filtering self.sentences accoring to 
                the specified category
                """
                self.sentiments = SENTI_CLASSIFIER_LIB.predict(self.sentences)
                return 
        


        @print_execution
        def __filter_on_category(self):
                 __filter = lambda tag, __list: [(sent, __tag, sentiment) for (sent, __tag, sentiment) in \
                                                                                    __list if __tag== tag ]


                 self.food, self.cost, self.ambience, self.service, self.null, self.overall = \
                         __filter("food", self.all_sent_tag_sentiment),  __filter("cost", self.all_sent_tag_sentiment),\
                         __filter("ambience", self.all_sent_tag_sentiment), __filter("service", self.all_sent_tag_sentiment),\
                         __filter("null", self.all_sent_tag_sentiment),  __filter("overall", self.all_sent_tag_sentiment)


        @print_execution
        def __extract_noun_phrases(self):
                """
                Extarct Noun phrases for the self.c_sentences for each sentence and outputs a list 
                self.sent_sentiment_nps which is of the form 
                [('the only good part was the coke , thankfully it was outsourced ', 
                                            u'positive', [u'good part']), ...]
                """
                __nouns = NounPhrases([e[0] for e in self.all_food], default_np_extractor=NOUN_PHSE_ALGORITHM_NAME)

                self.all_food_with_nps = [[sent, tag, sentiment, sub_tag, nps] for ((sent, tag, sentiment, sub_tag,), nps) in 
                        zip(self.all_food, __nouns.noun_phrases[NOUN_PHSE_ALGORITHM_NAME])]

                map(lambda __list: __list.append(self.review_time), self.all_food_with_nps)
                return 


        @print_execution
        def __get_review_result(self):
                result = MongoScripts.get_review_result(review_id = self.review_id) 
                return result 

        
        @print_execution
        def __update_review_result(self):
                MongoScripts.update_review_result_collection(
                        review_id = self.review_id, 
                        eatery_id = self.eatery_id, 
                        food = self.food,
                        cost = self.cost,
                        ambience = self.ambience,
                        null = self.null,
                        overall = self.overall,
                        service = self.service, 
                        food_result= self.all_food_with_nps, 
                        service_result = self.all_service, 
                        cost_result = self.all_cost, 
                        ambience_result = self.all_ambience, ) 
                return 


class DoClusters(object):
        """
        Does heuristic clustering for the all reviews
        """
        def __init__(self, eatery_id, category=None, with_sentences=False):
                self.eatery_id = eatery_id
                self.mongo_instance = MongoScriptsDoClusters(self.eatery_id)
                self.category = category
                mongo_eatery_instance= MongoScriptsEateries(self.eatery_id)
                self.eatery_name = mongo_eatery_instance.eatery_name

        def run(self):
                """
                Two cases:
                    Case 1:Wither first time the clustering is being run, The old_considered_ids list
                    is empty
                        case food:

                        case ["ambience", "cost", "service"]:
                            instance.fetch_reviews(__category) fetch a list of this kind
                            let say for ambience [["positive", "ambience-null"], ["negative", "decor"], 
                            ["positive", "decor"]...]
                            
                            DoClusters.make_cluster returns a a result of the form 
                                [{"name": "ambience-null", "positive": 1, "negative": 2}, ...]

                            After completing it for all categories updates the old_considered_ids of 
                            the eatery with the reviews

                    Case 2: None of processed_reviews and old_considered_ids are empty
                        calculates the intersection of processed_reviews and old_considered_ids
                        which implies that some review_ids in old_considered_ids are not being 
                        considered for total noun phrases
                        
                        Then fecthes the review_ids of reviews who are not being considered for total
                        noun phrases 

                        instance.fetch_reviews(__categoryi, review_ids) fetch a list of this kind
                            let say for ambience [["positive", "ambience-null"], ["negative", "decor"], 
                            ["positive", "decor"]...]

                """

                old_considered_ids = self.mongo_instance.old_considered_ids()
                if not old_considered_ids:
                        #That clustering is running for the first time
                        warnings.warn("{0} No clustering of noun phrases has been done yet {1}".format(\
                                    bcolors.FAIL, bcolors.RESET))
                        
                        __nps_food = self.mongo_instance.fetch_reviews("food")
                        
                        ##sub_tag_dict = {u'dishes': [[u'super-positive', 'sent', [u'paneer chilli pepper starter']],
                        ##[u'positive', sent, []],
                        ##u'menu-food': [[u'positive', sent, []]], u'null-food': [[u'negative', sent, []],
                        ##[u'negative', sent, []],
                        sub_tag_dict = DoClusters.unmingle_food_sub(__nps_food)

                        for sub_category in ["dishes", "place-food", "sub-food"]:
                                __result = self.clustering(sub_tag_dict.get(sub_category), sub_category)
                                self.mongo_instance.update_food_sub_nps(__result, sub_category)
                        
                        for sub_category in ["menu-food", "overall-food"]:
                                #REsult corresponding to the menu-food tag
                                __result = DoClusters.aggregation(sub_tag_dict.get(sub_category))
                                self.mongo_instance.update_food_sub_nps(__result, sub_category)
                        


                        for __category in ["ambience", "service", "cost"]:
                                __nps = self.mongo_instance.fetch_reviews(__category)
                                __whle_nps = DoClusters.make_cluster(__nps, __category)
                                
                                self.mongo_instance.update_nps(__category, __whle_nps)
                        
                        self.mongo_instance.update_considered_ids()
                else:
                        
                        processed_reviews = self.mongo_instance.processed_reviews()
                        reviews_ids = list(set.symmetric_difference(set(old_considered_ids), \
                                set(processed_reviews)))

                        print "These are the review ids required to be considered %s"%reviews_ids

                        if not bool(reviews_ids):
                                warnings.warn("{0} All the noun phrases has already been processed {1}".format(\
                                    bcolors.OKBLUE, bcolors.RESET))
                                return 

                        MongoScriptsDoClusters.reviews_with_time(reviews_ids)
                        __nps_food = self.mongo_instance.fetch_reviews("food", reviews_ids)
                            
                            
                        ##{u'dishes': [[u'positive', sent, [u'paneer chilli pepper starter']],
                        ##[u'positive', sent, []],
                        ##u'menu-food': [[u'positive', sent, []]], u'null-food': [[u'negative', sent, []],
                        ##[u'negative', sent, []],
                        sub_tag_dict = DoClusters.unmingle_food_sub(__nps_food)

                        for sub_category in ["dishes", "place-food", "sub-food"]:
                                #deals with clustering in ProductionHeuristicClustering
                                __nps_new_result = self.clustering(sub_tag_dict.get(sub_category), sub_category)
                                #old noun phrases stored already in mongodbunder food.sub_category
                                __nps_old_result = self.mongo_instance.fetch_nps_frm_eatery("food", sub_category)
                                
                                
                                print  "This is the new result"
                                print __nps_new_result
                                print  "Enfind printing new result"
                                __whle = __nps_old_result + __nps_new_result
                                __whle_result = self.join_two_clusters(__whle, sub_category)
                                self.mongo_instance.update_food_sub_nps(__whle_result, sub_category)
                        
                        for sub_category in ["menu-food", "overall-food"]:
                                #REsult corresponding to the menu-food tag
                                __nps_new_result = DoClusters.aggregation(sub_tag_dict.get(sub_category))
                                __nps_old_result = self.mongo_instance.fetch_nps_frm_eatery("food", sub_category)
                    
                                __whl_new_result = DoClusters.aggregation(__nps_old_result, __nps_new_result)
                                self.mongo_instance.update_food_sub_nps(__whl_new_result, sub_category)
                        

                                        

                        for __category in ["ambience", "service", "cost"]:
                                __nps = self.mongo_instance.fetch_reviews(__category, reviews_ids)
                                __nps_new_result = DoClusters.make_cluster(__nps, __category)

                                __nps_old_result = self.mongo_instance.fetch_nps_frm_eatery(__category)
                                __whle_nps = DoClusters.adding_new_old_nps(__nps_old_result, __nps_new_result)
                                
                                self.mongo_instance.update_nps(__category, __whle_nps)
                        
                        self.mongo_instance.update_considered_ids(review_list=reviews_ids)

                return 


        def join_two_clusters(self, __list, sub_category):
                clustering_result = ProductionJoinClusters(__list)
                return clustering_result.run()
                    


        def clustering(self, __sent_sentiment_nps_list, sub_category):
                """
                Args __sent_sentiment_nps_list:
                        [
                        (u'positive', [u'paneer chilli pepper starter'], u'2014-09-19 06:56:42'),
                        (u'positive', [u'paneer chilli pepper starter'], u'2014-09-19 06:56:42'),
                        (u'positive', [u'paneer chilli pepper starter'], u'2014-09-19 06:56:42'),
                         (u'neutral', [u'chicken pieces', u'veg pasta n'], u'2014-06-20 15:11:42')]  

                Result:
                    [
                    {'name': u'paneer chilli pepper starter', 'positive': 3, 'timeline': 
                    [(u'positive', u'2014-09-19 06:56:42'), (u'positive', u'2014-09-19 06:56:42'), 
                    (u'positive', u'2014-09-19 06:56:42')], 'negative': 0, 'super-positive': 0, 'neutral': 0, 
                    'super-negative': 0, 'similar': []}, 
                    
                    {'name': u'chicken pieces', 'positive': 0, 'timeline': 
                    [(u'neutral', u'2014-06-20 15:11:42')], 'negative': 0, 'super-positive': 0, 
                    'neutral': 1, 'super-negative': 0, 'similar': []}
                    ]
                """
                if not bool(__sent_sentiment_nps_list):
                        return list()

                ##Removing (sentiment, nps) with empyt noun phrases
                __sentiment_np_time = [(sentiment, nps, review_time) for (sentiment, sent, nps, review_time) \
                        in __sent_sentiment_nps_list if nps]
                
                __sentences = [sent for (sentiment, sent, nps, review_time) in __sent_sentiment_nps_list if nps]
                clustering_result = ProductionHeuristicClustering(sentiment_np_time = __sentiment_np_time,
                                                                sub_category = sub_category,
                                                                sentences = __sentences,
                                                                eatery_name= self.eatery_name)
                return clustering_result.run()



        @staticmethod
        def aggregation(old, new=None):
                """
                __list can be either menu-food, overall-food,
                as these two lists doesnt require clustering but only aggreation of sentiment analysis
                Args:
                    case1:[ 
                        [u'negative', u'food is average .', [], u'2014-09-19 06:56:42'],
                        [u'negative', u"can't say i tasted anything that i haven't had before .", [u'i haven'],
                        u'2014-09-19 06:56:42'],
                        [u'negative', u"however , expect good food and you won't be disappointed .", [],
                        u'2014-09-19 06:56:42'],
                        [u'neutral', u'but still everything came hot ( except for the drinks of course ', [],
                        u'2014-09-19 06:56:42'],
                        ] 
                    
                    case1: output
                        {u'negative': 5, u'neutral': 1, u'positive': 2, u'super-positive': 1,
                        'timeline': [(u'super-positive', u'2014-04-05 12:33:45'), (u'positive', u'2014-05-06 13:06:56'),
                        (u'negative', u'2014-05-25 19:24:26'), (u'negative', u'2014-05-25 19:24:26'),
                        (u'positive', u'2014-06-09 16:28:09'), (u'negative', u'2014-09-19 06:56:42'),
                        (u'negative', u'2014-09-19 06:56:42'), (u'negative', u'2014-09-19 06:56:42'),
                        (u'neutral', u'2014-09-19 06:56:42')]}


                    case2: When aggregation has to be done on old and new noun phrases 
                        old: {"super-positive": 102, "super_negative": 23, "negative": 99, 
                                "positive": 76, "neutral": 32}
                        new as same as case1:
                        new: {"super-positive": 102, "super_negative": 23, "negative": 99, 
                                "positive": 76, "neutral": 32}
                    

                Result:
                    {u'negative': 4, u'neutral': 2}
                """
                if not bool(old):
                        sentiment_dict = dict()
                        [sentiment_dict.update({key: 0}) for key in SENTIMENT_TAGS]
                        sentiment_dict.update({"timeline": list()})
                        sentiment_dict.update({"total_sentiments": 0})
                        return sentiment_dict

                print "Printind old and new"
                print old
                print new
                print "finished Printind old and new"

                sentiment_dict = dict()
                if new :
                        [sentiment_dict.update({key: (old.get(key) + new.get(key))}) for key in SENTIMENT_TAGS] 
                        #this statement ensures that we are dealing with case 1
                        sentiment_dict.update({"timeline": sorted((old.get("timeline") + new.get("timeline")), key= lambda x: x[1] )})
                        sentiment_dict.update({"total_sentiments": old.get("total_sentiments")+ new.get("total_sentiments")})
                        return sentiment_dict


                filtered_sentiments = Counter([sentiment for (sentiment, sent, nps, review_time) in old])
                timeline = sorted([(sentiment, review_time) for (sentiment, sent, nps, review_time) in old], key=lambda x: x[1])
               
                def convert(key):
                        if filtered_sentiments.get(key):
                                return {key: filtered_sentiments.get(key) }
                        else:
                                return {key: 0}


                [sentiment_dict.update(__dict) for __dict in map(convert,  SENTIMENT_TAGS)]
                sentiment_dict.update({"timeline": timeline})
                total = sentiment_dict.get("positive") + sentiment_dict.get("negative") + sentiment_dict.get("neutral") + sentiment_dict.get("super-negative")\
                                    +sentiment_dict.get("super-positive")

                sentiment_dict.update({"total_sentiments": total})
                return sentiment_dict


        @staticmethod
        def unmingle_food_sub(__list):
                """
                __list = [u'the panner chilly was was a must try for the vegetarians from the menu .', 
                u'food', u'positive', u'menu-food',[]],
                [u'and the Penne Alfredo pasta served hot and good with lots of garlic flavours which 
                we absolute love .', u'food',cu'super-positive',u'dishes', [u'garlic flavours', 
                u'penne alfredo pasta']],

                result:
                    {u'dishes': [[u'positive', 'sent', [u'paneer chilli pepper starter'], '2014-09-19 06:56:42'],
                                [u'positive', 'sent', [], '2014-09-19 06:56:42'],
                                [u'positive', sent, [u'friday night'], '2014-09-19 06:56:42'],
                                [u'positive', sent, [], '2014-09-19 06:56:42'],
                                [u'positive', sent, [], '2014-09-19 06:56:42'],
                                [u'super-positive', sent, [u'garlic flavours', u'penne alfredo pasta']]],
                    u'menu-food': [[u'positive', sent, [], u'2014-06-09 16:28:09']],
                    u'null-food': [[u'negative', sent, [], u'2014-06-09 16:28:09'],
                                [u'super-positive', sent, [], '2014-09-19 06:56:42'],
                                [u'super-positive', sent, [], '2014-09-19 06:56:42'],
                                [u'negative', sent, [], '2014-09-19 06:56:42'],
                                }
                """
                __sub_tag_dict = dict()
                for (sent, tag, sentiment, sub_tag, nps, review_time)  in __list:
                        if not __sub_tag_dict.has_key(sub_tag):
                                __sub_tag_dict.update({sub_tag: [[sentiment, sent, nps, review_time]]})
                        
                        else:
                            __old = __sub_tag_dict.get(sub_tag)
                            __old.append([sentiment, sent, nps, review_time])
                            __sub_tag_dict.update({sub_tag: __old})

                return __sub_tag_dict

        @staticmethod
        def make_cluster(__nps, __category):
                """
                args:
                    __nps : [[u'super-positive', u'ambience-overall', u'2014-09-19 06:56:42'],
                            [u'neutral', u'ambience-overall', u'2014-09-19 06:56:42'],
                            [u'positive', u'open-area', u'2014-09-19 06:56:42'],
                            [u'super-positive', u'ambience-overall', u'2014-08-11 12:20:18'],
                            [u'positive', u'decor', u'2014-04-05 12:33:45'],
                            [u'super-positive', u'decor', u'2014-05-06 18:50:17'],
                
                return:
                        [{'name': u'decor', u'positive': 1, "timeline": },
                        {'name': u'ambience-overall', u'neutral': 1, u'super-positive': 2,"timeline"
                                :  [('super-positive','2014-09-19 06:56:42'), ("super-positive": '2014-08-11 12:20:18')]}]
                    
                """
                nps_dict = DoClusters.make_sentences_dict(__nps, __category)
                result = [DoClusters.flattening_dict(key, value) for key, value in nps_dict.iteritems()]
                return result

        @staticmethod
        def adding_new_old_nps(__new, __old):
                """
                __new: [{'name': u'decor', u'super-positive': 1, "negative": 3, "total_sentiment": 4 , "timeline": [(u'negative', u'2014-09-19 06:56:42'),
                  (u'negative', u'2014-09-19 06:56:42'), (u'neutral', u'2014-09-19 06:56:42')]}, 
                  
                  {'name': u'ambience-null', u'positive': 1, "total_sentiments": 1, "timeline": [(u'negative', u'2014-09-19 06:56:42')]},

                __old: [{'name': u'music', u'super-positive': 1, "timeline": []}, {'name': u'ambience-null', u'neutral': 1, "super-negative": 10}, 
                {'name': u'ambience-overall', u'neutral': 1, u'super-positive': 2},
                """
                aggregated_list = list()

                        
                def make_dict(__list):
                        new_dict = dict()
                        for __dict in __list:
                                name = __dict.get("name")
                                __dict.pop("name")
                                new_dict.update({name: __dict})
                        return new_dict

                __new_dict = make_dict(__new)
                __old_dict = make_dict(__old)

                keys = set.union(set(__old_dict.keys()), set(__new_dict.keys()))
                for key in keys:
                        a = Counter(__new_dict.get(key))
                        b = Counter(__old_dict.get(key))
                        sentiments = dict(a+b)
                        sentiments.update({"name": key})
                        aggregated_list.append(sentiments)

                return aggregated_list

        @staticmethod
        def flattening_dict(key, value):
                """
                key: ambience-overall 
                value: 
                    {'sentiment': [u'super-positive',u'neutral', u'super-positive', u'neutral', u'neutral'],
                    'timeline': [(u'super-positive', u'2014-09-19 06:56:42'), (u'neutral', u'2014-09-19 06:56:42'),
                            (u'super-positive', u'2014-08-11 12:20:18'), (u'neutral', u'2014-05-06 13:06:56'),
                            (u'neutral', u'2014-05-06 13:06:56')]},


                Output: 
                    {'name': u'ambience-overall', u'neutral': 3, u'super-positive': 2, 
                'timeline': [(u'neutral', u'2014-05-06 13:06:56'), (u'neutral', u'2014-05-06 13:06:56'),
                (u'super-positive', u'2014-08-11 12:20:18'), (u'super-positive', u'2014-09-19 06:56:42'),
                (u'neutral', u'2014-09-19 06:56:42')]},

                """
                __dict = dict()
                sentiments = Counter(value.get("sentiment"))
                def convert(key):
                        if sentiments.get(key):
                                return {key: sentiments.get(key) }
                        else:
                                return {key: 0}


                [__dict.update(__sentiment_dict) for __sentiment_dict in map(convert, SENTIMENT_TAGS)]

                __dict.update({"name": key})
                __dict.update({"timeline": sorted(value.get("timeline"), key=lambda x: x[1] )})
                __dict.update({"total_sentiments": value.get("total_sentiments")})
                return __dict


        @staticmethod
        def make_sentences_dict(noun_phrases, category):
                """
                Input:
                    [[u'super-positive', u'ambience-overall', u'2014-09-19 06:56:42'],
                    [u'neutral', u'ambience-overall', u'2014-09-19 06:56:42'],
                    [u'positive', u'open-area', u'2014-09-19 06:56:42'],
                    [u'super-positive', u'ambience-overall', u'2014-08-11 12:20:18'],
                    [u'positive', u'decor', u'2014-04-05 12:33:45'],
                    [u'super-positive', u'decor', u'2014-05-06 18:50:17'],
                    [u'neutral', u'ambience-overall', u'2014-05-06 13:06:56'],
                    [u'positive', u'decor', u'2014-05-06 13:06:56'],
                    [u'positive', u'music', u'2014-05-06 13:06:56'],
                    [u'neutral', u'ambience-overall', u'2014-05-06 13:06:56']]
                
                Result:

                {ambience-overall: {
                                'sentiment': [u'super-positive',u'neutral', u'super-positive', u'neutral', u'neutral'],
                                'timeline': [(u'super-positive', u'2014-09-19 06:56:42'), (u'neutral', u'2014-09-19 06:56:42'),
                                            (u'super-positive', u'2014-08-11 12:20:18'), (u'neutral', u'2014-05-06 13:06:56'),
                                            (u'neutral', u'2014-05-06 13:06:56')]},
                
                ambience-null: {
                                'sentiment': [u'super-positive',u'neutral', u'super-positive', u'neutral', u'neutral'],
                                'timeline': [
                                        (u'super-positive', u'2014-09-19 06:56:42'), (u'neutral', u'2014-09-19 06:56:42'),
                                    (u'super-positive', u'2014-08-11 12:20:18'), (u'neutral', u'2014-05-06 13:06:56'),
                        }}

                """
                sentences_dict = dict()

                for sub_tag in eval("{0}_SUB_TAGS".format(category.upper()[0:4])):
                        for sentiment in SENTIMENT_TAGS:
                            sentences_dict.update({sub_tag: {"sentiment": list(), "timeline": list(), "total_sentiments": 0}})

                for __sentiment, __category, review_time in noun_phrases:
                        timeline = sentences_dict.get(__category).get("timeline")
                        timeline.append((__sentiment, review_time))
                        sentiment = sentences_dict.get(__category).get("sentiment")
                        sentiment.append(__sentiment)
                        total_sentiments = sentences_dict.get(__category).get("total_sentiments") +1 

                        sentences_dict.update({
                            __category: {"sentiment": sentiment, "timeline": timeline, "total_sentiments": total_sentiments}})
    
                
                        
                return sentences_dict
                """
                for __sentiment, __category, review_time in noun_phrases:
                        if not sentences_dict.has_key(__category):
                                sentences_dict.update({__category: {"sentiment": [__sentiment], \
                                        "timeline": [(__sentiment, review_time)]}})

                        else:
                                timeline = sentences_dict.get(__category).get("timeline")
                                timeline.append((__sentiment, review_time))
                                sentiment = sentences_dict.get(__category).get("sentiment")
                                sentiment.append(__sentiment)

                                sentences_dict.update({
                                    __category: {"sentiment": sentiment, "timeline": timeline}})



                left_out_sub_tgs = set.difference(set(eval("{0}_SUB_TAGS".format(category.upper()[0:4]))), set(sentences_dict.keys()))
                
                for sub_tag in left_out_sub_tags:
                        sentences_dict.update({sub_tag: {"sentiment": None, "timeline": []}})

                return sentences_dict
                """

if __name__ == "__main__":
        """
        14 599
        1 3239
        4 309576
        5 5586
        98 9784
        42 3425
        47 303574
        62 307801
        820 218cdcf7214b3ea1ba6ce89e7d37ef9a
        84 8511e15af9b6379ba951b627a323a0eb
        """
        review_id = '3320891'
        review_text = "Visited the place for a friend's birthday bash. Lots of people have written detailed reviews about this place. So am giving a quick short review:1. Ambience is great. They have divided the place into fine dining, disc, and outdoor lounge area. However the outdoor area is still covered by a makeshift tent like a large pavilion with numerous ACs running to keep the place cool.2. Food is average. Can't say I tasted anything that I haven't had before. However, expect good food and you won't be disappointed. Do try their Paneer Chilli Pepper starter. Pizzas and risotto too was good.3. Drinks - here is an interesting (read weird) fact..even through they have numerous drinks in the menu, on a Friday night (when I visited the place) they were serving only specific brands of liquor. And way above even twice the MRP per bottle. So do make sure you carry a fat wallet if you are gonna drink.4. Service was good. A little slow but still everything came hot (except for the drinks of course!! ;)...but I guess the slow speed was due to the crowd present on a Friday night.And finally, if you are now planning to go (which I wouldn't say no to) do ensure you make a reservation. They DO NOT entertain without a reservation.Hope this was useful. Bon Appetit! :))"
        review_time = '2014-09-19 06:56:42'


        eatery_id = "8511e15af9b6379ba951b627a323a0eb"
        ins = EachEatery(eatery_id=eatery_id)
    
        try:
                for review_id, review_text, review_time in ins.return_non_processed_reviews():
                        per_review_instance = PerReview(review_id, review_text, review_time, eatery_id)
                        per_review_instance.run()
        except Exception:
                print "No review to be processed"
                pass

        do_cluster_ins = DoClusters(eatery_id=eatery_id)
        do_cluster_ins.run()

