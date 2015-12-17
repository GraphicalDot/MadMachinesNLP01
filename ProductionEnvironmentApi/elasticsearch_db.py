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

from elasticsearch import Elasticsearch, helpers
from elasticsearch import RequestError

ES_CLIENT = Elasticsearch(ELASTICSEARCH_IP, timeout=30)
NUMBER_OF_DOCS = 10
#localhost:9200/test/_analyze?analyzer=whitespace' -d 'this is a test'
#curl -XGET "http://192.168.1.4:9200/food/_analyze?analyzer=custom_analyzer&pretty=1" -d "cheesecake"

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
                self.other_mappings = {'properties': {'eatery_id': {'type': 'string'},
                                                    'eatery_name': {'type': 'string'},
                                                    'location': {'type': 'geo_point'},
                                                    'mention_factor': {'type': 'double'},
                                                    'negative': {'type': 'long'},
                                                    'neutral': {'type': 'long'},
                                                    'positive': {'type': 'long'},
                                                    'super-negative': {'type': 'long'},
                                                    'super-positive': {'type': 'long'},
                                                    'timeline': {'type': 'string'},
                                                    'total_sentiments': {'type': 'long'},
                                                    'trending_factor': {'type': 'double'}}}

                """
                if not ES_CLIENT.indices.exists("food"):
                        self.prep_food_index()
                        
                
                if not ES_CLIENT.indices.exists("ambience"):
                        self.prep_ambience_index()
                
                if not ES_CLIENT.indices.exists("cost"):
                        self.prep_cost_index()
                
                if not ES_CLIENT.indices.exists("service"):
                        self.prep_service_index()
                """
                if renew_indexes:
                        self.prep_food_index()
                        
                        print "{0}Deleting INDEX=<<ambience>> {1}".format(bcolors.FAIL, bcolors.RESET)
                        try:
                                ES_CLIENT.indices.delete(index="ambience")
                        except Exception as e:
                                print e
                        
                        print "{0}Deleting INDEX=<<cost>> {1}".format(bcolors.FAIL, bcolors.RESET)
                        try:
                                ES_CLIENT.indices.delete(index="cost")
                        except Exception as e:
                                print e
                        print "{0}Deleting INDEX=<<service>> {1}".format(bcolors.FAIL, bcolors.RESET)
                        try:
                                ES_CLIENT.indices.delete(index="service")
                        except Exception as e:
                                print e

                        print "{0}Creating INDEX=<<ambience>> {1}".format(bcolors.OKGREEN, bcolors.RESET)
                        self.prep_ambience_index()
                        
                        print "{0}Creating INDEX=<<cost>> {1}".format(bcolors.OKGREEN, bcolors.RESET)
                        self.prep_cost_index()
                        
                        print "{0}Creating INDEX=<<service>> {1}".format(bcolors.OKGREEN, bcolors.RESET)
                        self.prep_service_index()
                return 

        def prep_ambience_index(self):
                ES_CLIENT.indices.create(index="ambience")
                for __sub_category in AMBI_SUB_TAGS:
                                ES_CLIENT.indices.put_mapping(index="ambience", doc_type=__sub_category, body = {__sub_category: self.other_mappings })
                                print "{0}Mappings updated for  {1}  {2}".format(bcolors.OKGREEN, __sub_category, bcolors.RESET)
            
        def prep_cost_index(self):
                ES_CLIENT.indices.create(index="cost")
                for __sub_category in COST_SUB_TAGS:
                                ES_CLIENT.indices.put_mapping(index="cost", doc_type=__sub_category, body = {__sub_category: self.other_mappings })
                                print "{0}Mappings updated {1} for {2}".format(bcolors.OKGREEN, __sub_category, bcolors.RESET)
        
            
        def prep_service_index(self):
                ES_CLIENT.indices.create(index="service")
                for __sub_category in SERV_SUB_TAGS:
                                ES_CLIENT.indices.put_mapping(index="service", doc_type=__sub_category, body = {__sub_category: self.other_mappings })
                                print "{0}Mappings updated {1} for {2}".format(bcolors.OKGREEN, __sub_category, bcolors.RESET)

        def prep_food_index(self):
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

                __settings = {'settings': 
                                    {'analysis': 
                                            {'analyzer': 
                                                    {'custom_analyzer': {
                                                                'filter': ['lowercase', 'asciifolding'],
                                                                'tokenizer': 'ngram_tokenizer',
                                                                'type': 'custom'},
                                                                
                                                        'custom_analyzer_two': {'filter': ['lowercase', 'asciifolding'],
                                                                'tokenizer': 'limited_tokenizer',
                                                                'type': 'custom'},
                                                
                                                        'keyword_analyzer': {
                                                            'filter': ['lowercase', 'asciifolding'],
                                                            'tokenizer': 'keyword',
                                                            'type': 'custom'},
                                                    
                                                        'phonetic_analyzer': {
                                                                'filter': ['lowercase', 'asciifolding', 'standard', 'custom_metaphone'],
                                                                'tokenizer': 'whitespace',
                                                                'type': 'custom'},
                                                        
                                                        'shingle_analyzer': {
                                                                'filter': ['lowercase', 'asciifolding', 'shingle_tokenizer'],
                                                                'tokenizer': 'ngram_tokenizer',
                                                                'type': 'custom'},
                                                            
                                                        'standard_analyzer': {
                                                                    'filter': ['lowercase', 'asciifolding'],
                                                                    'tokenizer': 'standard',
                                                                    'type': 'custom'}
                                                        },
                                                                 
                                                    'filter': {
                                                            'custom_metaphone': {'encoder': 'metaphone',
                                                                        'replace': False,
                                                                        'type': 'phonetic'},
                                                                                 
                                                            'shingle_tokenizer': {'max_shingle_size': 5,
                                                                                    'min_shingle_size': 2,
                                                                                    'type': 'shingle'}
                                                            },
                                                                                    
                                                    'tokenizer': {
                                                            'limited_tokenizer': {
                                                                        'max_gram': '10',
                                                                        'min_gram': '2',
                                                                        'token_chars': ['letter', 'digit'],
                                                                        'type': 'edgeNGram'},
                                                                                                           
                                                            'ngram_tokenizer': {'max_gram': 100,
                                                                                'min_gram': 2,
                                                                                'token_chars': ['letter', 'digit'],
                                                                                'type': 'edgeNGram'}
                                                            }
                                                    }
                                                    }
                                        }








                print "{0}Settings updated {1}".format(bcolors.OKGREEN, bcolors.RESET)

                ES_CLIENT.indices.create(index="food", body=__settings)
                __mappings = {'dishes': {'_all': {'enabled': True},
                          'properties': {
                                    'dish_phonetic': {'analyzer': 'phonetic_analyzer', 'type': 'string'},
                                    'dish_raw': {'analyzer': 'keyword_analyzer', 'type': 'string'},
                                    'dish_shingle': {'analyzer': 'shingle_analyzer', 'type': 'string'},
                                    "dish_autocomplete": { 'analyzer': 'custom_analyzer', 'type': 'string'}, 
                                        
                                        'eatery_id': {'index': 'not_analyzed', 'type': 'string'},
                                              'eatery_name': {'copy_to': ['eatery_shingle', 'eatery_raw', 'eatery_autocomplete'],
                                                      'type': 'string'},
                                                "eatery_autocomplete": { 'analyzer': 'custom_analyzer', 'type': 'string'}, 
                                                 'eatery_raw': {'analyzer': 'keyword_analyzer', 'type': 'string'},
                                                    'eatery_shingle': {'analyzer': 'shingle_analyzer', 'type': 'string'},
                                                       'location': {'type': 'geo_point'},
                                                          'mention_factor': {'type': 'double'},
                                                             'name': {'copy_to': ['dish_raw', 'dish_shingle', 'dish_phonetic', 'dish_autocomplete'],
                                                                     'type': 'string'},
                                                                'negative': {'type': 'long'},
                                                                   'neutral': {'type': 'long'},
                                                                      'positive': {'type': 'long'},
                                                                         'similar': {'properties': {'name': {'copy_to': ['dish_raw',
                                                                                    'dish_shingle',
                                                                                           'dish_phonetic', 'dish_autocomplete'],
                                                                                                 'type': 'string'},
                                                                                                      'negative': {'type': 'long'},
                                                                                                           'neutral': {'type': 'long'},
                                                                                                                'positive': {'type': 'long'},
                                                                                                                     'super-negative': {'type': 'long'},
                                                                                                                          'super-positive': {'type': 'long'},
                                                                                                                               'timeline': {'type': 'string'}}},
                                                                            'super-negative': {'type': 'long'},
                                                                               'super-positive': {'type': 'long'},
                                                                                  'timeline': {'type': 'string'},
                                                                                     'total_sentiment': {'type': 'integer'},
                                                                                        'trending_factor': {'type': 'double'}}}}

                    
                    
                    

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
                latitude, longitude = eatery.get("eatery_coordinates")
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
                                                __dish.update({"location": {"lon": longitude, "lat": latitude}})
                                                l = ES_CLIENT.index(index="food", doc_type=sub_category, body=__dish)
                                                print l 
                                else:
					try:
                                        	sub_data = data[sub_category]
                                        	sub_data.update({"eatery_id": eatery_id})
                                        	sub_data.update({"eatery_name": eatery_name})
                                                sub_data.update({"location": {"lon": longitude, "lat": latitude}})

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
        def dish_suggestions(dish_name):
                
                body = {"_source": ["name"],
                        "from": 0, 
                        "size": 10, 
                                "query": {
                                        "match": {
                                                "dish_autocomplete": {     
                                                        "query":    dish_name,    
                                                        "analyzer": "standard" 
                                                                    }
                                                }
                                        }
                            }

                dish_suggestions = ES_CLIENT.search(index="food", doc_type="dishes", body=body)
                return ElasticSearchScripts.process_result(dish_suggestions) 
        
        @staticmethod
        def eatery_suggestions(dish_name):
                
                body = {"_source": ["eatery_name"],
                        "from": 0, 
                        "size": 10, 
                                "query": {
                                        "match": {
                                                "eatery_autocomplete": {     
                                                        "query":    dish_name,    
                                                        "analyzer": "standard" 
                                                                    }
                                                }
                                        }
                            }

                dish_suggestions = ES_CLIENT.search(index="food", doc_type="dishes", body=body)
                return ElasticSearchScripts.process_result(dish_suggestions) 











        @staticmethod
        def must_eat():
                """
                """

                food_body = {"_source": ["name", "location", "eatery_name", "eatery_id", "positive", "negative", "neutral", "super-positive", "super-negative", "total_sentiments"],
                        "from": 0, 
                        "size": 10, 
                        "sort": [
                                {"trending_factor" : {"order" : "desc"}}
                                ],
                        "query": {
                                "match_all": {}
                                            },
                        }

                trending_dishes = ES_CLIENT.search(index="food", doc_type="dishes", body=food_body)
                return ElasticSearchScripts.process_result(trending_dishes),  
                        



        @staticmethod
        def get_trending(latitude, longitude):
                """
                """

                food_body = {"_source": ["name", "location", "eatery_name", "eatery_id", "positive", "negative", "neutral", "super-positive", "super-negative", "total_sentiments"],
                        "from": 0, 
                        "size": 10, 
                        "sort": [
                                {"trending_factor" : {"order" : "desc"}}
                                ],
                        "query": {
                                "match_all": {}
                                            },
                        "filter": {
                                "geo_distance": {
                                        "distance": "5km",
                                        "location": {
                                                "lat": latitude,
                                                "lon": longitude
                                                    }
                                                }     
                                }
                        }

                trending_dishes = ES_CLIENT.search(index="food", doc_type="dishes", body=food_body)
                
                ambience_body = {"_source": ["name", "location", "eatery_name", "eatery_id", "positive", "negative", "neutral", "super-positive", "super-negative", "total_sentiments"],
                        "from": 0, 
                        "size": 2, 
                        "sort": [
                                {"trending_factor" : {"order" : "desc"}}
                                ],
                        "query": {
                                "match_all": {}
                                            },
                        "filter": {
                                "geo_distance": {
                                        "distance": "5km",
                                        "location": {
                                                "lat": latitude,
                                                "lon": longitude
                                                    }
                                                }     
                                }
                        }
                
                trending_ambience = ES_CLIENT.search(index="ambience", doc_type="ambience-overall", body=ambience_body)
                cost_body = {"_source": ["name", "eatery_name", "location", "eatery_id", "positive", "negative", "neutral", "super-positive", "super-negative", "total_sentiments"],
                        "from": 0, 
                        "size": 2, 
                        "sort": [
                                {"trending_factor" : {"order" : "desc"}}
                                ],
                        "query": {
                                "match_all": {}
                                            },
                        "filter": {
                                "geo_distance": {
                                        "distance": "5km",
                                        "location": {
                                                "lat": latitude,
                                                "lon": longitude
                                                    }
                                                }     
                                }
                        }
                
                trending_cost = ES_CLIENT.search(index="cost", doc_type="value for money", body=cost_body)
                
                service_body = {"_source": ["name", "eatery_name", "location", "eatery_id", "positive", "negative", "neutral", "super-positive", "super-negative", "total_sentiments"],
                        "from": 0, 
                        "size": 2, 
                        "sort": [
                                {"trending_factor" : {"order" : "desc"}}
                                ],
                        "query": {
                                "match_all": {}
                                            },
                        "filter": {
                                "geo_distance": {
                                        "distance": "5km",
                                        "location": {
                                                "lat": latitude,
                                                "lon": longitude
                                                    }
                                                }     
                                }
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

        @staticmethod
        def match_for_eatery(eatery_name):
            """
            When a user searched for the exact eatery or enters a eatery_name which is not present in the 
            elastic search, For this to be executed successfully
            First: We will searhc for the exact eatery name, if that fails
            First can be searched in the mongodb Itself
            
            Second : We will search search for the fuzzy match for that eatery name
            """
            
            return 

            
        @staticmethod
        def get_dishes(__dish_name, number_of_dishes=None, number_of_suggestions=None):
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
                        number_of_dishes = 30
                


                def find_exact_match(__dish_name, number_of_dishes):
                        exact_dish_search_body={"_source": ["name", "eatery_name", "eatery_id", "location", "positive", "negative", "neutral", "super-positive", "super-negative", "total_sentiments"],
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
                        print "Fussy match for %s"%__dish_name
                        fuzzy_search_body = {"_source": ["name", "eatery_name", "eatery_id", "location", "positive", "negative", "neutral", "super-positive", "super-negative", "total_sentiments"],
                                "query": {
                                    "fuzzy_like_this": {
                                            "fields": ["dish_shingle", "dish_raw"],
							"like_text": __dish_name,  
                                                        "fuzziness": 6,
                                                        "max_query_terms": 25,
						        "boost": 1, 
						        "prefix_length": 0, 
						        "ignore_tf": False,  
                                                    }},
                                            
                                "from": 0,
                                "size": number_of_dishes,
                                }
                        __result = ES_CLIENT.search(index="food", doc_type="dishes", body=fuzzy_search_body)
                        __result = ElasticSearchScripts.process_result(__result)
                        return __result


                def find_standard_match(__dish_name, number_of_dishes):
                        standard_search_body = {"_source": ["name", "eatery_name", "eatery_id", "location", "positive", "negative", "neutral", "super-positive", "super-negative", "total_sentiments"],
                                "query": {
                                    "match": {
                                            "name": {
                                                    "query": __dish_name,
                                                    }}},
                                            
                                "from": 0,
                                "size": number_of_dishes,
                                "sort": [
                                            {"trending_factor": {
                                                    "order" : "desc"}}
                                           ],
                                }
                        __result = ES_CLIENT.search(index="food", doc_type="dishes", body=standard_search_body)
                        __result = ElasticSearchScripts.process_result(__result)
                        return __result

                
                print "FInished Dish passed in suggest_dish instance of ElasticSearchScripts is %s"%__dish_name
                result = find_exact_match(__dish_name, number_of_dishes)
                if result:
                        return result
                else:
                        print "There is no exact result matching the Query %s"%__dish_name
                
                result = find_fuzzy_match(__dish_name, number_of_dishes)
                
                if result:
                        return result
                
                
                return None


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

                

if __name__ == "__main__":
            """
    
            """
            ElasticSearchScripts(renew_indexes=True)

