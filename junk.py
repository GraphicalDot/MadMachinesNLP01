#!/usr/bin/env python

import pymongo

connection = pymongo.Connection()
db = connection.modified_canworks
eatery = db.eatery
reviews = db.review


def return_eateries_list():
	__a = list()
	for post in eatery.find():
		__a.append([post.get("eatery_id"), post.get("eatery_name"), post.get("area_or_city"), reviews.find({"eatery_id": post.get("eatery_id")}).count()])
	return sorted(__a, reverse=True, key=lambda x: x[3])



def reviews_list_every_eatery(__input_list, number_of_restaurants):
	__a = list()
	for eatery_object in __input_list[0: number_of_restaurants]:
		__reviews = list(reviews.find({"eatery_id": eatery_object[0]}))
		eatery_object.append(__reviews)
		__a.append(eatery_object)
	return __a


def editing_review_time(__input_list):
	__a = list()
	for eatery_object in __input_list:
		eatery_review_times = [post.get("review_time") for post in eatery_object[4]]
		__a.append([eatery_object[0], eatery_object[1], eatery_object[2], eatery_object[3], eatery_review_times])
	return __a


def manipulate_review_time(__input_list):
	__abc = list()
	for eatery_object in __input_list:
		new_list = sorted(eatery_object[4], reverse=True)
		__p = list()
		__p.append(list())
		__p[0].append(new_list[0])
		for element in new_list:
			if __p[-1][-1].split(" ")[0].split("-")[1] != element.split(" ")[0].split("-")[1]:
				__p.append(list())__p[-1].append(element)
			else:
				__p[-1].append(element)
		__abc.append([eatery_object[0], eatery_object[1], eatery_object[2], eatery_object[3], __p])
	return __abc


def final_output(__input_list):
	__abcd = list()
	for eatery_object in __input_list:
		__a = list()
		for element in eatery_object[4]:
			__str = element[0].split(" ")[0]
			__a.append([__str,  "{0}/{1}".format(__str.split("-")[1], __str.split("-")[0][2:]),  len(element)])
		__abcd.append([eatery_object[0], eatery_object[1], eatery_object[2], eatery_object[3], __a])
	return __abcd		





