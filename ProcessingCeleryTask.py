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

@app.task()
class PosTagger(celery.Task):
        #Queue: pos_tagger
        max_retries=3, 
	acks_late=False
	default_retry_delay = 5
	def run(self, __sentence_dict):
                """
                Args:
                {"review_id": "6538124", "sentence": "great Food & amp ; Drinks .", 
                                    "sentiment": ["svm_linear_kernel", "super-positive"], 
                                    "tag": ["svm_linear_kernel", "food"]
                                    "word_tokenization: {"punkt_n_treebank": [
                                                                            ]
                                                        },
                                    "pos_tagger": [{"word_tokenizer": "punkt_n_treebank",
                                                    "stan_pos_tagger": []}
                                    ]    
                                                    } 

                __pos_tagger = PosTaggers([__sentence_dict.get("word_tokenization").get("punkt_n_treebank")]) #using default standford pos tagger
                 
                __pos_tagged_sentences =  __pos_tagger.pos_tagged_sentences
                #Updating __pos_tagged_sentences dict with the nameof word tokenizer
                __pos_tagged_sentences.update({"word_tokenizer": "punkt_n_treebank"})

                
                __sentence_dict.update({"pos_tagger": __pos_tagged_sentences})
		
                        
                logger.info("Finished Word tokenization")
                """
                return __sentence_dict
        def after_return(self, status, retval, task_id, args, kwargs, einfo):
		#exit point of the task whatever is the state
		logger.info("Ending run Word Tokenization")
		pass

	def on_failure(self, exc, task_id, args, kwargs, einfo):
		print "fucking faliure occured"
		self.retry(exc=exc)

@app.task()
class WordTokenization(celery.Task):
        #Queue: word_tokenization
        max_retries=3, 
	acks_late=True
	default_retry_delay = 5
	def run(self,  __sentence_dict):
                """
                Args:
                    dictionary with keys as follows
                    review_id: Id of the review from which the sentence has been tokenized
                    sentence:  The sentence
                    sentiment: List of tuples, with each tuple has first element has a algorithm name
                                                an second element as the precited sentiment by this algorithm
                    tag: List of tuples, with each tuple has first element has a algorithm name
                                                an second element as the precited tag by this algorithm


                Result:
                    [{"review_id": "6538124", "sentence": "great Food & amp ; Drinks .", 
                                    "sentiment": ["svm_linear_kernel", "super-positive"], 
                                    "tag": ["svm_linear_kernel", "food"]
                                    "word_tokenization: {"punkt_n_treebank": [
                                                                            ]
                                                        },}, 
                """
                #Other options are, punkt_tokenize, treebank_tokenize, default is punkt_n_treebank
                WORD_TOKENIZATION_ALGORITHM = "punkt_n_treebank"

                word_tokenize = WordTokenize([__sentence_dict.get("sentence")])
                __sentence_dict.update({"word_tokenization": word_tokenize.word_tokenized_list})
		
                        
                logger.info("Finished Word tokenization")
                return __sentence_dict
	
        def after_return(self, status, retval, task_id, args, kwargs, einfo):
		#exit point of the task whatever is the state
		logger.info("Ending run Word Tokenization")
		pass

	def on_failure(self, exc, task_id, args, kwargs, einfo):
		print "fucking faliure occured"
		self.retry(exc=exc)


@app.task()
class Classification(celery.Task):
        #Queue: classification
        max_retries=3, 
	acks_late=True
	default_retry_delay = 5
	def run(self, __sent_tokenized_list):
                """
                Args:
                    tuple (review_id, sentence, sentence_tokenized_list)

                returns:
                 [{"review_id": "6538124", "sentence": "great Food & amp ; Drinks .", "sentiment": ["svm_linear_kernel", "super-positive"], 
                                                                                        "tag": ["svm_linear_kernel", "food"]}, 
                {"review_id": "6538124", "sentence": "food Presentation & amp ; Server were great as well .", 
                                                                                        "sentiment": ["svm_linear_kernel", "super-positive"], 
                                                                                        "tag": ["svm_linear_kernel", "service"]},  
                ]
                """

                result = list()
                ALGORITHM_TAG = "svm_linear_kernel"
                ALGORITHM_SENTIMENT = "svm_linear_kernel"
                whole_list = list()
                for __tuple in __sent_tokenized_list:
                        for sentence in __tuple[2]:
                                whole_list.append((__tuple[0], sentence))

                tag_classifier = joblib.load("Text_Processing/PrepareClassifiers/InMemoryClassifiers/{0}_classifier_tag.lib".format(ALGORITHM_TAG))
                sentiment_classifier =joblib.load("Text_Processing/PrepareClassifiers/InMemoryClassifiers/{0}_classifier_sentiment.lib".format(ALGORITHM_SENTIMENT))
                predicted_tags = tag_classifier.predict([__tuple[1] for __tuple in whole_list])
                predicted_sentiments = sentiment_classifier.predict([__tuple[1] for __tuple in whole_list])
                
                for __ in zip(whole_list, predicted_tags, predicted_sentiments):
                        result.append({"review_id": __[0][0],
                                        "sentence": __[0][1], 
                                        "tag": (ALGORITHM_TAG, __[1]),
                                        "sentiment": (ALGORITHM_SENTIMENT, __[2])
                                        })


                return result
	
        def after_return(self, status, retval, task_id, args, kwargs, einfo):
		#exit point of the task whatever is the state
		logger.info("Ending run Classification")
		pass

	def on_failure(self, exc, task_id, args, kwargs, einfo):
		print "fucking faliure occured"
		self.retry(exc=exc)



