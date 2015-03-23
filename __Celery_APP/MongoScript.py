
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
import hashlib
file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(file_path)

from GlobalConfigs import MONGO_NP_RESULTS_IP, MONGO_NP_RESULTS_PORT, MONGO_NP_RESULTS_DB, MONGO_SENTENCES_NP_RESULTS_COLLECTION,\
                        MONGO_REVIEWS_NP_RESULTS_COLLECTION, MONGO_EATERY_NP_RESULTS_COLLECTION

from Text_Processing import bcolors 

connection = pymongo.MongoClient(MONGO_NP_RESULTS_IP, MONGO_NP_RESULTS_PORT, tz_aware=True, w=1, 
                                            j=True, max_pool_size=400, use_greenlets=True)


#This will have results for sentences
sentences_result_collection = eval("connection.{db_name}.{collection_name}".format(
                                                                    db_name=MONGO_NP_RESULTS_DB,
                                                                    collection_name=MONGO_SENTENCES_NP_RESULTS_COLLECTION)) 

#This will have combined result of all the setences present in the review, matched by review id 
reviews_result_collection = eval("connection.{db_name}.{collection_name}".format(
                                                                    db_name=MONGO_NP_RESULTS_DB,
                                                                    collection_name=MONGO_REVIEWS_NP_RESULTS_COLLECTION)) 


eatery_result_collection = eval("connection.{db_name}.{collection_name}".format(
                                                                    db_name=MONGO_NP_RESULTS_DB,
                                                                    collection_name=MONGO_EATERY_NP_RESULTS_COLLECTION)) 





sentences_result_collection.ensure_index("sentence_id", unique=True)
reviews_result_collection.ensure_index("review_id", unique=True)


