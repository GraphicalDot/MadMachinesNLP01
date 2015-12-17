#!/usr/bin/env python
"""
Author: kaali
Date: 16 May, 2015
Purpose: Final celery code to be run with tornado
"""
import pymongo
import os
import sys
import warnings
import itertools

file_path = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(file_path)
sys.path.append(parent_dir)

os.chdir(parent_dir)
from connections import reviews, eateries, reviews_results_collection, eateries_results_collection, bcolors
os.chdir(file_path)


class MongoScriptsReviews(object):
        
        @staticmethod
        def return_reviews(eatery_id, start_epoch=None, end_epoch=None):
                if start_epoch and end_epoch:
                        review_list = [post.get("review_id") for post in reviews.find({"eatery_id" :eatery_id, \
                            "converted_epoch": {"$gt":  start_epoch, "$lt" : end_epoch}})]
                else:
                        review_list = [post.get("review_id") for post in reviews.find({"eatery_id" :eatery_id})]
                    
                return review_list

        @staticmethod
        def return_all_reviews(eatery_id):
                review_list = [post.get("review_id") for post in reviews.find({"eatery_id" :eatery_id})]
                return review_list

        @staticmethod
        def return_all_reviews_with_text(eatery_id):
                review_list = [(post.get("review_id"), post.get("review_text"), post.get("review_time")) for post \
                        in reviews.find({"eatery_id" :eatery_id}) if bool(post.get("review_text")) and post.get("review_text") != " "]
                return review_list


        @staticmethod
        def reviews_with_text(reviews_ids):
                review_list = list()
                for review_id in reviews_ids:
                        review = reviews.find_one({"review_id": review_id})
                        review_text, review_time = review.get("review_text"), review.get("review_time")
                        
                        if bool(review_text) and review_text != " ":
                                review_list.append((review_id, review_text, review_time))
                return review_list

        @staticmethod
        def update_review_result_collection(**kwargs):
                review_id = kwargs["review_id"]
                eatery_id = kwargs["eatery_id"]
                review = reviews.find_one({"review_id": review_id}, {"_id": False, "review_text": True, \
                        "converted_epoch": True, "review_time": True})    
                kwargs.update({"review_text": review.get("review_text"), "review_time": review.get("review_time")})

                print reviews_results_collection.update({"review_id": review_id}, {"$set": kwargs}, upsert=True, multi=False)
                eateries_results_collection.update({"eatery_id": eatery_id}, {"$push": \
                                {"processed_reviews": review_id }}, upsert=True)

                return 

        @staticmethod
        def get_proccessed_reviews(eatery_id):
                result = eateries_results_collection.find_one({"eatery_id": eatery_id}, {"_id": False, 
                                    "processed_reviews": True})
  
                try:
                        if result.get("processed_reviews"):
                                return result.get("processed_reviews")
                except Exception as e:
                        print "No processed reviews present"
                        raise StandardError("No processed reviews are present")


        @staticmethod
        def flush_eatery(eatery_id):
                print eateries_results_collection.remove({"eatery_id": eatery_id})
                print reviews_results_collection.remove({"eatery_id": eatery_id})
                return 


        @staticmethod
        def update_eatery_places_cusines(eatery_id, places, cuisines):
            if places or cuisines:    
                    eateries_results_collection.update({"eatery_id": eatery_id}, {"$push": \
                        {"places": places, "cuisines": cuisines }}, upsert=True)


       
        @staticmethod
        def update_processed_reviews_list(eatery_id, review_id):
                eateries_results_collection.update({"eatery_id": eatery_id}, {"$push": {
                    "processed_reviews": review_id}}, upsert=False)

                warnings.warn("{0} Updating processed_review list of eatery --<<{1}>>-- with review_id\
                        {2}{3}".format(bcolors.OKBLUE, eatery_id, review_id, bcolors.RESET))
                return
 