@app.task()
class SentenceTokenization(celery.Task):
        #Queue: sentence_tokenization
        max_retries=3, 
	acks_late=True
	default_retry_delay = 5
	def run(self, eatery_id):
                sent_tokenizer = SentenceTokenizationOnRegexOnInterjections()
                result = [(review.get("review_id"), review.get("review_text"), sent_tokenizer.tokenize(review.get("review_text")))
                                for review in reviews.find({"eatery_id": eatery_id})]
                return result

        
        def after_return(self, status, retval, task_id, args, kwargs, einfo):
		#exit point of the task whatever is the state
		logger.info("Ending run Sentence tokenization")
		pass

	def on_failure(self, exc, task_id, args, kwargs, einfo):
		print "fucking faliure occured"
		self.retry(exc=exc)






@app.task(max_retries=3, retry=True, acks_late= True)
def MappingList(it, callback):
	print callback, 
        print type(callback)
        print it
        # Map a callback over an iterator and return as a group
	callback = subtask(callback)
	return group(callback.clone([arg,]) for arg in it)()


@app.task()
class DoesAll(celery.Task):
	max_retries=3, 
	acks_late=True
	default_retry_delay = 5
	def run(self, review_id):
                review_text = reviews.find_one({"review_id": review_id}).get("review_text")
                sent_tokenizer = SentenceTokenizationOnRegexOnInterjections()
                tokenized_sentences = sent_tokenizer.tokenize(review_text)
                
                ALGORITHM_TAG = "svm_linear_kernel"
                ALGORITHM_SENTIMENT = "svm_linear_kernel"


                ##Nxt lines of the code predicts the tag, sentiment fo rthe tokenized sentences
                tag_classifier = joblib.load("Text_Processing/PrepareClassifiers/InMemoryClassifiers/{0}_classifier_tag.lib".format(ALGORITHM_TAG))
                
                sentiment_classifier =joblib.load("Text_Processing/PrepareClassifiers/InMemoryClassifiers/{0}_classifier_sentiment.lib".format(ALGORITHM_SENTIMENT))
                predicted_tags = tag_classifier.predict(tokenized_sentences)
                predicted_sentiments = sentiment_classifier.predict(tokenized_sentences)
                
                WORD_TOKENIZATION_ALGORITHM = "punkt_n_treebank"

                word_tokenize = WordTokenize(tokenized_sentences)
                word_tokenized_sentences = word_tokenize.word_tokenized_list.get(WORD_TOKENIZATION_ALGORITHM)
                
                __pos_tagger = PosTaggers(word_tokenized_sentences,  default_pos_tagger="stan_pos_tagger") #using default standford pos tagger
                __pos_tagged_sentences =  __pos_tagger.pos_tagged_sentences.get("stan_pos_tagger")


                __noun_phrases = NounPhrases(__pos_tagged_sentences, default_np_extractor = "regex_textblob_conll_np")
                
                result =  __noun_phrases.noun_phrases.get("regex_textblob_conll_np")
                return result

        def after_return(self, status, retval, task_id, args, kwargs, einfo):
		#exit point of the task whatever is the state
		logger.info("Ending")
		pass

	def on_failure(self, exc, task_id, args, kwargs, einfo):
		print "fucking faliure occured in Test"
		self.retry(exc=exc)


@app.task()
class ReviewIds(celery.Task):
	max_retries=3, 
	acks_late=True
	default_retry_delay = 5
	def run(self, eatery_id):
                return [post.get("review_id") for post in reviews.find({"eatery_id": eatery_id})][0:2]

        
        def after_return(self, status, retval, task_id, args, kwargs, einfo):
		#exit point of the task whatever is the state
		logger.info("Ending Test")
		pass

	def on_failure(self, exc, task_id, args, kwargs, einfo):
		print "fucking faliure occured in Test"
		self.retry(exc=exc)







@app.task(max_retries=3, retry=True)
def ProcessEateryId(eatery_id):
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
        first = (SentenceTokenization.s(eatery_id)| Classification.s()| MappingList.s(WordTokenization.s()))()
        


        result = chord(MappingList.s(PosTagger.s()),),
        return result
@app.task()
class Test(celery.Task):
	max_retries=3, 
	acks_late=True
	default_retry_delay = 5
	def run(self, x, y):
                return x +y 

        
        def after_return(self, status, retval, task_id, args, kwargs, einfo):
		#exit point of the task whatever is the state
		logger.info("Ending Test")
		pass

	def on_failure(self, exc, task_id, args, kwargs, einfo):
		print "fucking faliure occured in Test"
		self.retry(exc=exc)


                    
