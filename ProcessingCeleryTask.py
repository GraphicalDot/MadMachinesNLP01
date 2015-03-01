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

connection = pymongo.Connection()
db = connection.intermediate
collection = db.intermediate_collection
from pymongo.errors import BulkWriteError

logger = logging.getLogger(__name__)

db = connection.modified_canworks
reviews = db.review

ALGORITHM_TAG = ""
ALGORITHM_SENTIMENT = ""

from GlobalConfigs import MONGO_REVIEWS_IP, MONGO_REVIEWS_PORT, MONGO_NLP_RESULTS_IP,\
        MONGO_NLP_RESULTS_PORT, MONGO_NLP_RESULTS_DB, MONGO_NLP_RESULTS_COLLECTION 

from __Celery_APP.App import app
from __Celery_APP.MongoScript import MongoForCeleryResults
from Text_Processing import WordTokenize, PosTaggers, SentenceTokenizationOnRegexOnInterjections, bcolors, NounPhrases,\
                NERs, NpClustering

file_path = os.path.dirname(os.path.abspath(__file__))

"""
status: List active nodes in this cluster
        celery -A ProcessingCeleryTask status

purge: Purge messages from all configured task queues.
        celery -A ProcessingCeleryTask purge


inspect active: List active tasks
        celery -A proj inspect active
        These are all the tasks that are currently being executed.

inspect scheduled: List scheduled ETA tasks
        celery -A proj inspect scheduled
        These are tasks reserved by the worker because they have the eta or countdown argument set.

inspect reserved: List reserved tasks
        celery -A proj inspect reserved

inspect revoked: List history of revoked tasks
        celery -A proj inspect revoked
        
inspect registered: List registered tasks
        celery -A proj inspect registered

inspect stats: Show worker statistics (see Statistics)
        celery -A proj inspect stats
        
control enable_events: Enable events
        celery -A proj control enable_events

control disable_events: Disable events
        celery -A proj control disable_events


To daemonize the celery workers
https://celery.readthedocs.org/en/latest/tutorials/daemonizing.html#daemonizing
-P threads

   The thread pool will execute tasks in separate threads and the --concurrency
      argument controls the maximum number of threads used for that.



To run tasks for scraping one restaurant 
runn.apply_async(["https://www.zomato.com/ncr/pita-pit-lounge-greater-kailash-gk-1-delhi", None, None, True])

TO scrape a list of restaurant use this
runn.apply_async(args=["https://www.zomato.com/ncr/south-delhi-restaurants", 30, 270, False])
	 Task.acks_late
	     If set to True messages for this task will be acknowledged after the task has been executed, 
	     not just before, which is the default behavior.
	
	Task.ErrorMail
	    If the sending of error emails is enabled for this task, then this is the class defining the 
	    logic to send error mails.
	
	Task.store_errors_even_if_ignored
	    If True, errors will be stored even if the task is configured to ignore results.

	
	Task.ErrorMail
	    If the sending of error emails is enabled for this task, then this is the class defining the 
	    logic to send error mails.


	 Task.rate_limit
	     Set the rate limit for this task type which limits the number of tasks that can be run in a 
	     given time frame. Tasks will still complete when a rate limit is in effect, but it may take 
	     some time before it’s allowed to start.
	     If this is None no rate limit is in effect. If it is an integer or float, it is interpreted as 
	     “tasks per second”.
	     The rate limits can be specified in seconds, minutes or hours by appending “/s”, “/m” or “/h” 
	     to the value. Tasks will be evenly distributed over the specified time frame.
	     Example: “100/m” (hundred tasks a minute). This will enforce a minimum delay of 600ms between 
	     starting two tasks on the same worker instance.



"""




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
        def run(self, result, clustering_algorithm_name, number):
                """
                Args:
                    result: A list of list in the form [[u'Subway outlet', u'positive'],
                     [u'subway', u'positive'],
                      [u'bread', u'positive']]

                    number: Maximum number of noun phrases required
                """
                self.start = time.time()
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
                return sorted_result[0: number]


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
	def run(self, __sentence, word_tokenization_algorithm, pos_tagging_algorithm, noun_phrases_algorithm, 
                                    tag_analysis_algorithm, sentiment_analysis_algorithm):
                """
                To Start this worker
                    celery -A ProcessingCeleryTask  worker -n SentTokenizeToNP -Q SentTokenizeToNP --concurrency=4 
                    --loglevel=info 
                
                Estimated Time:
                    generally takes 0.09 to 0.15, Can increase to greater magnitude if used with more slow 
                    pos taggers like standford pos tagger

                Args:
                    __sentence = [id, sentence, predicted_tag, predicted_sentiment]
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
                review_id = __sentence[0]
                sentence = __sentence[1]
                sentence_id = __sentence[2]
                tag = __sentence[3]
                sentiment = __sentence[4]


                word_tokenization_algorithm_result, pos_tagging_algorithm_result,\
                        noun_phrases_algorithm_result = MongoForCeleryResults.retrieve_document(sentence_id, word_tokenization_algorithm,\
                        pos_tagging_algorithm, noun_phrases_algorithm)


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
                        MongoForCeleryResults.insert_pos_tagging_result(sentence_id,
                                                                            word_tokenization_algorithm, 
                                                                            pos_tagging_algorithm, 
                                                                            pos_tagging_algorithm_result)


                if not noun_phrases_algorithm_result:
                        __noun_phrases = NounPhrases(pos_tagging_algorithm_result, default_np_extractor=noun_phrases_algorithm)
                        noun_phrases_algorithm_result =  __noun_phrases.noun_phrases.get(noun_phrases_algorithm)
                        MongoForCeleryResults.insert_noun_phrases_result(sentence_id, 
                                                                            word_tokenization_algorithm, 
                                                                            pos_tagging_algorithm, 
                                                                            noun_phrases_algorithm, 
                                                                            noun_phrases_algorithm_result)
               
                __return_sentiment = lambda noun_phrase: (noun_phrase, sentiment)

                return map(__return_sentiment, flatten(noun_phrases_algorithm_result))

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
	def run(self, eatery_id, category, start_epoch, end_epoch, tag_analysis_algorithm, sentiment_analysis_algorithm,):
                start = time.time()
                """
                Start This worker:
                    celery -A ProcessingCeleryTask  worker -n ReviewIdToSentTokenizeOne -Q ReviewIdToSentTokenizeQueue 
                        --concurrency=4 --loglevel=info
                
                How it Works:
                    Get all the review for the particular eatery_id, 
                    for every review checks the MongoForCeleryResults.if_review(review[0], prediction_algorithm_name)
                    function, if the sentences for this review_id for the prediction_algorithm_name is present
                    this function returns True, else False

                    already_predicted_list: All the reviews which have already been predicted and
                                            db has their tokenized sentences present in it with prediction
                                            done by prediction_algorithm_name

                    new_predicted_list: Opposite of already_predicted_list
                        all the review texts for the review_ids present in this list, then be sentence tokenized
                        and then a bulk insert on mongodb has been done
                        MongoForCeleryResults.bulk_insert_predictions(eatery_id, tag_analysis_algorithm.replace("_tag.lib", ""), 
                                        new_predicted_list)


                Args:
                    eatery_id: 
                            type: str
                            Id of the eatery for which the reviews has to be classfied and the noun phrases to be found
                    start_epoch: float
                            1324173248.0
                            Start time for the reviews
                    end_epoch: 
                            type: float
                            1424173248.0
                            End time for the reviews

                    tag_analysis_algorithm: 
                            type: str
                            Name of the algortihm that shall be used for tag classification

                    sentiment_analysis_algorithm:
                            type: str
                            Name of the algortihm that shall be used for tag classification
                
                Returns:
                        type: List of lists, which each list is of four elements
                        (id, sentence, sentence_id, predicted_tag, predicted_sentiment)
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
                        


                
                predicted_reviews, not_predicted_reviews = list(), list()

                for review in review_list:
                        if MongoForCeleryResults.if_review(review[0], prediction_algorithm_name):
                                predicted_reviews.append(review)
                        else:
                                not_predicted_reviews.append(review)

                
                ##This for loop inserts all the sentences in the mongodb, independent of the category
                ##they belongs to, 

                new_predicted_list, already_predicted_list = list(), list()
                if bool(not_predicted_reviews):
                        for element in not_predicted_reviews:
                                for __sentence in sent_tokenizer.tokenize(element[1]): 
                                        ids_sentences.append(list((element[0], __sentence.encode("ascii", "xmlcharrefreplace"), 
                                                            hashlib.md5(__sentence.encode("ascii", "xmlcharrefreplace")).hexdigest()))) 
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
                

                if bool(predicted_reviews): #Only to run when predicted_reviews list is non empty
                        for review in predicted_reviews:
                                already_predicted_list.extend(
                                        MongoForCeleryResults.review_result(review[0], prediction_algorithm_name))


                aggregated = new_predicted_list +  already_predicted_list


                result = [list(element) for element in aggregated if element[3] == category]
	        logger.info("{color} Length of the result is ---<{length}>--- with type --<{type}>--".format(color=bcolors.OKBLUE,\
                        length=len(result), type=type(result)))

                return result
        
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
        def run(self, it, word_tokenization_algorithm, pos_tagging_algorithm, noun_phrases_algorithm, 
                                    tag_analysis_algorithm, sentiment_analysis_algorithm, callback):
                self.start = time.time()
                callback = subtask(callback)
                tag_analysis_algorithm = tag_analysis_algorithm.replace("_tag.lib", "")
                sentiment_analysis_algorithm = sentiment_analysis_algorithm.replace("_sentiment.lib", "")



	        return group(callback.clone([arg, word_tokenization_algorithm, pos_tagging_algorithm, 
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

@app.task()
class Prediction(celery.Task):
	def run(self, sentences, prediction_algorithm_name):
                self.start = time.time()


                classifier_path = "{0}/Text_Processing/PrepareClassifiers/InMemoryClassifiers/".format(file_path)
                classifier = joblib.load("{0}{1}".format(classifier_path, prediction_algorithm_name))
                return list(classifier.predict(sentences))

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
class ProcessEateryId(celery.Task):
	def run(self, eatery_id, category, start_epoch, end_epoch, word_tokenization_algorithm, pos_tagging_algorithm, 
                                                    noun_phrases_algorithm, tag_analysis_algorithm, sentiment_analysis_algorithm):
                self.start = time.time()
                result = (ReviewIdToSentTokenize.s(eatery_id, category, start_epoch, end_epoch, tag_analysis_algorithm, 
                    sentiment_analysis_algorithm, word_tokenization_algorithm, pos_tagging_algorithm, noun_phrases_algorithm)|
                        MappingList.s(SentTokenizeToNP.s()))()
                
                return result

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



                    
