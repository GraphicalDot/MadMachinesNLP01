#!/usr/bin/env python

"""
Author: Kaali
Dated: 9 march, 2015
Purpose: This module deals with the clustering of the noun phrases, Evverything it uses are heuristic rules because
till now i am unable to find any good clutering algorithms which suits our needs.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
import requests
import numpy as np
from sklearn.cluster import MeanShift, estimate_bandwidth
import Levenshtein
import codecs
import nltk
from compiler.ast import flatten
import time
import progressbar
from collections import Counter



class HeuristicClustering:
        def __init__(self, __result, __eatery_name):
                """
                Args:
                    __result
                            type: list of dictionaries
                            example: [{'positive': 20, 'name': u'teppanyaki grill', 'negative': 12}, 
                            {'positive': 8, 'negative': 10, 'name': u'main course'}, {'positive': 7, 'negative': 8, 'name': u'kylin'}]
                """
                
                if __eatery_name:
                        self.list_to_exclude = ["food", "service", "cost", "ambience", "delhi", "Delhi", 
                                "place", "Place", __eatery_name.lower().split()]
                else:
                        self.list_to_exclude = ["food", "service", "cost", "ambience", "delhi", "Delhi", "place", "Place"]
                
                self.list_to_exclude = flatten(self.list_to_exclude)
                self.data = __result
                print "Length of the old data after exclusion %s"%len(self.data)
                
                self.result = self.merge_similar_elements()
        
        def merge_similar_elements(self):
                """
                Merging noun phrases who have exact similar spellings with each other and return a dictionary in the form
                u'ice tea': {'positive', 6, 'negative': 5},
                u'iced tea': {'positive', 2, 'negative', 10},
                u'icelolly': {'positive': 0, 'negative', 1},
                }
                """
        
                without_similar_elements = dict()
                for i in self.data:
                        if bool(set.intersection(set(i.get("name").split(" ")),  set(self.list_to_exclude))):
                                pass    

                        elif without_similar_elements.get(i.get("name")):
                                result = without_similar_elements.get(i.get("name"))
                                polarity = "negative" if i.get("polarity") == 0 else "positive"
                        
                                if polarity == "negative":
                                        new_frequency_negative = result.get("negative") + i.get("frequency")
                                else:
                                        new_frequency_negative = result.get("negative")


                                if polarity == "positive":
                                        new_frequency_positive = result.get("positive") + i.get("frequency")
                                else:
                                        new_frequency_positive = result.get("positive")
                                
                                without_similar_elements.update(
                                    {i.get("name"): 
                                        {"negative": new_frequency_negative,
                                        "positive": new_frequency_positive,
                                        }})

                
                        else:
                                without_similar_elements.update(
                                    {i.get("name"): 
                                        {"negative" if i.get("polarity") == 0 else "positive": i.get("frequency"),
                                        "negative" if i.get("polarity") == 1 else "positive": 0,
                                        }})

                return without_similar_elements


