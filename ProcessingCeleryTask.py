#!/usr/bin/env python
#-*- coding: utf-8 -*-
from __future__ import absolute_import
import celery
from celery import states
from celery.task import Task, subtask
from celery.utils import gen_unique_id, cached_property
from celery.decorators import periodic_task
from datetime import timedelta
from celery.utils.log import get_task_logger
import time
import pymongo
import random
from celery.registry import tasks
import logging
import inspect
from celery import task, group
from sklearn.externals import joblib
import time
import os
import sys
import time
import hashlib
import itertools
from compiler.ast import flatten
from collections import Counter
from itertools import groupby
from operator import itemgetter

connection = pymongo.Connection()
db = connection.intermediate
collection = db.intermediate_collection
from pymongo.errors import BulkWriteError

logger = logging.getLogger(__name__)

db = connection.modified_canworks
reviews = db.review

ALGORITHM_TAG = ""
ALGORITHM_SENTIMENT = ""

from GlobalConfigs import MONGO_REVIEWS_IP, MONGO_REVIEWS_PORT, MONGO_REVIEWS_EATERIES_COLLECTION,\
        MONGO_REVIEWS_REVIEWS_COLLECTION, MONGO_NP_RESULTS_IP,MONGO_NP_RESULTS_PORT, MONGO_NP_RESULTS_DB,\
        MONGO_SENTENCES_NP_RESULTS_COLLECTION, MONGO_REVIEWS_NP_RESULTS_COLLECTION, MONGO_EATERY_NP_RESULTS_COLLECTION 
            

from __Celery_APP.App import app
from __Celery_APP.MongoScript import MongoForCeleryResults
from Text_Processing import WordTokenize, PosTaggers, SentenceTokenizationOnRegexOnInterjections, bcolors, NounPhrases,\
                NERs, NpClustering

file_path = os.path.dirname(os.path.abspath(__file__))
                
                
#ReviewIdToSentTokenize Worker:
        #review_list

        #Check if noun phrase for review_id is present, break the list into no and yes lists for reviews
                #case 1: Nothing is present for any review
                        #Step1: Tokenize all the reviews with data structures and sentence id and eatery id
                        #Step2: Predict all the sentences
                        #Step3: Store the results in mongodb

                #case2: Partial present and partial not present
                        #REpeat case 1 for all the not present

                
                #After this step sentences_result_collection will have all the sentences, with data_strutures like this
                #present in the database
                        #post = {u'review_id': u'121052', 
                        #u'sentiment': {u'svm_linear_kernel_classifier': u'super-positive'}, 
                        #u'sentence': u'their staff is very courteous and welcoming .', 
                        #u'eatery_id': u'154', 
                        #u'sentence_id': u'1f3236fb2052b82c1d7691588a78b1e7', 
                        #u'tag': {u'svm_linear_kernel_classifier': u'service'}, 
                        #u'_id': ObjectId('54f41f064af2c83b8a0a3f4b')}

#NoNounPhrasesReviews Worker:
        #check in reviews_result__collection whether the noun phrase are present or not
        #only pass on the reviews which will have no noun_phrases present in it
                #Step 1:
                        #it will get list of list with each list like below
                        #([eatery_id, review_id, sentence, sentence_id, tag, sentiment]
                #Step2:
                        #newdictList = [ next(x[1]) for x in groupby(sorted(a, key=itemgetter('review_id')), key=itemgetter('review_id')) ]
                    
                #Step3:
                        #filter newdictList on the basis of, for which review_id noun phrases are present for particular algorithms
                        #append to a new list called as reviews_with_noun_phrases

                #Step4:
                        #Make a new list wich will have all the sentences with review ids who dont have noun phrases

#MappingList Worker:
            #Makes parallel execution of the SentTokenizeToNP workers

#SentTokenizeToNP Worker:
        #it will only get sentences whose review ids doesnt have noun phrases
                        
                #Step1: it will get a data  structure like this
                        #([eatery_id, review_id, sentence, sentence_id, tag, sentiment], ner_algorithm, word_tokenization_algorithm, 
                        #   pos_tagging_algorithm, noun_phrases_algorithm, tag_analysis_algorithm, sentiment_analysis_algorithm,)

                        #Will check for all the algortihms for particular sentneces
                
                        #update reviews_result_collection with the noun phrases for this sentence, 
                        #and also with the sentences id


