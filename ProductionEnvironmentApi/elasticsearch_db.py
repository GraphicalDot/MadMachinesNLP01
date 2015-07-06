#!/usr/bin/env python
"""
https://gist.github.com/lightsuner/5df39112b8507d15ede6
https://gist.github.com/lukas-vlcek/5143799
http://192.168.1.5:9200/_cluster/state?pretty&filter_nodes=true&filter_routing_table=true&filter_indices=dishes

Author: kaali
Dated: 9 June, 2015
"""

import requests
import time
import os
import sys
from itertools import ifilter
from compiler.ast import flatten
file_name = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(file_name)
from GlobalConfigs import ES_CLIENT, eateries_results_collection, bcolors, ELASTICSEARCH_IP
from GlobalAlgorithmNames import FOOD_SUB_TAGS, COST_SUB_TAGS, AMBI_SUB_TAGS, SERV_SUB_TAGS

from elasticsearch import Elasticsearch, helpers
from elasticsearch import RequestError

ES_CLIENT = Elasticsearch(ELASTICSEARCH_IP)
NUMBER_OF_DOCS = 10
#localhost:9200/test/_analyze?analyzer=whitespace' -d 'this is a test'
class ElasticSearchScripts(object):
        def __init__(self, renew_indexes=False):
                """
                Will have minimum two indexes
                one for dishes and one for eateries
                FOOD_SUB_TAGS = ['dishes', 'menu-food', 'null-food', 'overall-food', 'place-food', 'sub-food']
                COST_SUB_TAGS = ['cheap', 'cost-null', 'expensive', 'not worth', 'value for money']
                SERV_SUB_TAGS = ['booking', 'management', 'presentation', 'service-null', 'service-overall',\
                'staff', 'waiting-hours']

                AMBI_SUB_TAGS = [u'ambience-null', 'ambience-overall', 'crowd', 'dancefloor', 'decor', \'
                in-seating', 'music', 'open-area', 'romantic', 'smoking-zone', 'sports', 'sports-screens', 'view']

                Index:
                        food:
                                _type: dishes
                                _type: overall
                                _type: menu ##How is the menu
                                _type: place
                                _type: cusine ##Will have cusinine asscociated with it like italian, mexican
                        cost:
                                __type:
                                __type:
                                __type:
                                __type:
                        ambience:
                                __type: overall
                                __type: crowd
                                __type: dancefloor
                                __type: decor
                                __type: inseating
                                __type: music
                                __type: openarea
                                __type: romantic
                                __type: smoking-zone
                                __type: sports
                                __type: sportss
                                __type: view
                        service:
                                __type: booking
                                __type: management
                                __type: presentation
                                __type: overall
                                __type: staff
                                __type: waitinghours
                    
                """
                
                if not ES_CLIENT.indices.exists("food"):
                        ElasticSearchScripts.prep_food_index()
                        
                
                if not ES_CLIENT.indices.exists("ambience"):
                        ElasticSearchScripts.prep_ambience_index()
                
                if not ES_CLIENT.indices.exists("cost"):
                        ElasticSearchScripts.prep_cost_index()
                
                if not ES_CLIENT.indices.exists("service"):
                        ElasticSearchScripts.prep_service_index()

                if renew_indexes:
                        ElasticSearchScripts.prep_food_index()
                        print "{0}Deleting INDEX=<<ambience>> {1}".format(bcolors.FAIL, bcolors.RESET)
                        ES_CLIENT.indices.delete(index="ambience")
                        print "{0}Deleting INDEX=<<cost>> {1}".format(bcolors.FAIL, bcolors.RESET)
                        ES_CLIENT.indices.delete(index="cost")
                        print "{0}Deleting INDEX=<<service>> {1}".format(bcolors.FAIL, bcolors.RESET)
                        ES_CLIENT.indices.delete(index="service")

                        print "{0}Creating INDEX=<<ambience>> {1}".format(bcolors.OKGREEN, bcolors.RESET)
                        ElasticSearchScripts.prep_ambience_index()
                        print "{0}Creating INDEX=<<cost>> {1}".format(bcolors.OKGREEN, bcolors.RESET)
                        ElasticSearchScripts.prep_cost_index()
                        print "{0}Creating INDEX=<<service>> {1}".format(bcolors.OKGREEN, bcolors.RESET)
                        ElasticSearchScripts.prep_service_index()
                return 

        @staticmethod
        def prep_ambience_index():
                ES_CLIENT.indices.create(index="ambience")
            
        @staticmethod
        def prep_cost_index():
                ES_CLIENT.indices.create(index="cost")
        
            
        @staticmethod
        def prep_service_index():
                ES_CLIENT.indices.create(index="service")

        @staticmethod
        def prep_food_index():
                """
                Two indexes will be created one for the restaurants and one for the dishes
                index:
                        eateries
                            type:
                                eatery
                        dishes:
                                dish
                """
                try:
                        ES_CLIENT.indices.delete(index="food")
                        print "{0} DELETING index {1}".format(bcolors.OKGREEN, bcolors.RESET)
                except Exception as e:
                        print "{0} {1}".format(bcolors.FAIL, bcolors.RESET)
                        print "{0} Index Food doesnt exists {1}".format(bcolors.FAIL, bcolors.RESET)
                        print e

                __settings = {
                                "settings": {
                                        "analysis": {
                                                "analyzer": {
                                                        "phonetic_analyzer": {
                                                            "type": "custom",
                                                            "tokenizer" : "whitespace",
                                                            "filter": ["lowercase", "asciifolding", "standard", "custom_metaphone"],
                                                                    },
                                                        "keyword_analyzer": {
                                                            "type": "custom",
                                                            "tokenizer" : "keyword",
                                                            "filter": ["lowercase", "asciifolding"],
                                                                    },
                                                        "shingle_analyzer": {
                                                            "type": "custom",
                                                            "tokenizer" : "ngram_tokenizer",
                                                            "filter": ["lowercase", "asciifolding", "shingle_tokenizer"],
                                                                    },
                                                        "custom_analyzer": {
                                                            "type": "custom",
                                                            "tokenizer" : "ngram_tokenizer",
                                                            "filter": ["lowercase", "asciifolding"],
                                                                    },
                                                        "custom_analyzer_two": {
                                                            "type": "custom",
                                                            "tokenizer" : "limited_tokenizer",
                                                            "filter": ["lowercase", "asciifolding"],
                                                                    },
                                                        "standard_analyzer": {
                                                                "type": "custom", 
                                                                "tokenizer": "standard",
                                                                "filter": ["lowercase", "asciifolding"],
                                                                }
                                                        },
                                                "tokenizer": {
                                                        "ngram_tokenizer": {
                                                                "type" : "edgeNGram",
                                                                "min_gram" : 2,
                                                                "max_gram" : 100,
                                                                "token_chars": [ "letter", "digit" ]
                                                                },
                                                        "limited_tokenizer": {
                                                                "type" : "edgeNGram",
                                                                "min_gram" : "2",
                                                                "max_gram" : "10",
                                                                "token_chars": [ "letter", "digit" ]
                                                                },
                                                        }, 
                                                "filter": {
                                                            "shingle_tokenizer": {
                                                                "type" : "shingle",
                                                                "min_shingle_size" : 2,
                                                                "max_shingle_size" : 5,
                                                                },

                                                            "custom_metaphone": {
                                                                    "type" : "phonetic",
                                                                    "encoder" : "metaphone",
                                                                    "replace" : False
                                                                    }
                                                            }
                                                }
                                        }}

                print "{0}Settings updated {1}".format(bcolors.OKGREEN, bcolors.RESET)

                ES_CLIENT.indices.create(index="food", body=__settings)
                __mappings = {'dishes': {
                                 '_all' : {'enabled' : True},
                                'properties': 
                                                {'name': 
                                                        {
                                                            #'analyzer': 'custom_analyzer', 
                                                            'type': 'string', 
                                                            'copy_to': ['dish_raw', 'dish_shingle', "dish_phonetic"],
                                                            },
                                                    
                                                    
                                        'dish_phonetic': {
                                                    'type': 'string', 
                                                    'analyzer': 'phonetic_analyzer',
                                                    },
                                        'dish_shingle': {
                                                    'type': 'string', 
                                                    'analyzer': 'shingle_analyzer',
                                                    },
                                        'dish_raw': {
                                                    'type': 'string', 
                                                    'analyzer': 'keyword_analyzer',
                                                    },

                                        'eatery_shingle': {
                                                    'type': 'string', 
                                                    'analyzer': 'shingle_analyzer',
                                                    },

                                        'eatery_raw': {
                                                    'type': 'string', 
                                                    'analyzer': 'keyword_analyzer',
                                                    },
                                        
                                        'negative': {'type': 'long'},
                                        'neutral': {'type': 'long'},
                                        'positive': {'type': 'long'},
                                        'similar': {
                                                'properties': {'name': 
                                                                    {
                                                                        'type': 'string', 
                                                                        'copy_to': ['dish_raw', 'dish_shingle', "dish_phonetic"],
                                                                    
                                                                    },
                                                            'negative': {
                                                                     'type': 'long'},
                                                            'neutral': {
                                                                    'type': 'long'},
                                                            'positive': {
                                                                    'type': 'long'},
                                                            'super-negative': {
                                                                    'type': 'long'},
                                                            'super-positive': {
                                                                    'type': 'long'},
                                                            'timeline': {
                                                                'type': 'string'}
                                                            }
                                                },
   
                                        'super-negative': {
                                                    'type': 'long'},
                                        'super-positive': {
                                                    'type': 'long'},
                                        'eatery_name': {
                                                            'type': 'string', 
                                                            'copy_to': ['eatery_shingle', "eatery_raw"],
                                                    },
                                        'eatery_id': {
                                                    'type': 'string', 
                                                    'index': 'not_analyzed',
                                                    },
                                        'total_sentiment': {
                                                    'type': 'integer', 
                                                    },
                                        'timeline': {
                                            'type': 'string'}}}}
                
                try:
                        ES_CLIENT.indices.put_mapping(index="food", doc_type="dishes", body = __mappings)
                        print "{0}Mappings updated {1}".format(bcolors.OKGREEN, bcolors.RESET)
                except Exception as e:
                        print "{0}Mappings update Failed with error {1} {2}".format(bcolors.FAIL, e, bcolors.RESET)

                test_doc = {'eatery_name': u"Karim's", u'name': u'chicken korma', u'super-negative': 0, u'negative': 0, u'super-positive': 1, 
                        u'neutral': 6, u'timeline': [[u'positive', u'2013-01-24 17:34:01'], [u'neutral', u'2014-07-18 23:49:05'], 
                        [u'neutral', u'2014-06-05 13:30:14'], [u'super-positive', u'2013-07-04 17:03:37'], 
                        [u'neutral', u'2013-04-18 20:40:35'], [u'neutral', u'2013-01-18 23:04:17'], 
                        [u'neutral', u'2013-01-11 14:04:49'], [u'neutral', u'2012-12-29 21:51:43']], 'eatery_id': '463', 
                        u'similar': [{u'name': u'chicken qorma', u'positive': 1, u'negative': 0, u'super-positive': 0, u'neutral': 0, 
                            u'timeline': [[u'positive', u'2013-01-24 17:34:01']], u'super-negative': 0}, 
                            {u'name': u'chicken korma', u'positive': 0, u'negative': 0, u'super-positive': 1, u'neutral': 5, 
                                u'timeline': [[u'neutral', u'2014-07-18 23:49:05'], [u'neutral', u'2014-06-05 13:30:14'], 
                                    [u'super-positive', u'2013-07-04 17:03:37'], [u'neutral', u'2013-04-18 20:40:35'], 
                                    [u'neutral', u'2013-01-18 23:04:17'], [u'neutral', u'2013-01-11 14:04:49']], u'super-negative': 0}, 
                                {u'name': u'i order chicken korma', u'positive': 0, u'negative': 0, u'super-positive': 0, u'neutral': 1, 
                                    u'timeline': [[u'neutral', u'2012-12-29 21:51:43']], u'super-negative': 0}], u'positive': 1}
                
                
                print "{0}Updating test data {1}".format(bcolors.OKGREEN, bcolors.RESET)
                l = ES_CLIENT.index(index="food", doc_type="dishes", body=test_doc)

                print "{0}Result:\n {1} {2}".format(bcolors.OKGREEN, l, bcolors.RESET)

                __body = {"query" : {
                            "term" : { "_id" : l.get("_id")}
                                }}

                print "{0}Test Doc deleted {1}".format(bcolors.OKGREEN, bcolors.RESET)
                ES_CLIENT.delete_by_query(index="food", doc_type="dishes", body=__body)

                print "{0}_________ Index Dishes ready to be used _______________{1}".format(bcolors.OKGREEN, bcolors.RESET) 
                return 

        @staticmethod
        def insert_eatery(eatery_id):
                """
                This method deasl with updating or inserting th eatery data into 
                Deals only with four categories food, ambience, service, cost
                """

                delete_body = {
                            "query" : {
                                        "term" : { "eatery_id" : eatery_id }
                                    }
                            }

                #https://people.mozilla.org/~wkahngreene/elastic/guide/reference/api/delete-by-query.html
                try:
                        ES_CLIENT.delete_by_query(index="_all", body=delete_body, consistency="quorum")
                except Exception as e:
                        print "{0}Error occurred while deleting all the entries for the eatery_id {1}{2}".format(\
                                bcolors.FAIL, eatery_id, bcolors.RESET)
                
                
                #Elasticsearch refreshes every index at an interval of 1 second, We need to
                #refresh it for every update
                r = requests.post("http://{0}:9200/_refresh".format(ELASTICSEARCH_IP))
                

                eatery = eateries_results_collection.find_one({"eatery_id": eatery_id})
                eatery_name = eatery.get("eatery_name")
                food_data = eatery["food"]
                ambience_data = eatery["ambience"]
                cost_data = eatery["cost"]
                service_data = eatery["food"]

                for category in ["food", "cost", "ambience", "service"]:
                        data = eatery[category]
                        for sub_category in eval("{0}_SUB_TAGS".format(category[0:4].upper())):
                                
                                if sub_category in ["dishes", "place-food", "sub-food"]:
                                        sub_data = data[sub_category]
                                        for __dish in sub_data:
                                                __dish.update({"eatery_id": eatery_id})
                                                __dish.update({"eatery_name": eatery_name})
                                                l = ES_CLIENT.index(index="food", doc_type=sub_category, body=__dish)
                            
                                else:
					try:
                                        	sub_data = data[sub_category]
                                        	sub_data.update({"eatery_id": eatery_id})
                                        	sub_data.update({"eatery_name": eatery_name})

                                        	l = ES_CLIENT.index(index=category, doc_type=sub_category, body=sub_data)
                                	except Exception as e:
                                        	print sub_category
                                        	print e
                                        	pass

                return 
        def return_dishes(eatery_id):
                """
                Return top 10 dishes filtered on the basis of their total sentiments 
                """
                return 



        @staticmethod
        def process_result(__result):
                result = [l["_source"] for l in __result["hits"]["hits"]]
                return result
       


        @staticmethod
        def convert_time_series(__result):
                n_result = list()

                def __a(__dict, dates):
                        __result = []
                        for date in dates:
                                if __dict[date]:
                                    __result.append(__dict[date])
                                else:
                                    __result.append(0)
                                    
                        return __result

                for element in __result:
                        n_result.append([str(element[0].replace("-", "")), str(element[1].split(" ")[0])])
                sentiments, dates = zip(*n_result)
                dates = sorted(list(set(dates)))

                neutral = __a(Counter([x[1].split(" ")[0] for x in ifilter(lambda x: x[0] == "neutral"\
                                                                                    , n_result)]), dates)
        
                superpositive = __a(Counter([x[1].split(" ")[0] for x in ifilter(lambda x: x[0] == \
                                                                "superpositive" , n_result)]), dates)
        
                supernegative = [-abs(num) for num in __a(Counter([x[1].split(" ")[0] for x in \
                        ifilter(lambda x: x[0] == "supernegative" , n_result)]), dates)]
        
                negative = [-abs(num) for num in __a(Counter([x[1].split(" ")[0] for x in \
                                        ifilter(lambda x: x[0] == "negative" , n_result)]), dates)]
        
                positive = __a(Counter([x[1].split(" ")[0] for x in ifilter(lambda x: x[0] \
                                                            == "positive" , n_result)]), dates)

        
                series = [{"name": e, "data": eval(e)} for e in ["neutral", "superpositive", "supernegative", \
                        "positive", "negative"]]
        
                return {"categories": dates,
                            "series": series}


        @staticmethod
        def get_trending(location):
                """
                """
                food_body = {"_source": ["name", "eatery_name", "positive", "negative", "neutral", "super-positive", "super-negative", "total_sentiments",  "timeline"],
                            "from": 0, 
                            "size": 4, 
                            "query" : {
                                  "match_all": {}
                                     },
                              "sort" : [
                                        {"total_sentiments" : {"order" : "desc"}}
                                           ]
                              }

                trending_dishes = ES_CLIENT.search(index="food", doc_type="dishes", body=food_body)
                
                ambience_body = { "_source": ["name", "eatery_name", "positive", "negative", "neutral", "super-positive", "super-negative", "total_sentiments", "timeline"], 
                            "from": 0, 
                            "size": 2,
                            "query": {
                                    "match_all": {}
                                     },
                            "sort": [
                                    {"total_sentiments": {
                                                "order" : "desc"}}
                                           ]
                              }
                
                trending_ambience = ES_CLIENT.search(index="ambience", doc_type="ambience-overall", body=ambience_body)
                cost_body = { "_source": ["name", "eatery_name", "positive", "negative", "neutral", "super-positive", "super-negative", "total_sentiments",  "timeline"], 
                            "from": 0, 
                            "size": 2,
                            "query": {
                                    "match_all": {}
                                     },
                            "sort": [
                                    {"total_sentiments": {
                                            "order" : "desc"}}
                                           ]
                              }

                
                trending_cost = ES_CLIENT.search(index="cost", doc_type="value for money", body=cost_body)
                service_body = { "_source": ["name", "eatery_name", "positive", "negative", "neutral", "super-positive", "super-negative", "total_sentiments", "timeline"], 
                            "from": 0, 
                            "size": 2,
                            "query": {
                                    "match_all": {}
                                     },
                            "sort": [
                                    {"total_sentiments": {
                                            "order" : "desc"}}
                                           ]
                              }
                trending_service = ES_CLIENT.search(index="service", doc_type="service-overall", body=service_body)
                return {
                        "food": ElasticSearchScripts.process_result(trending_dishes),  
                        "ambience": ElasticSearchScripts.process_result(trending_ambience),  
                        "cost": ElasticSearchScripts.process_result(trending_cost),  
                        "service": ElasticSearchScripts.process_result(trending_service),  
                        }


        def find_eatery_id(self, eatery_id):

                return 

        def suggest_eatery_name(self, suggest_eatery):
                return 



        def elastic_query_processing(self, __query_dict, number_of_dishes=None, dish_suggestions=None):
                """
                Args:
                    {'ambience': ["decor", "overall-ambience"], 'food': {'dishes': [u'Mango Cowboy', u'mango cyrup', 
                                                                    u'mango ice cream']}, 'cost': [], 'service': []}
                
                Returns:
                    {"dishes": [{"match" either a string or list, "suggestions": []}, {}, {}, {}], 
                    "ambience": [{}, {}],
                    "cost": [{}, {}],
                    "service": [{}, {}]}
                
                """
                result = {"food": {}}
                dish_names = __query_dict.get("food").get("dishes")
                dishes = []
                if dish_names:
                        for dish in dish_names:
                                dishes.append(self.suggest_dish(dish, number_of_dishes, dish_suggestions))
                

                else:
                        dishes.append({"match": "No appropriate dishes could be found related to your query", "suggestions": None})

                result["food"]["dishes"] = dishes
                return result

        def suggest_dish(self, __dish_name, number_of_dishes=None, number_of_suggestions=None):
                """
                        dish_suggestions= {
                                   "query":{
                                            "match":{
                                                    "dish_shingle":  __dish_name}},

                                    "from": 0,
                                   "size": dish_suggestions,
                                    "sort":[
                                            {"total_sentiments": {
                                                    "order" : "desc"}}
                                            ]
			            }
                Args:
                        dish_name must be lower case
                        type(string)

                First it will look for the exact dish_name

                Second it will do the fuzzy search, and find the dish similar considering levenshtein distance algorithm, 

                third it will find the dish_names that sound similar to given dish name on the basis of soundex algorithm
                
                Preference of search:
                        Exact match
                        Fuzzy match
                        Phonetic match
                        Standard match
                """
                print "Dish passed in suggest_dish instance of ElasticSearchScripts is %s"%__dish_name
                if not number_of_dishes:
                        number_of_dishes = 2
                
                if not number_of_suggestions:
                        number_of_suggestions = 5

                def find_phonetic_match(__dish_name, number):
                        
                        phonetic_search_body = {
                                "query": {
                                        "match": {
                                            "dish_phonetic": {
                                                    "query": __dish_name,
                                                            "fuzziness": 10,
                                                            "prefix_length": 1}
                                                        }
                                            },
                                    "from": 0,
                                    "size": number_of_dishes,
                                    "sort": [
                                            {"total_sentiments": {
                                                    "order" : "desc"}}
                                           ]

                                    }
                        __result = ES_CLIENT.search(index="food", doc_type="dishes", body=phonetic_search_body)
                        __result = ElasticSearchScripts.process_result(__result)
                        return __result


                def find_exact_match(__dish_name, number_of_dishes):
                        exact_dish_search_body={
                                    "query":{
                                            "term":{
                                                        "dish_raw":  __dish_name}},

                                    "from": 0,
                                    "size": number_of_dishes,
                                    "sort": [
                                            {"total_sentiments": {
                                                    "order" : "desc"}}
                                           ]
                                }

                        __result = ES_CLIENT.search(index="food", doc_type="dishes", body=exact_dish_search_body)
                        __result = ElasticSearchScripts.process_result(__result)
                        return __result

                def find_fuzzy_match(__dish_name, number_of_dishes):
                        fuzzy_search_body = {
                                "query": {
                                    "match": {
                                            "dish_raw": {
                                                    "query": __dish_name,
                                                    "fuzziness": 10,
                                                    "prefix_length": 1
                                                    }}},
                                            
                                "from": 0,
                                "size": number_of_dishes,
                                "sort": [
                                            {"total_sentiments": {
                                                    "order" : "desc"}}
                                           ]}
                        __result = ES_CLIENT.search(index="food", doc_type="dishes", body=fuzzy_search_body)
                        __result = ElasticSearchScripts.process_result(__result)
                        return __result


                def find_standard_match(__dish_name, number_of_dishes):
                        standard_search_body = {
                                "query": {
                                    "match": {
                                            "name": {
                                                    "query": __dish_name,
                                                    }}},
                                            
                                "from": 0,
                                "size": number_of_dishes,
                                "sort": [
                                            {"total_sentiments": {
                                                    "order" : "desc"}}
                                           ]}
                        __result = ES_CLIENT.search(index="food", doc_type="dishes", body=standard_search_body)
                        __result = ElasticSearchScripts.process_result(__result)
                        return __result


                suggestions = find_standard_match(__dish_name, number_of_suggestions)

                print "FInished Dish passed in suggest_dish instance of ElasticSearchScripts is %s"%__dish_name
                result = find_exact_match(__dish_name, number_of_dishes)
                if result:
                        return {"name": __dish_name, "match": result, "suggestions": suggestions}
                
                result = find_fuzzy_match(__dish_name, number_of_dishes)
                if result:
                        return {"name": __dish_name, "match": result, "suggestions": suggestions}
                
                result = find_phonetic_match(__dish_name, number_of_dishes)
                if result:
                        return {"name": __dish_name, "match": result, "suggestions": suggestions}
                
                
                return {"name": __dish_name, "match": "We couldnt find any dish matching your Query %s"%__dish_name, "suggestions": suggestions}



        def return_dishes(eatery_id, number_of_dishes):
                """
                This will return all the dishes related to the particular eatery_id
                """
                if type(eatery_id) != str:
                        raise StandardError("eatery_id should be a string")


                search_body = {                                                   
                            "query":{ 
                                    "match_phrase":{ 
                                                "eatery_id":  eatery_id}}, 
                            "sort": { "total_sentiments": { "order": "desc" } }, 
                            "from": 0,
                            "size": number_of_dishes, 
                          }

                result = ES_CLIENT.search(index="dishes", doc_type="dish", body=search_body)["hits"]["hits"]
                return [e.get("_source") for e in result]
                

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
                For every eatery stored in mongodb, We have four keys asscoaited with that post
                food, service, cost, ambience

                For these corresponding keys we will have sub keys associated with it, For ex
                food tag has these keys associated with it.
                [u'menu-food', u'overall-food', u'sub-food', u'place-food', u'dishes']
                service:
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
                        }}
                return 

                
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

if __name__ == "__main__":
        ElasticSearchScripts(renew_indexes=True)

