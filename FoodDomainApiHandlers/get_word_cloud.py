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
from heuristic_clustering import HeuristicClustering

    
from sklearn.externals import joblib
from collections import Counter


class GetWordCloudApiHelper:
        def __init__(self, **kwargs):
                """
                Kwargs:
                    reviews: A list of tuples with first element as review_id and second element being review_text

                Class variables:
                        self.review_ids: 
                                All the review ids that belong to eatery_id which lies between start_epoch and end_epoch
                        self.sentences:
                                sentences that were generated after sentence tokenization of the reviews, mentioned
                                above
                        
                        self.tag_classifier:
                                tag classifier being loaded from InMemoryClassifiers depending upon the algortihm
                                being given to this class in kwargs

                        self.sentiment_classifier
                                sentiment classifier being loaded from InMemoryClassifiers depending upon the algortihm
                                being given to this class in kwargs

                        self.filtered_list:
                                a list to tuple of the form (review_id, sentence, tag)
                                which was filtered according to the category

                        self.c_review_ids, self.c_sentences, self.c_predicted_sentiment, self.c_predicted_tags:
                                type list
                                form:
                                    review_ids, sentences, predicted_sentiment, predicted_tags for the sentences
                                    who belongs to self.category
                        
                        self.noun_phrases: 
                                type list of list
                                Form:
                                    [noun_phrase, sentiment], [noun_phrase, sentiment], .....
                                 Example:
                                    [["ferror rocher shake", "super-positive"], ["basil sauce", "super-negative"], ...]
                        
                        self.normalized_noun_phrases: 
                                type list of list
                                same as self.noun_phrases except it doesnt have sentiments starting with super, they
                                have been normalized
                                Form:
                                    [noun_phrase, sentiment], [noun_phrase, sentiment], .....
                                 Example:
                                    [["ferror rocher shake", "positive"], ["basil sauce", "negative"], ...]
                                 
                        self.non_duplicate_nps: 
                                type list of lists
                                form:
                                    
                        
                        sorted_non_duplicate_nps: 
                                type list
                        
                        self.clustered_nps: 
                                type list
                """
                allowed_kwargs = ['reviews', 'eatery_name', 'category', 'total_noun_phrases', 'word_tokenization_algorithm_name', 
                        'noun_phrases_algorithm_name', 'pos_tagging_algorithm_name', 'tag_analysis_algorithm_name', 
                        'sentiment_analysis_algorithm_name', 'np_clustering_algorithm_name', 'ner_algorithm_name', 'with_celery']
                self.__dict__.update(kwargs)
                for kwarg in allowed_kwargs:
                        assert eval("self.{0}".format(kwarg)) != None
                
                self.sent_tokenizer = SentenceTokenizationOnRegexOnInterjections()
                self.tag_classifier = joblib.load("{0}/{1}".format(path_in_memory_classifiers, self.tag_analysis_algorithm_name))              
                self.sentiment_classifier = joblib.load("{0}/{1}".format(path_in_memory_classifiers,\
                                                        "svm_linear_kernel_classifier_sentiment_new_dataset.lib"))              
                
                
                self.sentences = list()
                c_review_ids, c_sentences, c_predicted_sentiment, c_predicted_tags = list(), list(), list(), list()
                self.noun_phrases = list()
                self.normalized_noun_phrases = list()
                self.non_duplicate_nps, sorted_non_duplicate_nps = list(), list()
                self.clustered_nps = list()
                self.normalized_sent_sentiment_nps = list()
        
        def get_args(self):
                print self.__dict__
        
        
        def run(self):
                """
                It returns the result
                """
                self.sent_tokenize_reviews() #Tokenize reviews, makes self.reviews_ids, self.sentences
                self.predict_tags()          #Predict tags, makes self.predict_tags
                        
                self.filtered_list = [e for e in zip(self.review_ids, self.sentences, self.predicted_tags) 
                                                                                if e[2] == self.category]

                if self.category == "cost":
                        self.cost_result = list()
                        classifier = joblib.load("{0}/{1}".format(path_in_memory_classifiers, 
                                                                "svm_linear_kernel_classifier_cost.lib"))
                       
                        review_ids, sentences, tags = zip(*self.filtered_list)
                        for cost_sub_category, frequency in Counter(classifier.predict(sentences)).items():
                                if cost_sub_category == "cost-null":
                                        pass
                                else:
                                        self.cost_result.append({"name": cost_sub_category,
                                                    "positive": frequency,
                                                    "negative": 0})
                        self.clustered_nps =  self.cost_result
                        return self.cost_result

                if self.category == "ambience":
                        self.ambience_result = list()
                        classifier = joblib.load("{0}/{1}".format(path_in_memory_classifiers, 
                                                        "svm_linear_kernel_classifier_ambience.lib"))
                        review_ids, sentences, tags = zip(*self.filtered_list)
                        for ambience_sub_category, frequency in Counter(classifier.predict(sentences)).items():
                                if ambience_sub_category == "ambience-null":
                                        pass
                                else:
                                        self.ambience_result.append({"name": ambience_sub_category,
                                                    "positive": frequency,
                                                    "negative": 0})
                        
                        self.clustered_nps = self.ambience_result
                        return self.ambience_result
                        

                self.predict_sentiment() #makes self.predicted_sentiment
                 
                ##New filtered list with sentiments included
                self.filtered_list = [e for e in zip(self.review_ids, self.sentences, self.predicted_tags, self.predicted_sentiment) 
                                            if e[2] == self.category]
                self.category_sentences() #makes c_review_ids, c_sentences, c_predicted_sentiment, c_predicted_tags
                self.extract_noun_phrases() #makes self.noun_phrases
                self.normalize_sentiments() #makes self.normalized_noun_phrases
                
                self.do_clustering() #makes self.clustered_nps
                return self.clustered_nps

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


        @print_execution
        def sent_tokenize_reviews(self):
                sentences = list()
                for review in self.reviews:
                        for __sentence in self.sent_tokenizer.tokenize(review[1]):
                                        __sentence = SolveEncoding.preserve_ascii(__sentence)
                                        sentences.append([review[0], __sentence])

                self.review_ids, self.sentences = zip(*sentences)
                return 
                        
        @print_execution
        def predict_tags(self):
                self.predicted_tags = self.tag_classifier.predict(self.sentences)
                return self.predicted_tags

        @print_execution
        def predict_sentiment(self):
                self.predicted_sentiment = self.sentiment_classifier.predict(self.sentences)
                return self.predicted_sentiment
        
        @print_execution
        def category_sentences(self):
                """
                break self.filtered_list which is the tuples specific to categories
                and generates c_review_ids, c_sentences, c_predicted_tags, c_predicted_sentiment
                MInd it, These are the category specific adn generated after filtering from all the sentences
                """
                self.c_review_ids, self.c_sentences, self.c_predicted_tags, self.c_predicted_sentiment = zip(*self.filtered_list)


        @print_execution
        def extract_noun_phrases(self):
                """
                self.sent_sentiment_nps = [('the only good part was the coke , thankfully it was outsourced ', 
                                            u'positive', [u'good part']), ...]
                """

                __nouns = NounPhrases(self.c_sentences, default_np_extractor=self.noun_phrases_algorithm_name)

                self.sent_sentiment_nps = [__tuple for __tuple in 
                        zip(self.c_sentences, self.c_predicted_sentiment, __nouns.noun_phrases[self.noun_phrases_algorithm_name])
                        if __tuple[2]]

                return self.sent_sentiment_nps 
        
        @print_execution
        def normalize_sentiments(self, ignore_super=False):
                """
                self.noun_phrases = [["ferror rocher shake", "positive"], ["basil sauce", "super-negative"], ...]
                Now, the above noun_phrases list has super-negative and super-positive sentiments associated with
                them,
                        ignore_super:
                                if True:
                                        super-positive and super-negative will be treated same as positive and negative
                                else:
                                        super-positive will consider as two positives,
                                        so for example: ["ferror rocher shake", "super-positive"]
                                        will have ["ferror rocher shake", "super-positive", "ferror rocher shake", "super-positive"]
                                        in new list
                for element in self.noun_phrases:
                        if element[0].startswith("super"):
                                self.normalized_noun_phrases.append((element[1], element[0].split("-")[1]))
                                if not ignore_super:
                                        self.normalized_noun_phrases.append((element[1], element[0].split("-")[1]))
                        else:
                                self.normalized_noun_phrases.append((element[1], element[0]))

                return self.normalized_noun_phrases
                """
                for (sentence, sentiment, noun_phrases) in self.sent_sentiment_nps:
                        __nouns = list()
                        if sentiment.startswith("super"):
                                sentiment = sentiment.split("-")[1]
                                __nouns.extend(noun_phrases)
                                if not ignore_super:
                                        __nouns.extend(noun_phrases)
                        else:
                                __nouns.extend(noun_phrases)
                        self.normalized_sent_sentiment_nps.append([sentence, sentiment, __nouns ])
                
                return self.normalized_sent_sentiment_nps




        @print_execution
        def do_clustering(self):
                __result = HeuristicClustering(self.normalized_sent_sentiment_nps, self.c_sentences, self.eatery_name)
                self.clustered_nps = sorted(__result.result, reverse=True, key= lambda x: x.get("positive")+x.get("negative"))
                return self.clustered_nps


        @print_execution
        def scores(self):
                __positive = sum([e.get("positive") for e in result])
                __negative = sum([e.get("negative") for e in result])

                def converting_to_percentage(__object):
                        i = (__object.get("positive")*__positive + __object.get("negative")*__negative)/(__positive+__negative)
                        __object.update({"likeness": '%.2f'%i})
                        return __object
                
        @print_execution
        def convert_sentences(__object):
                return {"sentence": __object[0],
                        "sentiment": __object[1]}
                                
                print map(converting_to_percentage, result)[0:30],
                

                """
                word_tokenize = WordTokenize(sentences,  default_word_tokenizer= word_tokenization_algorithm_name)
                word_tokenization_algorithm_result = word_tokenize.word_tokenized_list.get(word_tokenization_algorithm_name)


                __pos_tagger = PosTaggers(word_tokenization_algorithm_result,  default_pos_tagger=pos_tagging_algorithm_name)
                pos_tagging_algorithm_result =  __pos_tagger.pos_tagged_sentences.get(pos_tagging_algorithm_name)


                __noun_phrases = NounPhrases(pos_tagging_algorithm_result, default_np_extractor=noun_phrases_algorithm_name)
                noun_phrases_algorithm_result =  __noun_phrases.noun_phrases.get(noun_phrases_algorithm_name)

                #result = [element for element in zip(predicted_sentiment, noun_phrases_algorithm_result) if element[1]]
                result = [element for element in __result if element[1]]
                """

if __name__ == "__main__":
        GetWordCloudApiHelper(reviews= 0, total_noun_phrases= 20)