class MongoScriptsDoClusters(object):
        def __init__(self, eatery_id):
                self.eatery_id = eatery_id
                self.eatery_name = eateries.find_one({"eatery_id": self.eatery_id}).get("eatery_name")

        @staticmethod
        def reviews_with_time(review_list):
                for review_id in review_list:
                    result = reviews.find_one({"review_id": review_id}, {"_id": False, "review_time": True})
                    print "The review_id --<<{0}>>-- with review time --<<{1}>>--".format(review_id, result.get("review_time")), "\n"


        def if_no_reviews_till_date(self):
            """
            If no reviews has been written for this eatery till date, 
            which implies that there is no need to run doclusters 
            """
            return reviews.find({"eatery_id": self.eatery_id}).count()



        def processed_clusters(self):
                """
                This returns all the noun phrases that already have been processed for
                teh eatery id 
                """
                return eateries_results_collection.find_one({"eatery_id": self.eatery_id}, 
                            {"_id": False, noun_phrases: True}).get("noun_phrases")

        def old_considered_ids(self):
                """
                Returns review_ids whose noun_phrases has already been taken into account, 
                which means Clusteirng algorithms has already been done on the noun phrases 
                of these review ids and is stored under noun_phrases key of eatery
                nd these review ids has been stored under old_considered_ids
                """
                return eateries_results_collection.find_one({"eatery_id": self.eatery_id}, {"_id": False, 
                            "old_considered_ids": True}).get("old_considered_ids")


        def processed_reviews(self):
                return eateries_results_collection.find_one({"eatery_id": self.eatery_id}, {"_id": False, 
                            "processed_reviews": True}).get("processed_reviews")

        def fetch_reviews(self, category, review_list=None):
                if not review_list:
                        review_list = eateries_results_collection.find_one({"eatery_id": \
                                self.eatery_id}).get("processed_reviews")


                if category == "food":
                        food = [reviews_results_collection.find_one({"review_id": review_id})\
                            ["classification"][TAG_CLASSIFY_ALG_NME][SENTI_CLSSFY_ALG_NME]\
                            ["food"][FOOD_SB_CLSSFY_ALG_NME][NOUN_PHSE_ALGORITHM_NAME] for review_id in  review_list]
                        flatten_food = list(itertools.chain(*food))
                        
                        ##Checks if the food sub classification tab has beenchanged or not
                        if set.difference(set([e[3] for e in flatten_food]), set(FOOD_SUB_TAGS)):
                                print set.symmetric_difference(set([e[3] for e in flatten_food]), set(FOOD_SUB_TAGS))
                                raise StandardError("Food sub classification has been changed,\
                                            Do something about it fuckerrrr, One way to solve this problem\
                                            is to flush whole database with food category, also food noun\
                                            phrases stored in the eatery")


                        return flatten_food          
                        
                        
       
                    
                result = [reviews_results_collection.find_one({"review_id": review_id})["classification"][
                    TAG_CLASSIFY_ALG_NME][SENTI_CLSSFY_ALG_NME][category]\
                        [eval("{0}_SB_CLSSFY_ALG_NME".format(category.upper()[0:4]))] for review_id in \
                        review_list]
                
                result = list(itertools.chain(*result))
                if set.difference(set([e[3] for e in result]), set(eval("{0}_SUB_TAGS".format(category.upper()[0:4])))):
                        raise StandardError("{0} sub classification has been changed,\
                                            Do something about it fuckerrrr, One way to solve this problem\
                                            is to flush whole database with {0} category".format(category))

               
                #[[u'super-positive', u'ambience-overall'], [u'super-positive', u'ambience-overall'], 
                #[u'neutral', u'ambience-overall']]
                return [[sentiment, sub_tag, review_time] for (sent, tag, sentiment, sub_tag, review_time) in result]


        def update_food_sub_nps(self, np_result, food_sub_category):
                try:    
                    eateries_results_collection.update({"eatery_id": self.eatery_id}, {"$set": {
                        "food.{0}".format(food_sub_category): np_result}}, upsert=False)
                except Exception as e:
                        raise StandardError(e)
                return 
        
        def fetch_nps_frm_eatery(self, category, sub_category=None):
                if category == "food":
                        if not sub_category:
                                raise StandardError("Food Category shall be provided to fecth nps")
                        return eateries_results_collection.find_one({"eatery_id": self.eatery_id}).get(category).get(sub_category)
                        
                return eateries_results_collection.find_one({"eatery_id": self.eatery_id}).get(category)

        def update_considered_ids(self, review_list=None):
                """
                Updating considered ids, Adding review ids to eateries considered_ids list, Thre reviews ids
                for which the noun phrases of all categories has been added to respective lists in eateries
                
                if reviews_list is not present updated old_considered_ids with all the ids present 
                in processed_reviews list of the eatery
                """
                if not review_list:
                        review_list = eateries_results_collection.find_one({"eatery_id":\
                                    self.eatery_id}).get("processed_reviews")
                
                print "This is the fucking review list %s"%review_list
                try:
                        eateries_results_collection.update({"eatery_id": self.eatery_id}, {"$push": \
                                {"old_considered_ids": {"$each": review_list }}}, upsert=False)

                except Exception as e:
                        raise StandardError(e)
                return

        def update_nps(self, category, category_nps):
                """
                Update new noun phrases to the eatery category list
                """
                try:
                    eateries_results_collection.update({"eatery_id": self.eatery_id}, {"$set": {category:
                    category_nps}}, upsert=False)
                except Exception as e:
                    raise StandardError(e)
                return 