class MongoForCeleryResults:
        """
        This is the class which deals with the update, deletion and insertion of results
        returned by celery nodes after doing natural language processing on the reviews for a particular
        eatery
        """
        def __init__(self,):
                pass

        @staticmethod
        def bulk_update_insert_sentence(eatery_id, __sentences):
                """
                __sentences of the form list with each lsit of the form
                review_id, eatery_id, sentence_id, sentence):
                Deals with update and deletion of the document
                The actual length of the sentences will be diferent because multiple reviews would
                have same setneces and would have same sentences ids
                """
                bulk = sentences_result_collection.initialize_ordered_bulk_op()
                for sentence in __sentences:

                        #bulk.find({"sentence_id": __sentences[3]}).updateOne{
                        bulk.find({"sentence_id": sentence[2],}).upsert().update_one(
                               {"$set": {
                                    "review_id": sentence[0], 
                                    "sentence": sentence[1], 
                                    "eatery_id": eatery_id}})
                                    
                        
                
                bulk.execute()
                return                                                    

        @staticmethod
        def insert_word_tokenization_result(sentence_id, word_tokenization_algorithm_name, 
                                                            word_tokenization_algorithm_result):

                """
                Deals with the update and insert operation word_tokenization_algorithm_result of sentence 
                with sentence_id
                """
                sentences_result_collection.update({"sentence_id": sentence_id,}, {"$set": 
                                    {"word_tokenization.{0}".format(word_tokenization_algorithm_name): word_tokenization_algorithm_result}},  
                                    upsert=False)

                return 
        
        @staticmethod
        def insert_pos_tagging_result(sentence_id, word_tokenization_algorithm_name,
                                                            pos_tagging_algorithm_name, 
                                                            pos_tagging_algorithm_result):

                """
                Deals with the update and insert operation pos_tagging_algorithm_result of sentence 
                with sentence_id
                """
                sentences_result_collection.update({"sentence_id": sentence_id,}, {"$set": 
                                    {"pos_tagging.{0}.{1}".format(pos_tagging_algorithm_name, word_tokenization_algorithm_name): 
                                        pos_tagging_algorithm_result}},  
                                    upsert=False)
                return 
        
        @staticmethod
        def insert_noun_phrases_result(sentence_id, word_tokenization_algorithm_name,pos_tagging_algorithm_name, 
                                                    noun_phrases_algorithm_name, noun_phrases_algorithm_result):

                """
                Deals with the update and insert operation noun_phrases_algorithm_result of sentence 
                with sentence_id
                """
                sentences_result_collection.update({"sentence_id": sentence_id,}, {"$set": 
                                    {"noun_phrases.{0}.{1}.{2}".format(noun_phrases_algorithm_name, pos_tagging_algorithm_name, 
                                            word_tokenization_algorithm_name): noun_phrases_algorithm_result}},  
                                    upsert=False)
                return 
        
        @staticmethod
        def insert_ner_result(sentence_id, pos_tagging_algorithm, ner_algorithm, ner_result):

                """
                Deals with the update and insert operation for ner result with sentence_id
                ner_algorithm, pos_tagging_algorithm, The ner result is based only on the 
                pos tagging of the sentnece, so the ner result will be stored only on the basis
                of the two algorithms name
                """
                sentences_result_collection.update({"sentence_id": sentence_id,}, {"$set": 
                                    {"ner.{0}.{1}".format(ner_algorithm, pos_tagging_algorithm): 
                                        ner_result}},  
                                    upsert=False)
                return 
        
        @staticmethod
        def bulk_insert_predictions(eatery_id, prediction_algorithm_name, __sentences):

                """
                Deals with the update and insert operation of tag analysis algorithm results
                and sentiment analysis algorithm result

                 zip(ids, sentences, sentences_ids, predicted_tags, predicted_sentiment) 
                """
                bulk = sentences_result_collection.initialize_ordered_bulk_op()
                for sentence in __sentences:
                        #bulk.find({"sentence_id": __sentences[3]}).updateOne{
                        bulk.find({"sentence_id": sentence[2],}).upsert().update_one(
                               {"$set": {
                                    "review_id": sentence[0], 
                                    "sentence": sentence[1], 
                                    "eatery_id": eatery_id,
                                    "tag.{0}".format(prediction_algorithm_name): sentence[3],  
                                    "sentiment.{0}".format(prediction_algorithm_name): sentence[4],  
                                    }})
                                    
                        
                
                bulk.execute()
                return 


        @staticmethod
        def retrieve_document(sentence_id, prediction_algorithm, word_tokenization_algorithm, pos_tagging_algorithm, 
                                                                noun_phrases_algorithm, ner_algorithm):
                """
                Here we need only the sentences_id because
                #Checking tag_analysis_algorithm result exists or not
                #result_collection.find_one({"sentence_id": sentence_id, "noun_phrases.regex_textblob_conll": {"$exists": True}})
                #Checking tag_analysis_algorithm result exists or not
                """
                if not sentences_result_collection.find_one({"sentence_id": sentence_id}):
                        return list((False, False, False))

                
                result = sentences_result_collection.find_one({"sentence_id": sentence_id})
                try:
                        tag_result = result.get("tag").get(prediction_algorithm)

                except Exception as e:
                        tag_result = None
                        print "Tga could be found"
                
                try:
                        sentiment_result = result.get("sentiment").get(prediction_algorithm)

                except Exception as e:
                        sentiment_result = None
                        print "Tga could be found"

                try:
                        ner_algorithm_result = result.get("ner").get(ner_algorithm).get(pos_tagging_algorithm)
                        
                        print "{start_color}NER for --<<{sentence_id}>>-- for --<<algorithm>>--has aready\
                                been found --<<{ners}>>--{end_color}".format(start_color =bcolors.OKBLUE, 
                                                            sentence_id = sentence_id, 
                                                            algorithm = ner_algorithm,
                                                            ners= ner_algorithm_result, 
                                                            end_color = bcolors.RESET,
                                                            )

                except Exception as e:
                        ner_algorithm_result = None
                        print "{start_color}NER for --<<{sentence_id}>>-- for --<<algorithm>>--has not\
                                been found --<<{ners}>>--{end_color}".format(start_color =bcolors.FAIL, 
                                                            sentence_id = sentence_id, 
                                                            algorithm = ner_algorithm,
                                                            ners= ner_algorithm_result, 
                                                            end_color = bcolors.RESET,
                                                            )

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

                return list((tag_result, sentiment_result, word_tokenization_algorithm_result, 
                                    pos_tagging_algorithm_result, noun_phrases_algorithm_result, ner_algorithm_result))


        @staticmethod
        def if_review(review_id, prediction_algorithm_name):
                if not bool(list(sentences_result_collection.find(
                                    {'review_id': review_id, 
                                    "tag.{0}".format(prediction_algorithm_name): {"$exists": True}}))):
                        print "{start_color} Review with {review_id} has not been found {end_color}".format(
                                            start_color = bcolors.FAIL,    
                                            review_id= hashlib.md5(review_id).hexdigest(),
                                            end_color=bcolors.RESET,)
                        return False
                print "{start_color} Review with {review_id} has already been found {end_color}".format(
                                            start_color = bcolors.OKBLUE,    
                                            review_id= hashlib.md5(review_id).hexdigest(),
                                            end_color=bcolors.RESET,)
                return True
      

        @staticmethod
        def get_review_sentence_ids(review_id):
                def conversion(__object):
                    return {"review_id": review_id,
                            "sentence_id": __object[0],
                            "sentence": __object[1],
                                } 
                try:
                        result = reviews_result_collection.find_one({'review_id': review_id}).get("sentence_ids")

                        return map(conversion, result)
                except Exception:
                        return False

        @staticmethod
        def update_review_sentence_ids(review_id, sentence_ids):
                """
                Args:
                    review_id
                    sentence_ids : a list of tuple with each tuple of the form
                            [["424r2cdcdv", "hey man!"], [], []]

                """
                bulk =  reviews_result_collection.initialize_ordered_bulk_op()
                for sentence in sentence_ids:

                        #bulk.find({"sentence_id": __sentences[3]}).updateOne{
                        bulk.find({"review_id": review_id,}).upsert().update_one(
                               {"$push": {
                                    "sentence_ids": sentence}})
                bulk.execute()
                return                                                    

                


        @staticmethod
        def post_review_noun_phrases(review_id, tag, sentiment, noun_phrases, word_tokenization_algorithm_name, 
                                                    pos_tagging_algorithm_name, noun_phrases_algorithm_name):
                
                bulk =  reviews_result_collection.initialize_ordered_bulk_op()
                for __np in noun_phrases:
                        for element in __np:
                                bulk.find({"review_id": review_id,}).upsert().update_one(
                               {"$push": {
                                    "noun_phrases.{0}.{1}.{2}.{3}".format(tag, noun_phrases_algorithm_name, 
                                        pos_tagging_algorithm_name, word_tokenization_algorithm_name): (element, sentiment)}})
                try:
                        bulk.execute()
                
                except pymongo.errors.InvalidOperation  as e:
                        reviews_result_collection.update({"review_id": review_id,}, 
                               {"$push": {
                                    "noun_phrases.{0}.{1}.{2}.{3}".format(tag, noun_phrases_algorithm_name, 
                                        pos_tagging_algorithm_name, word_tokenization_algorithm_name): (None, None)}}, 
                                        upsert=True)
                        print "No noun phrases"
                return                                                    
       




        @staticmethod
        def post_review_ner_result(review_id, ner_result, ner_algorithm_name,
                                                    pos_tagging_algorithm_name):
                """
                This method inserts the ner result of the setnences into the review to which they beong to,

                """
                bulk =  reviews_result_collection.initialize_ordered_bulk_op()
                for __np in ner_result:
                        for element in __ner:
                                bulk.find({"review_id": review_id,}).upsert().update_one(
                               {"$push": {
                                    "ner.{0}.{1}".format(ner_algorithm_name, 
                                        pos_tagging_algorithm_name): element}})
                try:
                        bulk.execute()
                
                except pymongo.errors.InvalidOperation  as e:
                        reviews_result_collection.update({"review_id": review_id,}, 
                               {"$push": {
                                    "ner.{0}.{1}".format(ner_algorithm_name, 
                                        pos_tagging_algorithm_name): (None, None)}}, 
                                        upsert=True)
                        print "No ner found for this sentence"
                return                                                    
                



        
        @staticmethod
        def get_review_noun_phrases(review_id, category, word_tokenization_algorithm, pos_tagging_algorithm, 
                                                                            noun_phrases_algorithm):
                
                """
                Checks whether the noun phrases for review_id is present for algorithms in
                reviews_result_collection
                """
                try:
                        result = reviews_result_collection.find_one({"review_id": review_id}, 
                            {"noun_phrases.{0}.{1}.{2}.{3}".format(category, noun_phrases_algorithm, pos_tagging_algorithm, 
                                word_tokenization_algorithm): True}).get("noun_phrases").get(category).get(noun_phrases_algorithm).get(pos_tagging_algorithm).get(word_tokenization_algorithm)

                except Exception as e:
                        print e
                        print "This review might not have any sentence categorized into desired category"
                        result = [None, None]
                return result
        
        @staticmethod
        def review_noun_phrases(review_id, category, word_tokenization_algorithm_name, pos_tagging_algorithm_name, 
                                                                            noun_phrases_algorithm_name):
                
                """
                Checks whether the noun phrases for review_id is present for algorithms in
                reviews_result_collection
                """
                if not reviews_result_collection.find_one({"review_id": review_id, 
                            "noun_phrases.{0}.{1}.{2}.{3}".format(category, noun_phrases_algorithm_name, pos_tagging_algorithm_name, 
                                word_tokenization_algorithm_name): {"$exists": True}}):
                        return False

                return True
        
        @staticmethod
        def review_result(review_id, prediction_algorithm_name):
                def conversion(__object):
                        print "{start_color} Sentence with {sentence_id} for the {review_id} has been found {end_color}".format(
                                    start_color=bcolors.OKBLUE,
                                    sentence_id = __object.get("sentence_id"),
                                    review_id = __object.get("review_id"),
                                    end_color=bcolors.FAIL,
                                )
                        
                        return [__object.get("review_id"), __object.get("sentence"), __object.get("sentence_id"), 
                                __object.get("tag").get(prediction_algorithm_name), 
                                __object.get("sentiment").get(prediction_algorithm_name)]
                    
            
            
                result = map(conversion, list(sentences_result_collection.find({'review_id': review_id}, 
                            fields= {"_id": False, "review_id": True, "sentence": True, "sentence_id": True, 
                                    "tag": True,  "sentiment" : True,})))
                return result


        @staticmethod
        def retrieve_predictions(sentence_id, tag_analysis_algorithm, sentiment_analysis_algorithm):
                """
                Chekcs if the required sentence has the specific predictions algorithms implemented
                or not, returns True if predictions for tag, sentiment, etc present else returns 
                False

                print "{0}This is the fucking sentecen id {1}{2}".format(bcolors.FAIL, sentence_id, bcolors.RESET)

                """
                result = sentences_result_collection.find_one({"sentence_id": sentence_id})
                if not result:
                        return list((False, False))


                try:
                        tag = result.get("tag").get(tag_analysis_algorithm)
                        sentiment = result.get("sentiment").get(sentiment_analysis_algorithm)
                        """
                        print "{start_color}Tag for --<<{sentence_id}>>-- has aready been found Tag --<<{tag}>>--\
                                    and sentiment --<<{sentiment}>>--{end_color}".format(start_color =bcolors.OKBLUE, 
                                                            sentence_id = sentence_id, 
                                                            tag= tag, 
                                                            sentiment = sentiment,
                                                            end_color = bcolors.RESET
                                                            )
                        """
                except Exception as e:
                        tag, sentiment = False, False
                        """
                        print "{start_color}Tag for --<<{sentence_id}>>-- has not been found --<<{tag}>>--\
                         and sentiment --<<{sentiment}>>--{end_color}".format(start_color =bcolors.FAIL, 
                                                            sentence_id = sentence_id, 
                                                            tag= tag, 
                                                            sentiment = sentiment,
                                                            end_color = bcolors.RESET
                                                         )
                        """
                return list((tag, sentiment))


        @staticmethod
        def update_classification_algorithms_reviews(not_already_tokenized_n_predicted, prediction_algorithm_name):
                bulk =  reviews_result_collection.initialize_ordered_bulk_op()
                for review in not_already_tokenized_n_predicted:
                                review_id = review[0]
                                bulk.find({"review_id": review_id,}).upsert().update_one(
                               {"$push": {
                                    "tag_classification_algorithm_name": prediction_algorithm_name}})
                                
                                bulk.find({"review_id": review_id,}).upsert().update_one(
                               {"$push": {
                                    "sentiment_classification_algorithm_name": prediction_algorithm_name}})
                try:
                        bulk.execute()
                
                except pymongo.errors.InvalidOperation  as e:
                        print "{start_color} Error occured while update classification algorithms with error --<<{e}>>--\
                                {end_color}".format(
                                        start_color = bcolors.FAIL,
                                        e = e,
                                        end_color = bcolors.RESET,)
                return                                                    
       
        @staticmethod
        def check_if_prediction_algorithm_present_review(review_id, prediction_algorithm_name):
                if bool(list(reviews_result_collection.find({"review_id": review_id , 
                    'tag_classification_algorithm_name': {"$in": [prediction_algorithm_name]}}))):
                        return True
                return False
                        
        @staticmethod
        def post_review_noun_phrases_to_eatery(eatery_id, result, category, word_tokenization_algorithm_name, 
                                                    pos_tagging_algorithm_name, noun_phrases_algorithm_name):
                
                bulk =  eatery_result_collection.initialize_ordered_bulk_op()
                for __data in result:
                        print __data[0], 
                        print __data[1], "\n\n"
                        bulk.find({"eatery_id": eatery_id,}).upsert().update_one(
                               {"$set": {
                                    "{0}.noun_phrases.{1}.{2}.{3}.{4}".format(__data[0], category, noun_phrases_algorithm_name,\
                                            pos_tagging_algorithm_name, word_tokenization_algorithm_name): __data[1]}})
                try:
                        bulk.execute()
                
                except pymongo.errors.InvalidOperation  as e:
                        print "{start_color} Something Terrible happened while storing noun_phrases --<<{noun_phrases}>>--\
                                for eatery_id --<<{eatery_id}>>-- {end_color}".format(
                                                        start_color = bcolors.FAIL,
                                                        noun_phrases= result,
                                                        eatery_id= eatery_id,
                                                        end_color = bcolors.RESET,
                                        )
                return                                                    
        
        @staticmethod
        def get_review_noun_phrases_for_eatery(eatery_id, review_id, category, word_tokenization_algorithm_name, 
                                                    pos_tagging_algorithm_name, noun_phrases_algorithm_name):
        
                
                if not eatery_result_collection.find_one(
                                {'eatery_id': eatery_id, 
                                    "{0}.noun_phrases.{1}.{2}.{3}.{4}".format(review_id, category, noun_phrases_algorithm_name,  
                                         pos_tagging_algorithm_name, word_tokenization_algorithm_name) : {"$exists": True}}):
                        
                                    
                                    
                        print "{start_color} Review with {review_id} has no noun phrases found in eatery --<<{eatery_id}>>--{end_color}".format(
                                            start_color = bcolors.FAIL,    
                                            #review_id= hashlib.md5(review_id).hexdigest(),
                                            review_id= review_id,
                                            eatery_id = eatery_id,
                                            end_color=bcolors.RESET,)
                        return False
                

                print "{start_color} Review with {review_id} has noun phrases found for eatery_id --<<{eatery_id}>>--{end_color}".format(
                                            start_color = bcolors.OKBLUE,    
                                            #review_id= hashlib.md5(review_id).hexdigest(),
                                            review_id= review_id,
                                            eatery_id = eatery_id,
                                            end_color=bcolors.RESET,)
                return True

                
        @staticmethod
        def noun_phrases_for_eatery(eatery_id, review_list, category, word_tokenization_algorithm_name, 
                                                    pos_tagging_algorithm_name, noun_phrases_algorithm_name):
    
                """
                Gets a review_list and returns the noun phrases for the eatery
                correponding to the word_tokenization_algorithm_name, pos_tagging_algorithm_name, 
                noun_phrases_algorithm_name
                """
                list_to_include = list()
                for review_id in review_list:
                        __string = "{0}.noun_phrases.{1}.{2}.{3}.{4}".format(review_id, 
                                                    category, noun_phrases_algorithm_name,
                                                    pos_tagging_algorithm_name, word_tokenization_algorithm_name)
                        list_to_include.append(__string)


                eatery_result_collection.find()


