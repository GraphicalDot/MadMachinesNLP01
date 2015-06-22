#!/usr/bin/env python
"""
Author: kaali
Dated: 9 June, 2015
Purpose: This is the script that will be used to populate elastic search on remote node
The purpose of the elastic search to solve the problem of query resolution

Configuring Details:
        each index in Elasticsearch is allocated 5 primary shards and 1 replica which means that if you have at least two nodes in\
                your cluster, your index will have 5 primary shards and another 5 replica shards (1 complete replica) for a total of 10 shards per index.
    
        So we will have 26 indexes char-a, char-b etc
        Then we will have two types 
        char-a/dishes/
        char-a/restaurants/

        char-a/dishes/ will have all the dishes starting with character "a"
        char-a/restaurants/ will have all the restaurants with their name starting with character "a"

        


        so in case of scaling we can move indexes and shards, so at the full capacity we can have
        130 nodes, 5 shards for each dish-* and 5 replica set for each.




https://www.elastic.co/guide/en/elasticsearch/reference/current/_executing_searches.html
##To match exact phrase
        body ={"query" :{
            "match_phrase" :{
                    "name": "chicken pieces"}}}



This example composes two match queries and returns all accounts containing "mill" and "lane" in the address:
{ "query": {"bool":{ "must": [
            {"match" : {"address": "mill"}},
            {"match" : {"address": "lane"}}
            ]}
                        }}

In contrast, this example composes two match queries and returns all accounts containing "mill" or "lane" in the address:
    {"query": {
        "bool": {
            "should": [{"match" :{"address": "mill" }},
                        { "match" :{"address": "lane" } }
                        ]}
                }}


The cache is not enabled by default, but can be enabled when creating a new index as follows:

    curl -XPUT localhost:9200/my_index -d'
    {
      "settings": {
          "index.cache.query.enable": true
            }
            }
            '

#To list all the indices
http://192.168.1.14:9200/_cat/indices?v


#To print mapping
http://192.168.1.14:9200/food/_mapping?pretty=true




Schema:
    Elastic search
    To start with we will have some shards


Task1:
        To incorporate new dishes for the same restaurant

Task2:
        Auto complete options as the user types in the string to be searched


Task3: Match the strng like "chiken tikkka" with the dishes stored in the database


Task4: Match other factors like service, ambience, and cost with the dishes


Task5:
     


Task3:
        




"""


import os
import sys
from compiler.ast import flatten
file_name = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(file_name)
from GlobalConfigs import ES


class ElasticSearchScripts(object):
        def __init__(self):
                pass


        
        def initial(self, eatery_id):
                """
                Used to initially update the data
                For every eatery stored in mongodb, We have four keys asscoaited with that post
                food, service, cost, ambience

                For these corresponding keys we will have sub keys associated with it, For ex
                food tag has these keys associated with it.
                [u'menu-food', u'overall-food', u'sub-food', u'place-food', u'dishes']
                service:
                """
                return 


        @staticmethod
        def upde_dish_for_rest(dish_name, eatery_id, eatery_name):
                """
                This method takes in three arguments dish_name, eatery_name, eatery_id
                """




        def flush(self, index_name):
                return


        @staticmethod
        def auto_complete(__str):
                """
                Returns lists of dishes name else returm empy list
                """
                search_body={"fields": ["name"], 
                        "query": {
                                "prefix": {
                                    "name": __str
                                        }}}


                search_body = {
                            "query" : {
                                "multi_match" : {
                                        "fields" : ["name", "similar"],
                                        "query" : __str,
                                        "type" : "phrase_prefix"
                                                                                        }
                                            }
                            }

                result = ES.search(index='food', doc_type='dishes', body=body)
                return flatten([e["fields"]["name"] for e in result["hits"]["hits"]])

        @staticmethod
        def exact_dish_match(__str):
                search_body = {"query":
                        {"match_phrase": 
                                {"name": __str}
                        }



        @staticmethod
        def dish_suggestions(__str):
                """
                Case1:
                    if actual resul couldnt be found
                Case2: 
                    To be sent along with the actual result
                return Suggestions for the __str
                """
                search_body =  body = {"fields": ["name", "similar"],
                        "query" : {
                            "multi_match" : {"fields" : ["name", "similar"],
                                            "query" : __str,
                                            "type" : "phrase_prefix"
                                                                                    }
                                        }}

                ##if you dont need score, also filter searchs are very fast to executed
                #and can be cached
                body= { "query" : {
                                    "filtered" : { 
                                                    "query" : {
                                                                        "match_all" : {} 
                                                                                    },
                                                                "filter" : {
                                                                                    "term" : { 
                                                                                                            "name" : "chicken"
                                                                                                                            }
                                                                                                }
                                                                        }
                                        }
                        }

                        
                result = ES.search(index='food', doc_type='dishes', body=body)
                