#ReviewsIdsToNounPhrases: Lastworker
                        #it will have only listof review ids going into it,
                        #the it will retrieve the noun phrases for all these reviews 
                        
#Clustering worker:
                        #makes cluster

                

def tag_classification(tag_analysis_algorithm, sentences):
        """
        Args:
            sentences: List of the sentences for whom the NLP clssification has to be done
            
            tag_analysis_algorithm: The name of the tag analysis algorithm on the basis of which the 
                                domain ralted tags has to be decided, Like for an example for the food domain the 
                                five tags thats has to be decided are food, overall, null, service, cost, ambience
        Returns:
            ["food", "ambience", ......]

        """
        classifier_path = "{0}/Text_Processing/PrepareClassifiers/InMemoryClassifiers/".format(file_path)
        classifier = joblib.load("{0}{1}".format(classifier_path, tag_analysis_algorithm))
        return classifier.predict(sentences)



def sentiment_classification(sentiment_analysis_algorithm, sentences):
        classifier_path = "{0}/Text_Processing/PrepareClassifiers/InMemoryClassifiers/".format(file_path)
        classifier = joblib.load("{0}{1}".format(classifier_path, sentiment_analysis_algorithm))
        return classifier.predict(sentences) 

@app.task()
class CleanResultBackEnd(celery.Task):
	ignore_result = True
	max_retries=3, 
	acks_late=True
	default_retry_delay = 5
        def run(self, id_list):
                """
                To start this worker,
                This worker has a Queue CleanResultBackEndQueue
                celery -A ProcessingCeleryTask  worker -n CleanResultBackEndOne -Q CleanResultBackEndQueue --concurrency=4 --loglevel=info
                It cleans the results which are being stored into the mongodb which is the result backend
                for the celery.

                Variables in Scope:
                    id_list:It is the list of all the ids who are being executed by several celery nodes

                """
                self.start = time.time() 
                connection = pymongo.Connection(MONGO_REVIEWS_IP, MONGO_REVIEWS_PORT)
                celery_collection_bulk = connection.celery.celery_taskmeta.initialize_unordered_bulk_op()
                
                for _id in id_list:
                        celery_collection_bulk.find({'_id': _id}).remove_one()

                try:
                    celery_collection_bulk.execute()
                except BulkWriteError as bwe:
                    print(bwe.details)
                connection.close()
                return 

        def after_return(self, status, retval, task_id, args, kwargs, einfo):
		#exit point of the task whatever is the state
		logger.info("{color} Ending --<{function_name}--> of task --<{task_name}>-- with time taken\
                        --<{time}>-- seconds  {reset}".format(color=bcolors.OKBLUE,\
                        function_name=inspect.stack()[0][3], task_name= self.__class__.__name__, 
                            time=time.time() -self.start, reset=bcolors.RESET))
                pass

	def on_failure(self, exc, task_id, args, kwargs, einfo):
		logger.info("{color} Ending --<{function_name}--> of task --<{task_name}>-- failed fucking\
                        miserably {reset}".format(color=bcolors.OKBLUE,\
                        function_name=inspect.stack()[0][3], task_name= self.__class__.__name__, reset=bcolors.RESET))
                logger.info("{0}{1}".format(einfo, bcolors.RESET))
		self.retry(exc=exc)


