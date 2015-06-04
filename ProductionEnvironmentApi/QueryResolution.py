#!/usr/bin/env python
"""
Author: kaali
Dated : 29May, 2015
Purpose: To find the noun phrases matching the query entered by User
How it works:
    


pipe = [
    {"$project": {"birthday":1, "id":1}
        },
            {"$match": { "birthday":{"$gte":datetime.datetime(1987, 1, 1, 0, 0)} }
                         }
                ]
                res =db.patients.aggregate(pipe,allowDiskUse=True)


have the results returned as a cursor, by specifying useCursor=True when you call aggregate.
"""


class QueryResolution(object):
        
        def __init__(self, food_text, ambience_text, cost_text, service_text):
                self.food_text = food_text
                self.cost_text = cost_text
                self.service_text = service_text
                self.ambience_text = ambience_text

        def __cost_classification(self):
                """
                Does the cost classification for the self.cost_text
                """
                if cost_predicted_sub_tag == "cost-null":
                        cost_predicted_sub_tag = None
                return cost_predicted_sub_tag
        
        
        def __service_classification(self):
                """
                Does the cost classification for the self.cost_text
                """
                if cost_predicted_sub_tag == "cost-null":
                        cost_predicted_sub_tag = None
                return cost_predicted_sub_tag
        
        def __ambience_classification(self):
                """
                Does the cost classification for the self.cost_text
                """
                if cost_predicted_sub_tag == "cost-null":
                        cost_predicted_sub_tag = None
                return cost_predicted_sub_tag

        def detect_dish(self):
                """
                Detect the dish whicht he user is trying to find out
                """


                    return dish_name


        


