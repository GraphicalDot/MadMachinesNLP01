#!/usr/bin/env python

import pymongo
import sys
import codecs
import csv
connection = pymongo.Connection()
db = connection.modified_canworks
eatery = db.eatery
reviews = db.review


def to_unicode_or_bust(obj, encoding='utf-8'):
	if isinstance(obj, basestring):
		if not isinstance(obj, unicode): 
			obj = unicode(obj, encoding)
	return obj                      



"""
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


def new_file_for_tag_manipulation(file_name):

	tag_list = ["food", "service", "null", "overall", "ambience", "cost", "positive"]
	__food = __service = __overall = __ambience = __cost = __null = list()

	for element in tag_list:
		total_length = reviews.count()
		print "Writing {0} sentences".format(element)
		index = 0

		for post in reviews.find():
			if bool(post.get(element)):
		eval("__{0}".format(element)).extend([[to_unicode_or_bust(sentence), element, post.get("review_id")] for sentence in post.get(element)])
			index += 1

	csvfile = codecs.open(file_name, 'wb')
	writer = csv.writer(csvfile, delimiter=" ")

	for tag in tag_list:
		writer.writerow(" ")
		for __entry in eval("__{0}".format(tag)):
			try:
				writer.writerow(to_unicode_or_bust(__entry))
			except:
				print __entry

	csvfile.close()
"""


def make_new_files_from_csvfile(csv_path, target_path):
	csvfile = codecs.open(csv_path, 'rb')
	reader = csv.reader(csvfile, delimiter=',')
	data, sorted_data = list(), list()
	for row in reader:
		data.append(row)

	for row in data:
		sorted_data.append([row[1], row[5]])

	tag_list = ["food", "service", "null", "overall", "ambience", "cost"]
	
	first_name = "manually_classified"

	for element in sorted_data:
		if element[1] in tag_list:
			with open("{0}/manually_classified_{1}.txt".format(target_path, element[1]), "a") as myfile:
				    myfile.write(element[0])
				    myfile.write("\n")





if __name__ == "__main__":
	csv_path = "/home/k/Downloads/canworks_file/total_reviews_classification_CT_01112014-NK_2.csv"
	target_path= "/home/k/Desktop/trainers"
	make_new_files_from_csvfile(csv_path, target_path)
