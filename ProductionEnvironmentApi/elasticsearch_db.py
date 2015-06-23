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


step1:
        Define setting for elastic search indexes 
                indexing references:
                
                reference1 : http://www.spacevatican.org/2012/6/3/fun-with-elasticsearch-s-children-and-nested-documents/


        make indexes into the elastic search

        make mappings into elastic search

        make analyzer on elastic search
            https://www.elastic.co/guide/en/elasticsearch/guide/current/analysis-intro.html
            for the time being we are going to use the standard analyzer
        

For each eatery update the es with dishes
    with each dish having a eatery_id and lat long for eatery stored with it

update char_h for eatery
    eatery details to be inserted 




If a new review comes in, watch for the noun phrases that has been changed and update es
same goes for eatery



so for ex user search for chicken, 
    dishes starting with chicken for eateries with eatries details
    the problem is do we need to also take similr dishes into account or not


Prolem Statement:
        Query: I need to have chicken tikka and chicken peri peri in a place 5km from my current location, with nice decor and 
        value for money


        Query2:
                nice decor within 5km

Resolution1:
        sentence tokenization:
            dishes: chicken tikka and chicken peri peri
            location : within 5 km, suggestion in 10 km 
            ambience: nice decor
            cost: value for money


        

Now ES:
        Step1:
            if Search dish1 and dish2 with common eatery:
                return eateries
            elseif :
                search dish1 or dish2 with eateries:
                    combine the resut
            else:
                search levenshtein 

            
        sort according to the location nearest being in 5km


Query Resolution 2:
        find all within 5km and then sort according to total decor



                



buk insertion and update are possible








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
from elasticsearch import Elasticsearch
from elasticsearch import RequestError

def analyzer():
        """
        Analyzers are composed of a single Tokenizer and zero or more TokenFilters. The tokenizer may be preceded 
        by one or more CharFilters. The analysis module allows you to register Analyzers under logical names which 
        can then be referenced either in mapping definitions or in certain APIs.
        Elasticsearch comes with a number of prebuilt analyzers which are ready to use. Alternatively, you can 
        combine the built in character filters, tokenizers and token filters to create custom analyzers.
        http://gibrown.com/2013/04/17/mapping-wordpress-posts-to-elasticsearch/
  

        curl -X POST 'http://localhost:9200/thegame/_close'     
        curl -X PUT 'http://localhost:9200/thegame/_settings' -d 

        curl -X POST 'http://localhost:9200/thegame/_open

        curl 'localhost:9200/test/_analyze?pretty=1&analyzer=my_edge_ngram_analyzer' -d 'FC Schalke 04'


        http://stackoverflow.com/questions/27804354/elasticsearch-use-custom-analyzer-on-filter



{
   "query": {
      "bool": {
         "must": [
            {
               "match": {
                  "title": "post"
               }
            },
            {
               "nested": {
                  "path": "seller",
                  "query": {
                     "match": {
                        "seller.firstName": {
                            "query": "Test 3",
                            "operator": "and"
                        }
                     }
                  }
               }
            }
         ]
      }
   }
}'


               {
"settings": {
    "analysis": {
         "analyzer": {
             "standardWithEdgeNGram": {
                 "tokenizer": "standard",
                 "filter": ["lowercase", "edgeNGram"]
             }
         },
         "tokenizer": {
             "standard": {
                 "type": "standard"
             }
         },
         "filter": {
             "lowercase": {
                "type": "lowercase"
            },
            "edgeNGram": {
                "type": "edgeNGram",
                "min_gram": 2,
                "max_gram": 15,
                "token_chars": ["letter", "digit"]
            }
        }
    }
},

"""


