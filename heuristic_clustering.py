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
                
                self.list_to_exclude = ["food", "service", "cost", "ambience", "delhi", "Delhi", "place", "Place", __eatery_name.lower().split()]
                self.list_to_exclude = flatten(self.list_to_exclude)
                self.data = __result
                self.new_data = self.merge_similar_elements()
                self.keys = self.new_data.keys()
                self.similar_strings = list()
                self.clusters = list()
                self.result = list()

                self.filter_clusters()
                self.without_clusters =  set.difference(set(range(0, len(self.keys))), set(flatten(self.clusters)))
        
                self.populate_result()
                self.result = sorted(self.result, reverse=True, key= lambda x: x.get("positive") + x.get("negative"))

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

        def filter_clusters(self):
            """

            """
            X = np.zeros((len(self.new_data), len(self.new_data)), dtype=np.float)
       
            for i in xrange(0, len(self.keys)):
                    for j in xrange(0, len(self.keys)):
                            st = 'Levenshtein.ratio("{1}", "{0}")'.format(self.keys[i], self.keys[j])
                            ratio = eval(st)
                            X[i][j] = ratio
                            if ratio >.8:
                                    if i != j:
                                            if [j ,i] not in self.similar_strings:
                                                    self.similar_strings.append([i, j])
                            
                                            if not bool(self.clusters):
                                                    self.clusters.append([i, j])
                                            else:
                                                    n = 0
                                                    #print "This is i = %s and this is j = %s"%(i, j)
                                                    found = False
                                                    for __c in self.clusters:
                                                            if i in __c or j in __c:
                                                                    l = self.clusters[n]
                                                                    l.extend([i, j])
                                                                    self.clusters[n] = l  
                                                                    found = True
                                                                    break
                                                            n += 1
                                                    if not found:
                                                            self.clusters.append([i, j])
            #Removing duplicate elements from clusters list
            self.clusters = [list(set(element)) for element in self.clusters]
            return 

        def populate_result(self):
        
                for __int_key in self.without_clusters:
                        new_dict = dict()
                        name = self.keys[__int_key]
                        new_dict = self.new_data[name]
                        new_dict.update({"name": name})
                        self.result.append(new_dict)

                for cluster_list in self.clusters:
                        __dict = self.maximum_frequency(cluster_list)
                        self.result.append(__dict)

                return

        def maximum_frequency(self, cluster_list):
                """
                Returning name with maximum frequency in a cluster, by joining all the frequencies
                """
                result = list()
                positive, negative = int(), int()
                positive_name, negative_name = str(), str()
                for element in cluster_list:
                        name = self.keys[element]    
                        new_dict = self.new_data[name]
                        new_dict.update({"name": name})
                        result.append(new_dict)        
                        positive = positive +  self.new_data[name].get("positive") 
                        negative = negative +  self.new_data[name].get("negative") 
        
        
                result = sorted(result, reverse= True, key=lambda x: x.get("positive"))
                return {"name": result[0].get("name"), "positive": positive, "negative": negative}


"""
if __name__ == "__main__":
        payload = {'category': 'food',
             'eatery_id': '4571',
              'ner_algorithm': 'stanford_ner',
               'pos_tagging_algorithm': 'hunpos_pos_tagger',
                'total_noun_phrases': 15,
                 'word_tokenization_algorithm': 'punkt_n_treebank'}

        r = requests.post("http://localhost:8000/get_word_cloud", data=payload)
        m = HeuristicClustering(r.json()["result"])

"""