@app.task()
class Clustering(celery.Task):
	max_retries=3, 
	acks_late=True
	default_retry_delay = 5
        def run(self, eatery_id, category, start_epoch, end_epoch, word_tokenization_algorithm_name, 
                        pos_tagging_algorithm_name, noun_phrases_algorithm_name, clustering_algorithm_name, number):
                """
                Args:
                    result: A list of list in the form [[u'Subway outlet', u'positive'],
                     [u'subway', u'positive'],
                      [u'bread', u'positive']]

                    number: Maximum number of noun phrases required
                """
                self.start = time.time()
                if start_epoch and end_epoch:
                        review_list = [post.get("review_id") for post in 
                            reviews.find({"eatery_id" :eatery_id, "converted_epoch": {"$gt":  start_epoch, "$lt" : end_epoch}})]

                else:
                        review_list = [post.get("review_id") for post in 
                            reviews.find({"eatery_id" :eatery_id})]
                
                
                result = list()
                for review_id in review_list:
                        print review_id
                        result.extend(MongoForCeleryResults.get_review_noun_phrases(review_id, category, word_tokenization_algorithm_name, pos_tagging_algorithm_name, noun_phrases_algorithm_name))


                
                result = [element for element in result if element]
                result = [element for element in result if element[0] != None]
                print result
                 
                
                edited_result = list()
                for element in result:
                        if element[1].startswith("super"):
                                edited_result.append((element[0], element[1].split("-")[1]))
                                edited_result.append((element[0], element[1].split("-")[1]))
                        else:
                                edited_result.append(tuple(element))


                final_result = list()
                for key, value in Counter(edited_result).iteritems():
                        final_result.append({"name": key[0], "polarity": 1 if key[1] == 'positive' else 0 , "frequency": value}) 
           
                sorted_result = sorted(final_result, reverse=True, key=lambda x: x.get("frequency"))
                #return sorted_result[0: number]
                return sorted_result

        def after_return(self, status, retval, task_id, args, kwargs, einfo):
		#exit point of the task whatever is the state
		logger.info("{color} Ending --<{function_name}--> of task --<{task_name}>-- with time taken\
                        --<{time}>-- seconds  {reset}".format(color=bcolors.OKBLUE,\
                        function_name=inspect.stack()[0][3], task_name= self.__class__.__name__, 
                            time=time.time() -self.start, reset=bcolors.RESET))
		pass

	def on_failure(self, exc, task_id, args, kwargs, einfo):
		logger.info("{color} Ending --<{function_name}--> of task --<{task_name}>-- failed fucking\
                        miserably {reset}".format(color=bcolors.OKBLUE,\
                        function_name=inspect.stack()[0][3], task_name= self.__class__.__name__, reset=bcolors.RESET))
                logger.info("{0}{1}".format(einfo, bcolors.RESET))
		self.retry(exc=exc)


@app.task()
class StoreInEatery(celery.Task):
	max_retries=3, 
	acks_late=True
	default_retry_delay = 5
        def run(self, eatery_id, category, start_epoch, end_epoch, word_tokenization_algorithm_name, 
                        pos_tagging_algorithm_name, noun_phrases_algorithm_name, clustering_algorithm_name):
                """
                Only executed after all the processing is been done, This stores the noun phrases for a particular 
                review id into an eatery correponding the algorithms being called from api
                
                """
                self.start = time.time()
                if start_epoch and end_epoch:
                        review_list = [post.get("review_id") for post in 
                            reviews.find({"eatery_id" :eatery_id, "converted_epoch": {"$gt":  start_epoch, "$lt" : end_epoch}})]

                else:
                        review_list = [post.get("review_id") for post in 
                            reviews.find({"eatery_id" :eatery_id})]
                
                
                result = list()
                for review_id in review_list:
                        result.extend([review_id, MongoForCeleryResults.get_review_noun_phrases(review_id, category, word_tokenization_algorithm_name, pos_tagging_algorithm_name, noun_phrases_algorithm_name)])



                #result will have the form, it will be a list of lists with wach list fo the form
                """
                ["3261061", [
                                [u':-( dj', u'positive'],
                                [u'good tracksnuce', u'positive'],
                                [u'long time', u'positive'],
                                [u'good hukka', u'positive'],
                                [u'mumbai hukka r', u'positive'],
                                                   ]]
                """

                MongoForCeleryResults.post_review_noun_phrases_to_eatery(eatery_id, result, category, word_tokenization_algorithm_name, 
                                    pos_tagging_algorithm_name, noun_phrases_algorithm_name)
                
                return 


        def after_return(self, status, retval, task_id, args, kwargs, einfo):
		#exit point of the task whatever is the state
		logger.info("{color} Ending --<{function_name}--> of task --<{task_name}>-- with time taken\
                        --<{time}>-- seconds  {reset}".format(color=bcolors.OKBLUE,\
                        function_name=inspect.stack()[0][3], task_name= self.__class__.__name__, 
                            time=time.time() -self.start, reset=bcolors.RESET))
		pass

	def on_failure(self, exc, task_id, args, kwargs, einfo):
		logger.info("{color} Ending --<{function_name}--> of task --<{task_name}>-- failed fucking\
                        miserably {reset}".format(color=bcolors.OKBLUE,\
                        function_name=inspect.stack()[0][3], task_name= self.__class__.__name__, reset=bcolors.RESET))
                logger.info("{0}{1}".format(einfo, bcolors.RESET))
		self.retry(exc=exc)




