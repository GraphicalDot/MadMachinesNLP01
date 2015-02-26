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
                                    upsert=True)

                connection.close()
                return 
        
        @staticmethod
        def insert_pos_tagging_result(sentence_id, pos_tagging_algorithm_name, 
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
                                    {"pos_tagging.{0}".format(pos_tagging_algorithm_name): pos_tagging_algorithm_result}},  
                                    upsert=True)
                connection.close()
                return 
        
        @staticmethod
        def insert_noun_phrases_result(sentence_id, noun_phrases_algorithm_name, 
                                                            noun_phrases_algorithm_result):

                """
                Deals with the update and insert operation noun_phrases_algorithm_result of sentence 
                with sentence_id
                """
                connection = pymongo.Connection(MONGO_NLP_RESULTS_IP, MONGO_NLP_RESULTS_PORT)
                result_collection = eval("connection.{db_name}.{collection_name}".format(
                                                                    db_name=MONGO_NLP_RESULTS_DB,
                                                                    collection_name=MONGO_NLP_RESULTS_COLLECTION)) 
                result_collection.update({"sentence_id": sentence_id,}, {"$set": 
                                    {"noun_phrases.{0}".format(noun_phrases_algorithm_name): noun_phrases_algorithm_result}},  
                                    upsert=True)
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
                                    upsert=True)
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
                        noun_phrases_algorithm_result = result.get("noun_phrases").get(noun_phrases_algorithm)
                except Exception as e:
                        noun_phrases_algorithm_result = None

                print noun_phrases_algorithm_result
                try:
                        word_tokenization_algorithm_result = result.get("word_tokenization").get(word_tokenization_algorithm)
                except Exception as e:
                        word_tokenization_algorithm_result = None
                        
                        
                print word_tokenization_algorithm_result

                try:
                        pos_tagging_algorithm_result = result.get("pos_tagging").get(pos_tagging_algorithm)
                except Exception as e:
                        pos_tagging_algorithm_result = None

                print pos_tagging_algorithm_result
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
                except Exception as e:
                        tag = False
                print tag 
                try:
                        sentiment = result.get("sentiment").get(sentiment_analysis_algorithm)
                except Exception as e:
                        sentiment= False

                print sentiment
                connection.close()
                return list((tag, sentiment))


