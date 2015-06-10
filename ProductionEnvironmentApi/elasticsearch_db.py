#!/usr/bin/env python
"""
Author: kaali
Dated: 9 June, 2015
Purpose: This is the script that will be used to populate elastic search on remote node
The purpose of the elastic search to solve the problem of query resolution
"""



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



        def flush(self, index_name):

