#!/usr/bin/env python

import pymongo


class GetReviews:
	connection = pymongo.Connection()
	"""
	Restaurants keys:
		u'eatery_F_M_Station', u'eatery_title', u'eatery_coordinates', u'eatery_opening_hours', u'eatery_adddress', 
		u'eatery_rating', u'eatery_id', u'eatery_S_M_Station', u'eatery_highlights', u'eatery_buffet_price', 
		u'eatery_photos', u'eatery_url', u'eatery_buffet_details', u'eatery_cuisine', u'eatery_should_order', 
		u'eatery_popular_reviews', u'_id', u'eatery_name', u'eatery_trending', u'eatery_cost' 


	Reviews Keys:
		u'review_summary', u'user_id', u'review_id', u'user_followers', u'review_time', u'review_url', u'user_url', 
		u'review_text', u'eatery_id', u'scraped_epoch', u'user_reviews', u'_id', u'user_name', u'review_likes', 
		u'converted_epoch'


	Users Keys:
		u'user_id', u'user_followers', u'user_url', u'user_reviews', u'updated_on', u'_id', u'user_name'

	"""


	def __init__(self, restaurant_name, res_skip= 0, res_limit=10, review_skip=0, review_limit=10):
		"""
		By default only 10 resturants are returned
		By default only 10 reviews are returned

		"""
		self.restaurants = self.connection.modified_canworks.eatery
		self.reviews = self.connection.modified_canworks.review
		self.users = self.connection.modified_canworks.user
		self.restaurant_name = restaurant_name
		self.res_skip = res_skip
		self.res_limit = res_limit
		self.review_skip = review_skip
		self.review_limit = review_limit


	def restaurants_list(self):
		"""
		This returns the restaurants on the basis of the restaurant name provided

		"""
		if not bool(self.res_skip):
			return list(restaurants.find().skip(0).limit(self.res_limit))
		
		return list(restaurants.find().skip(self.res_skip).limit(self.res_limit))
		
	def reviews(self):
		"""
		This returns the reviews on the basis of the restaurant name provided
		"""

		restaurant_id = self.restaurants.find_one({"eatery_name": self.restaurant_name})
		
		if not bool(self.review_skip):
			return list(reviews.find({"eatery_id": restaurant_id}).skip(0).limit(self.review_limit))
		
		return list(reviews.find({"eatery_id": restaurant_id}).skip(self.review_skip).limit(self.review_limit))





