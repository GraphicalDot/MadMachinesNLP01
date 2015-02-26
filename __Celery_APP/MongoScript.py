#-*- coding: utf-8 -*-
"""
Author: Kaali
Dated: 25 February, 2015
Purpose: This file deals with mongodb connections and also have functions
used by celery worket to input and output data

Whole point is there are two Mongodb databases hosted on different servers, One deals with all 
the data that has been scraped from websites and aggragated from xml, json api's of the websites.

The other databases deals with the results that has been accumulated by celery workers, The point
in making two different databses is, that a single database may not be able to handle hammering
both ways, getting reviews from scraping and then storing the results after running algorithms
on the reviews
"""
import os
import sys
import pymongo
file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(file_path)
from GlobalConfigs import MONGO_NLP_RESULTS_IP, MONGO_NLP_RESULTS_PORT, MONGO_NLP_RESULTS_DB, MONGO_NLP_RESULTS_COLLECTION
from Text_Processing import bcolors 

class MongoForCeleryResults:
        """
        This is the class which deals with the update, deletion and insertion of results
        returned by celery nodes after doing natural language processing on the reviews for a particular
        eatery
        """
        def __init__(self,):
                pass


        @staticmethod
        def update_insert_sentence(review_id, sentence_id, sentence):
                """
                Deals with update and deletion of the document
                """
                connection = pymongo.Connection(MONGO_NLP_RESULTS_IP, MONGO_NLP_RESULTS_PORT)
                result_collection = eval("connection.{db_name}.{collection_name}".format(
                                                                    db_name=MONGO_NLP_RESULTS_DB,
                                                                    collection_name=MONGO_NLP_RESULTS_COLLECTION)) 

                result_collection.update({"sentence_id": sentence_id,}, 
                                {"$set": {"review_id": review_id, "sentence": sentence,}},  upsert=True)
                connection.close()
                return

        @staticmethod
        def insert_word_tokenization_result(sentence_id, word_tokenization_algorithm_name, 
                                                            word_tokenization_algorithm_result):

                """
                Deals with the update and insert operation word_tokenization_algorithm_result of sentence 
                with sentence_id
                """
                connection = pymongo.Connection(MONGO_NLP_RESULTS_IP, MONGO_NLP_RESULTS_PORT)
                result_collection = eval("connection.{db_name}.{collection_name}".format(
                                                                    db_name=MONGO_NLP_RESULTS_DB,
                                                                    collection_name=MONGO_NLP_RESULTS_COLLECTION)) 

                result_collection.update({"sentence_id": sentence_id,}, {"$set": 
                                    {"word_tokenization.{0}".format(word_tokenization_algorithm_name): word_tokenization_algorithm_result}},  
                                    upsert=False)

                connection.close()
                return 
        
        @staticmethod
        def insert_pos_tagging_result(sentence_id, word_tokenization_algorithm_name,
                                                            pos_tagging_algorithm_name, 
                                                            pos_tagging_algorithm_result):

                """
                Deals with the update and insert operation pos_tagging_algorithm_result of sentence 
                with sentence_id
                """
                connection = pymongo.Connection(MONGO_NLP_RESULTS_IP, MONGO_NLP_RESULTS_PORT)
                result_collection = eval("connection.{db_name}.{collection_name}".format(
                                                                    db_name=MONGO_NLP_RESULTS_DB,
                                                                    collection_name=MONGO_NLP_RESULTS_COLLECTION)) 

                result_collection.update({"sentence_id": sentence_id,}, {"$set": 
                                    {"pos_tagging.{0}.{1}".format(pos_tagging_algorithm_name, word_tokenization_algorithm_name): 
                                        pos_tagging_algorithm_result}},  
                                    upsert=False)
                connection.close()
                return 
        
        @staticmethod
        def insert_noun_phrases_result(sentence_id, word_tokenization_algorithm_name,pos_tagging_algorithm_name, 
                                                    noun_phrases_algorithm_name, noun_phrases_algorithm_result):

                """
                Deals with the update and insert operation noun_phrases_algorithm_result of sentence 
                with sentence_id
                """
                connection = pymongo.Connection(MONGO_NLP_RESULTS_IP, MONGO_NLP_RESULTS_PORT)
                result_collection = eval("connection.{db_name}.{collection_name}".format(
                                                                    db_name=MONGO_NLP_RESULTS_DB,
                                                                    collection_name=MONGO_NLP_RESULTS_COLLECTION)) 
                result_collection.update({"sentence_id": sentence_id,}, {"$set": 
                                    {"noun_phrases.{0}.{1}.{2}".format(noun_phrases_algorithm_name, pos_tagging_algorithm_name, 
                                            word_tokenization_algorithm_name): noun_phrases_algorithm_result}},  
                                    upsert=False)
                connection.close()
                return 
        
        @staticmethod
        def insert_predictions(sentence_id, prediction_algorithm_name, tag, sentiment):

                """
                Deals with the update and insert operation of tag analysis algorithm results
                and sentiment analysis algorithm result
                """
                connection = pymongo.Connection(MONGO_NLP_RESULTS_IP, MONGO_NLP_RESULTS_PORT)
                result_collection = eval("connection.{db_name}.{collection_name}".format(
                                                                    db_name=MONGO_NLP_RESULTS_DB,
                                                                    collection_name=MONGO_NLP_RESULTS_COLLECTION)) 

                result_collection.update({"sentence_id": sentence_id,}, {"$set": 
                                    {"tag.{0}".format(prediction_algorithm_name): tag,  
                                    "sentiment.{0}".format(prediction_algorithm_name): sentiment}},  
                                    upsert=False)
                connection.close()
                return 


        @staticmethod
        def retrieve_document(sentence_id, word_tokenization_algorithm, pos_tagging_algorithm, noun_phrases_algorithm):
                """
                Here we need only the sentences_id because
                #Checking tag_analysis_algorithm result exists or not
                #result_collection.find_one({"sentence_id": sentence_id, "noun_phrases.regex_textblob_conll": {"$exists": True}})
                """
                #Checking tag_analysis_algorithm result exists or not
                connection = pymongo.Connection(MONGO_NLP_RESULTS_IP, MONGO_NLP_RESULTS_PORT)
                result_collection = eval("connection.{db_name}.{collection_name}".format(
                                                                    db_name=MONGO_NLP_RESULTS_DB,
                                                                    collection_name=MONGO_NLP_RESULTS_COLLECTION)) 
                if not result_collection.find_one({"sentence_id": sentence_id}):
                        return list((False, False, False))

                
                result = result_collection.find_one({"sentence_id": sentence_id})
               
                try:
                        noun_phrases_algorithm_result = result.get("noun_phrases").get(noun_phrases_algorithm)\
                                .get(pos_tagging_algorithm).get(word_tokenization_algorithm)
                        print "{start_color}Noun Phrases for --<<{sentence_id}>>-- for --<<algorithm>>--has aready\
                                been found --<<{noun_phrases}>>--{end_color}".format(start_color =bcolors.OKBLUE, 
                                                            sentence_id = sentence_id, 
                                                            algorithm = noun_phrases_algorithm,
                                                            noun_phrases= noun_phrases_algorithm_result, 
                                                            end_color = bcolors.RESET,
                                                            )
                except Exception as e:
                        noun_phrases_algorithm_result = None
                        print "{start_color}Noun Phrases for --<<{sentence_id}>>-- for --<<algorithm>>--has aready\
                                been found --<<{noun_phrases}>>--{end_color}".format(start_color =bcolors.FAIL, 
                                                            sentence_id = sentence_id, 
                                                            algorithm = noun_phrases_algorithm,
                                                            noun_phrases= noun_phrases_algorithm_result, 
                                                            end_color = bcolors.RESET,
                                                            )

                try:
                        word_tokenization_algorithm_result = result.get("word_tokenization").get(word_tokenization_algorithm)
                        print "{start_color}Word Tokenization result for --<<{sentence_id}>>--for --<<{algorithm}>>-- has aready\
                                been found --<<{word_tokenization}>>-- {end_color}".format(start_color =bcolors.OKBLUE, 
                                                            sentence_id = sentence_id, 
                                                            algorithm = word_tokenization_algorithm,
                                                            word_tokenization = word_tokenization_algorithm_result,
                                                            end_color = bcolors.RESET
                                                            )
                except Exception as e:
                        word_tokenization_algorithm_result = None
                        print "{start_color}Word Tokenization result for --<<{sentence_id}>>--for --<<{algorithm}>>-- has not been\
                                found --<<{word_tokenization}>>-- {end_color}".format(start_color =bcolors.FAIL, 
                                                            sentence_id = sentence_id, 
                                                            algorithm = word_tokenization_algorithm,
                                                            word_tokenization = word_tokenization_algorithm_result,
                                                            end_color = bcolors.RESET
                                                            )
                        
                        

                try:
                        pos_tagging_algorithm_result = result.get("pos_tagging").get(pos_tagging_algorithm)\
                                                .get(word_tokenization_algorithm)
                        print "{start_color}Pos Tagging result for --<<{sentence_id}>>--for --<<{algorithm}>>--\
                                has aready been found --<<{pos_tagging}>>--{end_color}".format(start_color =bcolors.OKBLUE, 
                                                            sentence_id = sentence_id, 
                                                            algorithm = pos_tagging_algorithm,
                                                            pos_tagging = pos_tagging_algorithm_result,
                                                            end_color = bcolors.RESET
                                                            )
                except Exception as e:
                        pos_tagging_algorithm_result = None
                        print "{start_color}Pos Tagging result for --<<{sentence_id}>>--for --<<{algorithm}>>--\
                                has not been found --<<{pos_tagging}>>--{end_color}".format(start_color =bcolors.FAIL, 
                                                            sentence_id = sentence_id, 
                                                            algorithm = pos_tagging_algorithm,
                                                            pos_tagging = pos_tagging_algorithm_result,
                                                            end_color = bcolors.RESET
                                                            )

                connection.close()
                return list((word_tokenization_algorithm_result, 
                                    pos_tagging_algorithm_result, noun_phrases_algorithm_result))

        @staticmethod
        def retrieve_predictions(sentence_id, tag_analysis_algorithm, sentiment_analysis_algorithm):
                """
                Chekcs if the required sentence has the specific predictions algorithms implemented
                or not, returns True if predictions for tag, sentiment, etc present else returns 
                False

                """
                connection = pymongo.Connection(MONGO_NLP_RESULTS_IP, MONGO_NLP_RESULTS_PORT)
                result_collection = eval("connection.{db_name}.{collection_name}".format(
                                                                    db_name=MONGO_NLP_RESULTS_DB,
                                                                    collection_name=MONGO_NLP_RESULTS_COLLECTION)) 
                if not result_collection.find_one({"sentence_id": sentence_id}):
                        return list((False, False))


                result = result_collection.find_one({"sentence_id": sentence_id})
                try:
                        tag = result.get("tag").get(tag_analysis_algorithm)
                        sentiment = result.get("sentiment").get(sentiment_analysis_algorithm)
                        print "{start_color}Tag for --<<{sentence_id}>>-- has aready been found Tag --<<{tag}>>--\
                                    and sentiment --<<sentiment>>--{end_color}".format(start_color =bcolors.OKBLUE, 
                                                            sentence_id = sentence_id, 
                                                            tag= tag, 
                                                            sentiment = sentiment,
                                                            end_color = bcolors.RESET
                                                            )
                except Exception as e:
                        tag, sentiment = False, False
                        print "{start_color}Tag for --<<{sentence_id}>>-- has not been found --<<{tag}>>--\
                         and sentiment --<<sentiment>>--{end_color}".format(start_color =bcolors.FAIL, 
                                                            sentence_id = sentence_id, 
                                                            tag= tag, 
                                                            sentiment = sentiment,
                                                            end_color = bcolors.RESET
                                                            )
                connection.close()
                return list((tag, sentiment))


