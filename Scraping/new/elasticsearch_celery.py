#!/usr/bin/env python

import json
import tornado.escape
import tornado.ioloop
import tornado.web
import tornado.autoreload
from tornado.httpclient import AsyncHTTPClient
from tornado.log import enable_pretty_logging
import tornado.httpserver
from itertools import ifilter
from tornado.web import asynchronous
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
import functools
import itertools



PORT_NUMBER = "5000"
from elasticsearch import Elasticsearch, helpers
from elasticsearch import RequestError
ES_CLIENT = Elasticsearch("localhost", timeout=30)


def cors(f):
        @functools.wraps(f) # to preserve name, docstring, etc.
        def wrapper(self, *args, **kwargs): # **kwargs for compability with functions that use them
                self.set_header("Access-Control-Allow-Origin",  "*")
                self.set_header("Access-Control-Allow-Headers", "content-type, accept")
                self.set_header("Access-Control-Max-Age", 60)
                return f(self, *args, **kwargs)
        return wrapper




class GetIndexes(tornado.web.RequestHandler):
        @cors
        @tornado.gen.coroutine
        @asynchronous
        def get(self):
                result = ES_CLIENT.indices.get_aliases().keys()
                self.write({"success": True,
                        "error": False,
                        "result": result, 
                        })

                self.finish()

class GetTypesIndex(tornado.web.RequestHandler):
        @cors
        @tornado.gen.coroutine
        @asynchronous
        def get(self):

                index_name = self.get_argument("index_name")
                result = ES_CLIENT.indices.get_mapping()[index_name]["mappings"].keys()
                self.write({"success": True,
                        "error": False,
                        "result": result, 
                        })
                self.finish()


def process_result(__result):
        result = [l["_source"] for l in __result["hits"]["hits"]]
        return result





class GetInfoOnStatus(tornado.web.RequestHandler):
        @cors
        @tornado.gen.coroutine
        @asynchronous
        def post(self):
                """
                If you want all the meseeges pass just index_name and doc_type
                if you want all meseeges for eatery_id pass eatery_id
                if you want messeges filtered on the basis of status, pass status

                """
                json_data = json.loads(self.request.body)
                self.request.arguments.update(json_data)
                
                index_name = self.request.arguments["index_name"]
                doc_type= self.request.arguments["doc_type"]
                eatery_id = self.request.arguments["eatery_id"]
                status = self.request.arguments["status"]
                skip = self.request.arguments["skip"]
                limit = self.request.arguments["limit"]
                """
                doc_type = self.get_argument("doc_type")
                eatery_id = self.get_argument("eatery_id")
                status = self.get_argument("status")
                skip = self.get_argument("skip")
                limit = self.get_argument("limit")
                """
                print index_name, doc_type, eatery_id, status, skip, limit
                if not eatery_id and not status:
                        __query= {
                                "query":{
                                        "match_all": {}     
                                    },

                                "from": skip,
                                "size": limit,
                                "sort":[
                                    {"generated": {
                                    "order" : "desc"}}
                                    ],}
                        

                if eatery_id and not status:
                        __query= {
                                "query":{
                                        "match":{
                                            "eatery_id":  eatery_id}
                                        },

                                "from": skip,
                                "size": limit,
                                "sort":[
                                    {"generated": {
                                    "order" : "desc"}}
                                    ],
                            }

                
                if status and not eatery_id:
                        __query= {
                                "query":{
                                        "match":{
                                            "status":  status}
                                        },

                                "from": skip,
                                "size": limit,
                                "sort":[
                                    {"generated": {
                                    "order" : "desc"}}
                                    ],
                            }



                if eatery_id and status:
                        __query  = {
                                "query": {
                                    "filtered": {
                                        "filter": {
                                            "bool": {
                                                "must": [
                                                    {"term": {"status": status}},
                                                    {"term": {"eatery_id": eatery_id}}
                                                    ]}}}},

                                "from": 0,
                                "size": 25,
                                "sort":[
                                        {"generated": {
                                        "order" : "desc"}}
                                        ],}

                print __query
                result = ES_CLIENT.search(index=index_name, doc_type=doc_type, body=__query)
                self.write({"success": True,
                        "error": False,
                        "result": process_result(result), 
                        })
                self.finish()




def main():
        http_server = tornado.httpserver.HTTPServer(Application())
        tornado.autoreload.start()
        http_server.listen(PORT_NUMBER)
        enable_pretty_logging()
        tornado.ioloop.IOLoop.current().start()


class Application(tornado.web.Application):
        def __init__(self):
                handlers = [
                    (r"/get_types_index", GetTypesIndex),
                    (r"/get_indexes", GetIndexes),
                    (r"/get_info_on_status", GetInfoOnStatus),
                    ]
                settings = dict(cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",)
                tornado.web.Application.__init__(self, handlers, **settings)
                self.executor = ThreadPoolExecutor(max_workers=60)



if __name__ == '__main__':
        print "server reloaded om %s "%(PORT_NUMBER)
        main()