class ElasticSearchScripts(object):
        def __init__(self):
                """
                Will have minimum two indexes
                one for dishes and one for eateries
                """
                
                pass



        @staticmethod
        def __settings_es(__index_name, delete_index=False):
                """
                Update the settings lke number of shards and replicas on elsticsearch
                
                This will specifies the number of shards = 20 and number of replicas 2 for the __index name given to it,

                The purpose of such a high number of shards is that later on, when we would expect a increase in load, 
                The shards could be shifted to new servers

                More reference here: http://blog.qbox.io/building-an-elasticsearch-index-with-python
                """
                client = Elasticsearch()
                query = {'settings': {
                                    'number_of_shards': 20,
                                    'number_of_replicas': 2,
                                    }
                        }
                try:
                        client.indices.create(index=__index_name, body=query)
                except Exception:
                        if delete_index:
                                client.indices.delete(index = __index_name)
                                client.indices.create(index=__index_name, body=query)
                        else:
                                print "Index settings for Index {0} already exists".format(__index_name)
                
        @staticmethod
        def __shards_analyze_mapping_es(__index_name):
                """
                Can be done only on the index level

                We have to declare nested type for nested documents in es mapping 
                so that es will stop treating them as flat objects 
                More is available here: https://www.elastic.co/blog/managing-relations-inside-elasticsearch


                This arrangement does come with some disadvantages. Most obvious, you can only access these nested 
                documents using a special ` nested query`. Another big disadvantage comes when you need to update 
                the document, either the root or any of the objects.
                
                To check whether the analyzer is udated or not
                curl 'http://192.168.1.2:9200/dishes/_analyze?pretty=1&analyzer=custom_analyzer' -d 'FC Schalke 04'

                """
                client.indices.get_mapping(index=__index_name)
                client.indices.get_settings(index=__index_name)

                __body = {'settings': {
                                    'number_of_shards': 5,
                                    'number_of_replicas': 2,
                        
                        
                                    
                        "analysis": {
                        "filter": {
                                "snowball": { "type": "snowball", "language": "English" },
                                "english_stemmer": { "type": "stemmer", "language": "english" },
                                "english_possessive_stemmer": { "type": "stemmer", "language": "possessive_english" },
                                "stopwords": { "type": "stop",  "stopwords": [ "_english_" ] },
                                "worddelimiter": { "type": "word_delimiter" }
                            },
         
                        "tokenizer": {
                                "nGram": { "type": "nGram", "min_gram": 1, "max_gram": 20 }
                            },
                
                        "analyzer": {
                                "custom_analyzer": {
                                        "type": "custom",
                                        "tokenizer": "nGram",
                                        "filter": [
                                                "stopwords",
                                                "asciifolding",
                                                "lowercase",
                                                "snowball",
                                                "english_stemmer",
                                                "english_possessive_stemmer",
                                                "worddelimiter"
                                                ]
                                                },
                        
                                "custom_search_analyzer": {
                                            "type": "custom",
                                            "tokenizer": "edgeNGram",
                                        "filter": [
                                                "stopwords",
                                                "asciifolding",
                                                "lowercase",
                                                "snowball",
                                                "english_stemmer",
                                                "english_possessive_stemmer",
                                                "worddelimiter"]
                                                }
                                    }}, 
                                }}

  
        def _change_default_analyzer(__index_name):
                client.indices.close(index=__index_name)
                body = {"index": {
                                "analysis": {
                                        "analyzer": {
                                                "default": {
                                                        "type": "custom_analyzer"}}}}}

                client.indices.put_settings(index=__index_name, body=body)

                client.indices.open(index=__index_name)
                return 


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
                        "mappings": {
                                "name": {
                                        "properties": {
                                                    "name": {
                                                            "type": "string",
                                                            "analyzer": "custom_analyzer",
                                                            },
                                                    "similar": {
                                                            "type": "nested",
                                                             "properties": {
                                                                    "name": {
                                                                            "type": "string", 
                                                                                    "index_analyzer": "custom_analyzer", 
                                                                                    "search_analyzer": "custom_search_analyzer",
                                                                                },
                                                                    'negative': { "type": "int"
                                                                                },
                                                                    'neutral': {"type": "int"
                                                                                },
                                                                    'positive': {"type": "int"
                                                                                },
                                                                    'super-negative': {"type": "int"
                                                                        },
                                                                    'super-positive': {"type": "int"
                                                                                },
                                                                    'timeline': {"type": "string"
                                                                            }
                                                             }
                                                            }
                                                        }
                                            }},


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
                