@app.task()
class SentTokenizeToNP(celery.Task):
	max_retries=3, 
	acks_late=True
	default_retry_delay = 5
	def run(self, __sentence_dict, ner_algorithm, word_tokenization_algorithm, pos_tagging_algorithm, noun_phrases_algorithm, 
                                    tag_analysis_algorithm, sentiment_analysis_algorithm,):
                """
                To Start this worker
                    celery -A ProcessingCeleryTask  worker -n SentTokenizeToNP -Q SentTokenizeToNP --concurrency=4 
                    --loglevel=info 
                
                Estimated Time:
                    generally takes 0.09 to 0.15, Can increase to greater magnitude if used with more slow 
                    pos taggers like standford pos tagger

                Args:
                    __sentence = [id, sentence, predicted_tag, predicted_sentiment]
                    {'review_id': u'3266371', 'sentiment': u'neutral', 
                    'sentence': u'preparing both veg and non - veg sandwiches on a single platform using the same gloves ...', 
                    'eatery_id': u'154', 'sentence_id': u'53bca4f961558ba9f513dccb7c3274d3', 'tag': u'food'},
                    
                    word_tokenization_algorithm:
                            type: str
                            Name of the algorithm that shall be used to do word tokenization of the sentence

                    pos_tagging_algorithm: 
                            type: str
                            Name of the algorithm that shall be used to do pos_tagging of the sentence

                    noun_phrases_algorithm:
                            type: str
                            Name of the algorithm that shall be used to do noun phrase extraction from the sentence
                
                """
                self.start = time.time()


                review_id = __sentence_dict.get("review_id")
                sentence = __sentence_dict.get("sentence")
                sentence_id = __sentence_dict.get("sentence_id")
                eatery_id = __sentence_dict.get("eatery_id")
                tag = __sentence_dict.get("tag")
                sentiment = __sentence_dict.get("sentiment")

                prediction_algorithm = tag_analysis_algorithm.replace("_tag.lib", "")

                tag_result, sentiment_result, word_tokenization_algorithm_result, pos_tagging_algorithm_result,\
                        noun_phrases_algorithm_result, ner_algorithm_result = MongoForCeleryResults.retrieve_document(\
                        sentence_id, prediction_algorithm, word_tokenization_algorithm, pos_tagging_algorithm,\
                        noun_phrases_algorithm, ner_algorithm)



                if not word_tokenization_algorithm_result:
                        word_tokenize = WordTokenize([sentence],  default_word_tokenizer= word_tokenization_algorithm)
                        print word_tokenize
                        ##word_tokenized_sentences = word_tokenize.word_tokenized_list.get(WORD_TOKENIZATION_ALGORITHM)
                        word_tokenization_algorithm_result = word_tokenize.word_tokenized_list.get(word_tokenization_algorithm)
                        MongoForCeleryResults.insert_word_tokenization_result(sentence_id, 
                                                                            word_tokenization_algorithm, 
                                                                            word_tokenization_algorithm_result)

                if not pos_tagging_algorithm_result:
                        __pos_tagger = PosTaggers(word_tokenization_algorithm_result,  default_pos_tagger=pos_tagging_algorithm) 
                        #using default standford pos tagger
                        pos_tagging_algorithm_result =  __pos_tagger.pos_tagged_sentences.get(pos_tagging_algorithm)
                        print pos_tagging_algorithm
                        MongoForCeleryResults.insert_pos_tagging_result(sentence_id,
                                                                            word_tokenization_algorithm, 
                                                                            pos_tagging_algorithm, 
                                                                            pos_tagging_algorithm_result)
                
                """        
                if not ner_algorithm_result:
                        __ner_class = NERs(pos_tagging_algorithm_result, default_ner=ner_algorithm)
                        ner_result = __ner_class.ners.get(ner_algorithm)
                        MongoForCeleryResults.insert_ner_result(sentence_id, 
                                                                        pos_tagging_algorithm, 
                                                                        ner_algorithm,
                                                                        ner_result,)
                """
                if not noun_phrases_algorithm_result:
                        __noun_phrases = NounPhrases(pos_tagging_algorithm_result, default_np_extractor=noun_phrases_algorithm)
                        noun_phrases_algorithm_result =  __noun_phrases.noun_phrases.get(noun_phrases_algorithm)
                        MongoForCeleryResults.insert_noun_phrases_result(sentence_id, 
                                                                            word_tokenization_algorithm, 
                                                                            pos_tagging_algorithm, 
                                                                            noun_phrases_algorithm, 
                                                                            noun_phrases_algorithm_result)


                MongoForCeleryResults.post_review_noun_phrases(review_id,
                                                                tag_result,
                                                                sentiment_result,
                                                                noun_phrases_algorithm_result, 
                                                                word_tokenization_algorithm,
                                                                pos_tagging_algorithm,
                                                                noun_phrases_algorithm)

                """
                MongoForCeleryResults.post_review_ner_result(review_id, 
                                                            ner_algorithm_result,
                                                            ner_algorithm,
                                                            pos_tagging_algorithm)
                """
                return 

        def after_return(self, status, retval, task_id, args, kwargs, einfo):
		#exit point of the task whatever is the state
		logger.info("{color} Ending --<{function_name}--> of task --<{task_name}>-- with time taken\
                        --<{time}>-- seconds  {reset}".format(color=bcolors.OKBLUE,\
                        function_name=inspect.stack()[0][3], task_name= self.__class__.__name__, 
                            time=time.time() -self.start, reset=bcolors.RESET))
		pass

	def on_failure(self, exc, task_id, args, kwargs, einfo):
		logger.info("{color} Ending --<{function_name}--> of task --<{task_name}>-- failed fucking\
                        miserably {reset}".format(color=bcolors.OKBLUE,\
                        function_name=inspect.stack()[0][3], task_name= self.__class__.__name__, reset=bcolors.RESET))
                logger.info("{0}{1}".format(einfo, bcolors.RESET))
		self.retry(exc=exc)

        


