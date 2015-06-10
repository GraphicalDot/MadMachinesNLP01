#!/usr/bin/env python
"""
Author: kaali
Dated: 9 June, 2015
Purpose: This is the script that will be used to populate elastic search on remote node
The purpose of the elastic search to solve the problem of query resolution


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
                








