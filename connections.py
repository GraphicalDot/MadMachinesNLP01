#!/usr/bin/env python


import pymongo
import ConfigParser
from sklearn.externals import joblib
import os
import jsonrpclib
from simplejson import loads


this_file_path = os.path.dirname(os.path.abspath(__file__))

config = ConfigParser.RawConfigParser()
config.read("variables.cfg")



path_for_classifiers = "%s/Text_Processing/PrepareClassifiers/InMemoryClassifiers/newclassifiers"%(this_file_path) 

sentiment_classifier = joblib.load("%s/%s"%(path_for_classifiers, config.get("algorithms", "sentiment_classification_library")))
tag_classifier = joblib.load("%s/%s"%(path_for_classifiers, config.get("algorithms", "tag_classification_library")))
food_sb_classifier = joblib.load("%s/%s"%(path_for_classifiers, config.get("algorithms", "food_algorithm_library")))
ambience_sb_classifier = joblib.load("%s/%s"%(path_for_classifiers, config.get("algorithms", "ambience_algorithm_library")))
service_sb_classifier = joblib.load("%s/%s"%(path_for_classifiers, config.get("algorithms", "service_algorithm_library")))
cost_sb_classifier = joblib.load("%s/%s"%(path_for_classifiers, config.get("algorithms", "cost_algorithm_library")))
                         


data_db_connection = pymongo.MongoClient(config.get("dataDB", "ip"), config.getint("dataDB", "port"))
data_db = data_db_connection[config.get("dataDB", "database")]

reviews = data_db[config.get("dataDB", "reviews")]
eateries = data_db[config.get("dataDB", "eateries")]


result_db_connection = pymongo.MongoClient(config.get("resultsDB", "ip"), config.getint("resultsDB", "port"))
result_db  = result_db_connection[config.get("resultsDB", "database")]
reviews_results_collection = result_db[config.get("resultsDB", "review_result")]
eateries_results_collection = result_db[config.get("resultsDB", "eatery_result")]
discarded_nps_collection=  result_db[config.get("resultsDB", "discarded_nps")]


corenlpserver = jsonrpclib.Server("http://{0}:{1}".format(config.get("corenlpserver", "ip"), config.getint("corenlpserver", "port")))






class SolveEncoding(object):
        def __init__(self):
                pass


        @staticmethod
        def preserve_ascii(obj):
                if not isinstance(obj, unicode):
                        obj = unicode(obj)
                obj = obj.encode("ascii", "xmlcharrefreplace")
                return obj

        @staticmethod
        def to_unicode_or_bust(obj, encoding='utf-8'):
                if isinstance(obj, basestring):
                        if not isinstance(obj, unicode):
                                obj = unicode(obj, encoding)
                return obj


class bcolors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        RESET='\033[0m'