@app.task()
class ReviewIdToSentTokenize(celery.Task):
	max_retries=3, 
	acks_late=True
	default_retry_delay = 5
	def run(self, eatery_id, category, start_epoch, end_epoch, tag_analysis_algorithm, sentiment_analysis_algorithm,
                        word_tokenization_algorithm_name, pos_tagging_algorithm_name, noun_phrases_algorithm_name):
                start = time.time()
                """
                Start This worker:
                    celery -A ProcessingCeleryTask  worker -n ReviewIdToSentTokenizeOne -Q ReviewIdToSentTokenizeQueue 
                        --concurrency=4 --loglevel=info
                """ 
                #As both tag_analysis_algorithm and sentiment_analysis_algorithm shall be same
                prediction_algorithm_name = tag_analysis_algorithm.replace("_tag.lib", "")

                self.start = time.time()
                sent_tokenizer = SentenceTokenizationOnRegexOnInterjections()
                
                ids_sentences = list()

                
                if start_epoch and end_epoch:
                        review_list = [(post.get("review_id"), post.get("review_text")) for post in 
                            reviews.find({"eatery_id" :eatery_id, "converted_epoch": {"$gt":  start_epoch, "$lt" : end_epoch}})]

                else:
                        review_list = [(post.get("review_id"), post.get("review_text")) for post in 
                            reviews.find({"eatery_id" :eatery_id})]
                        


                #review_list = [[review_id, review_text],[review_id, review_text], .....] 
                predicted_reviews, not_predicted_reviews = list(), list()

        
        
                for review in review_list:
                        #If the sentences for this reviews is present in the database, and are classified according to the prediction 
                        #algorithm given in the api call
                        if not MongoForCeleryResults.get_review_noun_phrases_for_eatery(eatery_id, review[0], category, 
                                word_tokenization_algorithm_name, pos_tagging_algorithm_name, noun_phrases_algorithm_name):
                                
                                not_predicted_reviews.append(review)
                        
                        """
                        if MongoForCeleryResults.if_review(review[0], prediction_algorithm_name):
                                predicted_reviews.append(review)
                        
                        #if the entences for particular review is not present that means it need to be sentence tokenized
                        #and then inserted into the database
                        else:
                                not_predicted_reviews.append(review)
                        """
               

                #check which reviews are sntence tokenized already
                not_already_tokenized_n_predicted = list()
                already_predicted_list = list()
                #not_already_tokenized have reviews which are noit yet sentence tokenized
                for review in not_predicted_reviews:
                        if not MongoForCeleryResults.check_if_prediction_algorithm_present_review(review[0], prediction_algorithm_name):
                                not_already_tokenized_n_predicted.append(review)

                        else:
                                already_predicted_list.append(review)
                #predicted_reviews = [[review_id, review_text],[review_id, review_text], .....] 
                #not_predicted_reviews = [[review_id, review_text],[review_id, review_text], .....] 
                
                ##This for loop inserts all the sentences in the mongodb, independent of the category
                ##they belongs to, 

                if bool(not_already_tokenized_n_predicted):
                        for element in not_already_tokenized_n_predicted:
                                sentences = list()
                                for __sentence in sent_tokenizer.tokenize(element[1]):
                                        ids_sentences.append(list(
                                                            (element[0], 
                                                            __sentence.encode("ascii", "xmlcharrefreplace"), 
                                                            hashlib.md5(__sentence.encode("ascii", "xmlcharrefreplace")).hexdigest()))) 
                                        
                                        sentences.append([hashlib.md5(__sentence.encode("ascii", "xmlcharrefreplace")).hexdigest(),
                                                             __sentence.encode("ascii", "xmlcharrefreplace")])
                                MongoForCeleryResults.update_review_sentence_ids(element[0], sentences)
                                #After this operation every review_id reviews_result_collection will have a list 
                                #sentence_ids of tokenize sentences present as elements in it

                                #(eatery_id, review_id, sentence, sentence_id)
                        #MongoForCeleryResults.bulk_update_insert_sentence(eatery_id, ids_sentences)
                
                        ids, sentences, sentences_ids = map(list, zip(*ids_sentences))


                        predicted_tags = tag_classification(tag_analysis_algorithm, sentences)
                        predicted_sentiment = sentiment_classification(sentiment_analysis_algorithm, sentences)

                        #Inserting tag and sentiment correponding to senences ids
                        #right now tag_analysis_algorithm shall be same as sentiment_analysis_algorithm
                        new_predicted_list =  zip(ids, sentences, sentences_ids, predicted_tags, predicted_sentiment) 
                        MongoForCeleryResults.bulk_insert_predictions(eatery_id, tag_analysis_algorithm.replace("_tag.lib", ""), 
                                        new_predicted_list)
                        print "Length of the new_predicted_list is %s"%len(new_predicted_list)
                        print new_predicted_list[0]

                        MongoForCeleryResults.update_classification_algorithms_reviews(not_already_tokenized_n_predicted, prediction_algorithm_name)


                
                all_sentences = list()
                for review in review_list:
                        all_sentences.extend(MongoForCeleryResults.review_result(review[0], prediction_algorithm_name))
               

                result = list()

                print all_sentences[0:2]
                print "Length of all the sentences for this eatery %s"%len(all_sentences)

                for __dsf_sentence in all_sentences:
                        if __dsf_sentence[3] == category:
                            __e = list(__dsf_sentence)
                            __e.insert(0, eatery_id)
                            result.append(__e)
	        logger.info("{color} Length of the result is ---<{length}>--- with type --<{type}>--".format(color=bcolors.OKBLUE,\
                        length=len(result), type=type(result)))
               
                list_of_dictionaries = [{"eatery_id": eatery_id,
                                        "review_id": __dsf_sentence[1],
                                        "sentence": __dsf_sentence[2],
                                        "sentence_id": __dsf_sentence[3],
                                        "tag": __dsf_sentence[4],
                                        "sentiment": __dsf_sentence[5],
                                        } for __dsf_sentence in result]
                print list_of_dictionaries[0]
                return list_of_dictionaries

        def after_return(self, status, retval, task_id, args, kwargs, einfo):
		logger.info("{color} Ending --<{function_name}--> of task --<{task_name}>-- with time taken\
                        --<{time}>-- seconds  {reset}".format(color=bcolors.OKBLUE,\
                        function_name=inspect.stack()[0][3], task_name= self.__class__.__name__, 
                            time=time.time() -self.start, reset=bcolors.RESET))
		pass

	def on_failure(self, exc, task_id, args, kwargs, einfo):
		logger.info("{color} Ending --<{function_name}--> of task --<{task_name}>-- failed fucking\
                        miserably {reset}".format(color=bcolors.OKBLUE,\
                        function_name=inspect.stack()[0][3], task_name= self.__class__.__name__, reset=bcolors.RESET))
                logger.info("{0}{1}".format(einfo, bcolors.RESET))
		self.retry(exc=exc)


