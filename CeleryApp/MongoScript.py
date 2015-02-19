#-*- coding: utf-8 -*-
"""
Author: Kaali
Dated: 19 February, 2015
Purpose: This file deals with mongodb connections and also have functions
used by celery worket to input and output data

Whole point is there are two Mongodb databases hosted on different servers, One deals with all 
the data that has been scraped from websites and aggragated from xml, json api's of the websites.

The other databases deals with the results that has been accumulated by celery workers, The point
in making two different databses is, that a single database may not be able to handle hammering
both ways, getting reviews from scraping and then storing the results after running algorithms
on the reviews
"""
import os
import sys
file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(file_path)
from GlobalConfigs import MONGO_NLP_RESULTS_IP, MONGO_NLP_RESULTS_PORT  














