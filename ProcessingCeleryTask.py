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
from processing_celery_app.App import app
from celery.registry import tasks
import logging
import inspect
from celery import task, group
from sklearn.externals import joblib
import time
connection = pymongo.Connection()
db = connection.intermediate
collection = db.intermediate_collection
from Text_Processing import WordTokenize, PosTaggers, SentenceTokenizationOnRegexOnInterjections, bcolors, NounPhrases

logger = logging.getLogger(__name__)

db = connection.modified_canworks
reviews = db.review

ALGORITHM_TAG = "svm_linear_kernel"
ALGORITHM_SENTIMENT = "svm_linear_kernel"


TAG_CLASSIFIER = joblib.load("Text_Processing/PrepareClassifiers/InMemoryClassifiers/{0}_classifier_tag.lib".format(ALGORITHM_TAG))
SENTIMENT_CLASSIFIER =joblib.load("Text_Processing/PrepareClassifiers/InMemoryClassifiers/{0}_classifier_sentiment.lib".format(ALGORITHM_SENTIMENT))

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


@app.task(ignore_result=True, max_retries=3, retry=True)
def eateries_list(url, number_of_restaurants, skip, is_eatery):
	print "{color} Execution of the function {function_name} starts".format(color=bcolors.OKBLUE, function_name=inspect.stack()[0][3])
	eateries_list = scrape_links(url, number_of_restaurants, skip, is_eatery)
	return eateries_list


"""





@app.task(max_retries=3, retry=True, acks_late= True)
def MappingList(it, callback):
	print callback, 
        print type(callback)
        print it
        # Map a callback over an iterator and return as a group
	callback = subtask(callback)
	return group(callback.clone([arg,]) for arg in it)()


@app.task()
class SentTokenizeToNP(celery.Task):
	max_retries=3, 
	acks_late=True
	default_retry_delay = 5
	def run(self, __sentence):
                """
                Args:
                    __sentence is a tuple with first element as its review id from which it have been generated and
                    the second element of the tuple is sentence itself
                """
                predicted_tags = TAG_CLASSIFIER.predict([__sentence[1]])[0]
                predicted_sentiment = SENTIMENT_CLASSIFIER.predict([__sentence[1]])[0]
               
                sentence = __sentence[1]
                WORD_TOKENIZATION_ALGORITHM = "punkt_n_treebank"

                word_tokenize = WordTokenize([sentence])
                ##word_tokenized_sentences = word_tokenize.word_tokenized_list.get(WORD_TOKENIZATION_ALGORITHM)
                word_tokenized_sentence = word_tokenize.word_tokenized_list.get(WORD_TOKENIZATION_ALGORITHM)
               
                    
                __pos_tagger = PosTaggers(word_tokenized_sentence,  default_pos_tagger="hunpos_pos_tagger") #using default standford pos tagger
                __pos_tagged_sentences =  __pos_tagger.pos_tagged_sentences.get("hunpos_pos_tagger")


                
                __noun_phrases = NounPhrases(__pos_tagged_sentences, default_np_extractor = "regex_textblob_conll_np")
                
                noun_phrases =  __noun_phrases.noun_phrases.get("regex_textblob_conll_np")
                
                return (__sentence[0], __sentence[1], predicted_tags, predicted_sentiment, word_tokenized_sentence, __pos_tagged_sentences, noun_phrases)

        def after_return(self, status, retval, task_id, args, kwargs, einfo):
		#exit point of the task whatever is the state
		logger.info("Ending")
		pass

	def on_failure(self, exc, task_id, args, kwargs, einfo):
		print "fucking faliure occured in Doesall Function"
		self.retry(exc=exc)


@app.task()
class ReviewIdToSentTokenize(celery.Task):
	max_retries=3, 
	acks_late=True
	default_retry_delay = 5
	def run(self, eatery_id, start_epoch, end_epoch):
                sent_tokenizer = SentenceTokenizationOnRegexOnInterjections()
                result = list()
                review_list = [(post.get("review_id"), post.get("review_text")) for post in 
                            reviews.find({"eatery_id" :eatery_id, "converted_epoch": {"$gt":  start_epoch, "$lt" : end_epoch}})]
                for element in review_list:
                        for __sentence in sent_tokenizer.tokenize(element[1]): 
                                result.append((element[0], __sentence.encode("ascii", "xmlcharrefreplace")))

                logger.warning("Lenght of the reviews list is %s"%len(result))
                return result[0:400]
        
        def after_return(self, status, retval, task_id, args, kwargs, einfo):
		#exit point of the task whatever is the state
		logger.info("Ending Review ids task")
		pass

	def on_failure(self, exc, task_id, args, kwargs, einfo):
		print "fucking faliure occured in Test"
		self.retry(exc=exc)




@app.task(max_retries=3, retry=True, acks_late=True)
def ProcessEateryId(eatery_id, category, start_epoch, end_epoch, word_tokenization_algorithm, pos_tagging_algorithm, noun_phrases_algorithm):
        #process_list = SentenceTokenization.s(eatery_id) | MappingList.s(Classification.s())
        """
        Queue: process_eatery_id
        
        Getting result of the below mentioned task
                for element in zip(__noun_phrases.noun_phrases.get("textblob_np_conll"), [__text[2] for __text in filtered_tag_text]):
        [element.get() for element in result.children[0]]
                for element in zip(__noun_phrases.noun_phrases.get("textblob_np_conll"), [__text[2] for __text in filtered_tag_text]):

                for element in zip(__noun_phrases.noun_phrases.get("textblob_np_conll"), [__text[2] for __text in filtered_tag_text]):
                for element in zip(__noun_phrases.noun_phrases.get("textblob_np_conll"), [__text[2] for __text in filtered_tag_text]):
        """
        result = (ReviewIdToSentTokenize.s(eatery_id, start_epoch, end_epoch)| MappingList.s(SentTokenizeToNP.s(category, word_tokenization_algorithm, pos_tagging_algorithm, noun_phrases_algorithm)))()
        return result


                    