@app.task()
class MappingList(celery.Task):
	max_retries=3, 
	acks_late=True
	default_retry_delay = 5
	"""
        To start:
        celery -A ProcessingCeleryTask  worker -n MappingListOne -Q MappingListQueue --concurrency=4 --loglevel=info                  
        Time to execute:
            Generlly in milliseconds as it just do mapping
        
        This worker just executes a parelled exectuion on the result returned by ReviewIdToSentTokenizeQueue by mappping 
        each element of the result to each SentTokenizeToNPQueue worker 
        
        Errors:
                tag_analysis_algorithm: svm_linear_kernel_classifier_tag.lib 
                sentiment_analysis_algorithm: svm_linear_kernel_classifier_sentiment.lib
                The name svm_linear_kernel_classifier_sentiment.lib can't be passed to callback, because
                it is not json serializable

        """
        def run(self, it, ner_algorithm, word_tokenization_algorithm, pos_tagging_algorithm, noun_phrases_algorithm, 
                                    tag_analysis_algorithm, sentiment_analysis_algorithm, callback):
                self.start = time.time()
                callback = subtask(callback)
                tag_analysis_algorithm = tag_analysis_algorithm.replace("_tag.lib", "")
                sentiment_analysis_algorithm = sentiment_analysis_algorithm.replace("_sentiment.lib", "")



	        return group(callback.clone([arg, ner_algorithm, word_tokenization_algorithm, pos_tagging_algorithm, 
                        noun_phrases_algorithm, tag_analysis_algorithm, sentiment_analysis_algorithm]) for arg in it)()

        
        def after_return(self, status, retval, task_id, args, kwargs, einfo):
		#exit point of the task whatever is the state
		logger.info("{color} Ending --<{function_name}--> of task --<{task_name}>-- with time taken\
                        --<{time}>-- seconds  {reset}".format(color=bcolors.OKBLUE,\
                        function_name=inspect.stack()[0][3], task_name= self.__class__.__name__, 
                            time=time.time() -self.start, reset=bcolors.RESET))
		pass

	def on_failure(self, exc, task_id, args, kwargs, einfo):
		logger.info("{color} Ending --<{function_name}--> of task --<{task_name}>-- failed fucking\
                        miserably {reset}".format(color=bcolors.OKBLUE,\
                        function_name=inspect.stack()[0][3], task_name= self.__class__.__name__, reset=bcolors.RESET))
                logger.info("{0}{1}".format(einfo, bcolors.RESET))
		self.retry(exc=exc)




"""
ReviewIdToSentTokenize
Tasks achieved
    <<Task1>>: 
            itertate over the concerned review ids
                        #If the sentences for this reviews is present in the database, and are classified according to the prediction 
                        #algorithm given in the api call
            if senteces fo this review is present:
                    predicted_reviews.append(review_id)

            else:
                    not_predicted_reviews.append(review_id)



    <<Task2>>: Pushing tokenized sentences of the review_id to the reviews_result_collection for the review id into the list
            sentence_ids
            After this operation, every review id in the not_predicted_reviews, will have entry in reviews_result_collection
            like mentioned below
                        u'review_id': u'3261061',
                                'sentence_ids': 
                                        [
                                        [u'78ab0df69d5a35a5b59e9b233acf8971','we reached on a sat night @ 9.30 pm 
                                        and after entering realized we were the First one to enter'],
                                        
                                        [u'd41d8cd98f00b204e9800998ecf8427e', u''],
                                        [u'd8575920feabdf646849a0729415a7bc', u':- ( dj was playing good tracksnuce 
                                        dimly lit place , and after a long time had a good Hukka ( As in Mumbai Hukka 
                                                                                    r banned ) Pizza was very oily ..'],
                                        [u'5f38e4ff99eb21c9d353fb0e63fa4287', u'cottage Cheese Starter was okay okay ...'],
                                        [u'00bd724c96e5ba203293342c1b064fb1', u"nothing Good or badand half of the stock listed 
                                                                        in their Menu was not available that's a sad part ."],
                                                                        
                                        [u'681eeb8360875a6013392a5414330256', u'rude guys at reception so Beware ...'],
                                        [u'ea35bf08199115cca8d324e66bd0829c', u"once u go out u can't enter back ...."],
                                        [u'ce5b2b0810e6eba2a18415e450a4da8c', u'strange Rule ..'],
                                        [u'7d3ab83ef752ce88b1c64e9ccf4dba5c', u'and a Turn offwould advice another place instead of this']]}
                                        
            A list was also created with all the sentences present in it for all the reviews                        
            
            ids_sentences.append(list(
                                                            (element[0], 
                                                            __sentence.encode("ascii", "xmlcharrefreplace"), 
                                                            hashlib.md5(__sentence.encode("ascii", "xmlcharrefreplace")).hexdigest()))) 
    
    <<Task3>>:
                Now a new list was created for every sentence which was made by tokenizing every review in 
                    not_predicted_reviews

                ids_sentences is now broken into seperated list for the purpose of being classified

                ids = review_ids from which the sentences being generated after being tokenized
    
                ids, sentences, sentences_ids = map(list, zip(*ids_sentences))

                predicted_tags = tag_classification(tag_analysis_algorithm, sentences)
                predicted_sentiment = sentiment_classification(sentiment_analysis_algorithm, sentences)

                #Inserting tag and sentiment correponding to senences ids
                #right now tag_analysis_algorithm shall be same as sentiment_analysis_algorithm
                
                new_predicted_list =  zip(ids, sentences, sentences_ids, predicted_tags, predicted_sentiment) 
                Inserting all the new sentences with their prediction algorithm name and their predictions into 
                the sentences_result_collection

                MongoForCeleryResults.bulk_insert_predictions(eatery_id, tag_analysis_algorithm.replace("_tag.lib", ""), 
                                        new_predicted_list)
                            
                This operation now stores every sentence like mentioned below in sentences_result_collection
                {u'_id': ObjectId('550bfb009f987a75f9931489'),
                        'eatery_id': u'307036',
                        'review_id': u'3261061',
                        'sentence': u"once u go out u can't enter back ....",
                        'sentence_id': u'ea35bf08199115cca8d324e66bd0829c',
                        'sentiment': {u'svm_linear_kernel_classifier': u'positive'},
                        'tag': {u'svm_linear_kernel_classifier': u'overall'}}

    <<Task4>>: 
            After the completion of the all the above three tasks. mongodb has all the sentences belonging to the
            concerned reviews into it, with the prediction from prediction algorithm given to it.

                                        
                                        

            the sentences for the reviews which were classified previously now being retrieved and then joined to the
            new predicted list
            for review in predicted_reviews:                                        
                    already_predicted_list.extend(MongoForCeleryResults.review_result(review[0], 
                    prediction_algorithm_name))

            
    <<Task4>>:
            new_predicted_list (the list of the sentences which are being precited for the first time)

            already_predicted_list (the list of the sentences which were predicted beforehand and were stored in db)

            aggregated = new_predicted_list+ already_predicted_list

    <<Task5>>:
            the aggregated list is now being filtered for the category which is required for the this particular api call


    Returns:
            All the sentences whther they were already predicted of was predited jsut now, 
            returns a list of lists of this form 
            ["eatery_id", "review_id", "sentence", "sentence_id", "tag", "sentiment"]


NoNounPhrasesReviews:
        <<Task1>>: Made a list of dictionaries out of the list of lists given to it
                list_of_dictionaries = [{"eatery_id": __dsf_[0],
                                        "review_id": __dsf_sentence[1],
                                        "sentence": __dsf_sentence[2],
                                        "sentence_id": __dsf_sentence[3],
                                        "tag": __dsf_sentence[4],
                                        "sentiment": __dsf_sentence[5],
                                        } for __dsf_sentence in result]
                       

        <<Task2>>:
                

"""
