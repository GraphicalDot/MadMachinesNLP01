#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import os
import csv
import codecs
import time
import random
import goose
import BeautifulSoup
import re
from database import DB, collection, CONNECTION
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from reviews_scrape import Reviews
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from db_insertion import DBInsert	
from colored_print import bcolors




class EateriesList(object):

	def __init__(self, url, number_of_restaurants, skip, is_eatery):
		if is_eatery:
			#This implies that the url that has been given to initiate this class is the restaurant url not a url on which 
			#lots of restaurant urls are present
			self.url = url
			print "yo yo hohoney singh"
			self.get_eateries_list = list()
			self.get_eateries_list.append({"eatery_url": self.url})
		
		else:	
			self.url = url
			self.number_of_restaurants = number_of_restaurants
			self.skip = skip
			self.soup = self.prepare_soup(self.url)
			self.get_eateries_list = self.eateries_list()
	


        def prepare_soup(self, url):
		"""
		This function, given the url fetches all the html through the help of goose library and prepares a soup with the help
		of beautifulsoup
		returns:
			soup of the webpage present on the url being provided

		"""
		goose_instance = goose.Goose()
		data = goose_instance.extract(url)
		data = data.raw_html
		soup = BeautifulSoup.BeautifulSoup(data)
		return soup
	
	
	def pagination_links(self):
		"""
		This forms the pagination, It first identifies how many pages are present on the url given to this class and then forms the
		pagination links, ready to be scraped
		return:
			pages_url: all the webpages which have the restaurants present in the area
			sample   ['http://url/ncr/malviya-nagar-delhi-restaurants?category=1&page=1', 
			'http://url/ncr/malviya-nagar-delhi-restaurants?category=1&page=2', ..... and so on]
		"""
		
		try:
                        pages_number = self.soup.find("div", {"class": "search-pagination-top bb box-sizing-content"}).text.split("&")[0].split(" ")[-1]
		except AttributeError:
			print "{0}Either the dom has been changed or just one page present in pagination".format(bcolors.FAIL)
			pages_number = 1
		
		__pages_url = ["%s?page=%s"%(self.url, page_number) for page_number in range(1, int(pages_number)+1)]
		print __pages_url
		return __pages_url


	def eateries_list(self):
		"""
		provided pages from the pagination_links function it fetches the url of eateries present on the page 

		returns:
			[{'cuisine': u'Asian, North Indian, Continental', 'adddress': 'T 540, Panchshila Park, Malviya Nagar, New Delhi', 
			'rating': u'3.9', 'title': 'Very Good', 'eatery_id': '998', 'cost': u'\nCostfor2:Rs.1600\n', 
			'eatery_url': 'http://url/ncr/suribachi-malviya-nagar-delhi', 'eatery_name': u'Suribachi'},

			{'cuisine': u'North Indian, Fast Food', 'adddress': 'C 51, Main Market Road, Upper Ground Floor, Malviya Nagar, Delhi', 
			'rating': u'3.4', 'title': 'Good', 'eatery_id': '305615', 'cost': u'\nCostfor2:Rs.400\n', 
			'eatery_url': 'http://url/ncr/urban-spoon-1-malviya-nagar-delhi', 'eatery_name': u'Urban Spoon'}]
		"""	
		eateries = list()
		self.start_page_number = self.skip/30 #Keeping in mind that zomato does have 30 restaurants per page
			
		self.end_page_number = self.number_of_restaurants/30 

		pages = self.pagination_links()
                print pages


                print self.start_page_number, self.end_page_number
                print  pages[self.start_page_number: self.start_page_number + self.end_page_number]


		for page in pages[self.start_page_number: self.start_page_number + self.end_page_number]:
			time.sleep(random.choice(range(0, 30)))
			eateries.extend(self.fetch_eateries(page))
		
		return eateries
	
	def fetch_eateries(self, page_url):
		"""
		This fetches all the li elements which belongs to individual eatries present on the page present on the urlgiven

		"""
		
		eateries_list = list()
		soup = self.prepare_soup(page_url)
		eatries_soup = soup.findAll("li", {"class": "resZS mb5 pb5 bb even  status1"})
                for eatery_soup in eatries_soup:
			eateries_list.append(self.each_eatery(eatery_soup))
		return eateries_list

	def each_eatery(self, eatery_soup):
		"""
		It fetches individual information for each eatery from the url given to it
		return:
			{'cuisine': u'Asian, North Indian, Continental', 'adddress': 'T 540, Panchshila Park, Malviya Nagar, New Delhi', 
			'rating': u'3.9', 'title': 'Very Good', 'eatery_id': '998', 'cost': u'\nCostfor2:Rs.1600\n', 
			'eatery_url': 'http://url/ncr/suribachi-malviya-nagar-delhi', 'eatery_name': u'Suribachi'}

		"""
		eatery = dict()
                
                #Subarea like gk, khan market
                try:
                    eatery["eatery_sub_area"] = "-".join(self.url.split("/")[-1].split("-")[0: -2])
                    
                except :
                    
                    eatery["eatery_sub_area"] = None


                eatery["eatery_id"] = eatery_soup.get("data-res_id")
		eatery["eatery_url"] = eatery_soup.find("a").get("href")
		eatery["eatery_name"] = eatery_soup.find("a").text
		try:
			eatery["eatery_address"] = eatery_soup.find("span", {"class": "search-result-address"})["title"]
		except Exception:
			eatery["eatery_address"] = None

		eatery["eatery_cuisine"] = eatery_soup.find("div", {"class": "res-snippet-small-cuisine truncate"}).text
		eatery["eatery_cost"] = eatery_soup.find("div", {"class": "ln24"}).text
		
		soup = eatery_soup.find("div", {"class": "right"})
		try:
			eatery["eatery_rating"] = {"rating": soup.findNext().text.replace(" ", "").replace("\n", ""),
						"votes": soup.find("div",  {"class": "rating-rank right"}).findNext().text }

		except Exception:
			eatery["eatery_rating"] = None

		try:
			eatery["eatery_title"] = eatery_soup.findNext().get("title")
		except Exception:
			eatery["eatery_title"] = None
		

		try:
			collection =  eatery_soup.find("div", {"class": "srp-collections"}).findAll("a")
			eatery["eatery_trending"] = [element.text for element in collection]

		except Exception:
			eatery["eatery_trending"] = None


		##Finding total number of reviews for each eatery soup
		try:
			eatery["eatery_popular_reviews"] = eatery_soup.find("a", {"data-result-type": "ResCard_Reviews"}).text
		except Exception:
			eatery["eatery_popular_reviews"] = None


		return eatery


class EateryData(object):
	"""
	This class fetches all the restaurants present on the url or the page, It also handles the pagination.
	For each restaurant present alongwith the pagination, It fetches all the required information for the restaurant and the reviews for it
	"""
	def __init__(self, eatery):
		self.eatery = eatery
		self.soup = self.with_selenium()
	        self.retry_eatery_id()
		self.retry_eatery_name()
		self.retry_eatery_address()
		self.retry_eatery_cost()
		self.retry_eatery_trending()
		self.retry_eatery_title()
		self.retry_eatery_rating()
		self.retry_eatery_cuisine()
		
		
		self.eatery_highlights()
		self.eatery_popular_reviews()
		self.eatery_opening_hours()
		self.eatery_metro_stations()
		self.eatery_photos()
		self.eatery_recommended_order()
		self.eatery_buffet_price()
		self.eatery_buffet_details()
		self.eatery_longitude_latitude()
		self.eatery_reviews()
		self.eatery_wishlists()
		self.area_or_city()

	def area_or_city(self):
		self.eatery["eatery_area_or_city"] = self.eatery.get("eatery_url").split("/")[3]

	def retry_eatery_id(self):
                """
                This class method retries for the eatery id
                """
                if not self.eatery.get("eatery_id"):
	                try:
                                self.eatery["eatery_id"] = self.soup.find("div", {"itemprop": "ratingValue"}).get("data-res-id")
	                except Exception:
		                self.eatery["eatery_id"] = None
	        return
	        

            
            
        def retry_eatery_name(self):
		"""
		This method tries to get the eatery url if the eatery dict supplied doesnt contain eatery name, Which happens
		if we want to scrape only one particular eatery
		"""
		if not self.eatery.get("eatery_name"):
			try:
				self.eatery["eatery_name"] = self.soup.find("h1", {"class": "res-name left"}).find("a").text
			except Exception:
				self.eatery["eatery_name"] = None
		return

	def retry_eatery_address(self):
		"""
		This method tries to get the eatery url if the eatery dict supplied doesnt contain eatery name, Which happens
		if we want to scrape only one particular eatery
		"""
		if not self.eatery.get("eatery_address"):
			try:
                            self.eatery["eatery_address"] = self.soup.find("h2", {"class": "res-main-address-text"}).text
			
			except Exception as e:
				self.eatery["eatery_address"] = None
		return

	def retry_eatery_cuisine(self):
		"""
		This method tries to get the eatery url if the eatery dict supplied doesnt contain eatery name, Which happens
		if we want to scrape only one particular eatery
		"""
		if not self.eatery.get("eatery_cuisine"):
			try:
				self.eatery["eatery_cuisine"] = self.soup.find("div", {"class": "pb2 res-info-cuisines clearfix"}).text
			except Exception:
				self.eatery["eatery_cuisine"] = None

		return

	def retry_eatery_cost(self):
		"""
		This method tries to get the eatery url if the eatery dict supplied doesnt contain eatery name, Which happens
		if we want to scrape only one particular eatery
		"""
		if not self.eatery.get("eatery_cost"):
			try:
				self.eatery["eatery_cost"] = self.soup.find("span", {"itemprop": "priceRange"}).text
			except Exception:
				self.eatery["eatery_cost"] = None

		return

	def retry_eatery_rating(self):
		"""
		This method tries to get the eatery url if the eatery dict supplied doesnt contain eatery name, Which happens
		if we want to scrape only one particular eatery
		"""
		if not self.eatery.get("eatery_rating"):
			try:
				self.eatery["eatery_rating"] = {"rating": self.soup.find("div", {"itemprop": "ratingValue"}).text.split("/")[0],
						"votes": self.soup.find("span", {"itemprop": "ratingCount"}).text}

			except Exception:
				self.eatery["eatery_rating"] = None
		return


	def retry_eatery_title(self):
		"""
		This method tries to get the eatery url if the eatery dict supplied doesnt contain eatery name, Which happens
		if we want to scrape only one particular eatery
		"""
		if not self.eatery.get("eatery_title"):
			self.eatery["eatery_title"] = None
		return

	def retry_eatery_trending(self):
		"""
		This method tries to get the eatery url if the eatery dict supplied doesnt contain eatery name, Which happens
		if we want to scrape only one particular eatery
		"""
		if not self.eatery.get("eatery_trending"):
			try:
				collection =  self.soup.find("div", {"class": "collections_res_container"}).findAll("a")
				self.eatery["eatery_trending"] = [element.text for element in collection]
			except Exception:
				self.eatery["eatery_trending"] = None
				
		return

	def with_selenium(self):
		#driver = webdriver.PhantomJS()
		driver = webdriver.Firefox()
		"""
		chromedriver = "{path}/chromedriver".format(path=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
		os.environ["webdriver.chrome.driver"] = chromedriver
		driver = webdriver.Chrome(chromedriver)
		"""
		
                driver.get(self.eatery.get("eatery_url"))


		try:
			driver.find_element_by_css_selector("a.everyone.empty").click()

		except NoSuchElementException:
			pass

                time.sleep(10)
		try:
			while True:
				time.sleep(random.choice([4, 3]))
				driver.find_element_by_class_name("load-more").click()
		except NoSuchElementException as e:
			print "{color} Catching Exception -<{error}>- with messege -<No More Loadmore tag present>-".format(color=bcolors.OKGREEN, error=e)
			pass
	
		except Exception as e:
                        print e
			raise StandardError("Coould not make the request")
		

		
		read_more_links = driver.find_elements_by_xpath("//div[@class='rev-text-expand']")
		for link in read_more_links:
			time.sleep(random.choice([2, 3]))
			link.click()

		html = driver.page_source
		driver.close()
		
		return BeautifulSoup.BeautifulSoup(html)

        def prepare_soup(self):
		"""
		Somehow this function became useless because of the studappa imposed by dynamic loading of webpages :)
		"""
		goose_instance = goose.Goose()
		data = goose_instance.extract(self.eatery.get("eatery_url"))
		data = data.raw_html
		soup = BeautifulSoup.BeautifulSoup(data)
		return soup

	def eatery_establishment_type(self):
		try:
                        variable = self.soup.find("div", {"class": "pb5 res-info-cuisines clearfix"}).text
			self.eatery["eatery_establishment_type"] = variable

		except Exception:	
			
			self.eatery["eatery_establishment_type"] = None
                return
	
        def eatery_known_for(self):
		try:
                        variable = self.soup.find("div", {"class": "res-info-known-for-text mr5"}).text
			self.eatery["eatery_known_for"] = variable

		except Exception:	
			
			self.eatery["eatery_known_for"] = None
                return
            

	def eatery_wishlists(self):
		try:
			variable = self.soup.find("div", {"class": "res-main-stats-num"})
			self.eatery["eatery_wishlist"] = variable.text

		except Exception:	
			
			self.eatery["eatery_wishlist"] = None


	def eatery_highlights(self):
		try:
			self.eatery["eatery_highlights"] = [dom.text.replace("\n", "") for dom in self.soup.findAll("div", {"class": "res-info-feature"})]
		except AttributeError:
			self.eatery["eatery_highlights"] = None
		return

	def eatery_popular_reviews(self):
		try:
			self.eatery["eatery_popular_reviews"] = self.soup.find("li", {"class": "text-tab-link"}).find("span").text
		except AttributeError:
			self.eatery["eatery_popular_reviews"] = None
		return

	def eatery_opening_hours(self):
		try:
			self.eatery["eatery_opening_hours"] = self.soup.find("span", {"class": "res-info-timings"}).text
		except AttributeError:
			self.eatery["eatery_opening_hours"] = None
		return

	def eatery_metro_stations(self):
		stations = self.soup.findAll("a", {"class": "res-metro-item clearfix left tooltip_formatted-e"})
		try:
			self.eatery["eatery_F_M_Station"] = {"distance": stations[0].find("div", {"class": "left res-metro-distance"}).text, "name": stations[0].find("div", {"class": "left res-metro-name"}).text}
		except Exception as e:
			self.eatery["eatery_F_M_Station"] = None

		try:
			self.eatery["eatery_S_M_Station"] = {"distance": stations[1].find("div", {"class": "left res-metro-distance"}).text, 
					"name": stations[1].find("div", {"class": "left res-metro-name"}).text}
		except Exception:
			self.eatery["eatery_S_M_Station"] = None
		return

	def eatery_photos(self):
		try:
			self.eatery["eatery_photos"] = (True, False)[self.soup.find("div", {"class": "res-photo-thumbnails"}).findAll("a") == None]
		except AttributeError:
			self.eatery["eatery_photos"] = False
		return

	def eatery_recommended_order(self):
		try:
			self.eatery["eatery_should_order"]= self.soup.find("div", {"class": "res-info-dishes-text"}).text
		except AttributeError:
			self.eatery["eatery_should_order"] = None
		return

	def eatery_buffet_price(self):
		try:
			self.eatery["eatery_buffet_price"] = self.soup.find("span", {"class": "res-buffet-price rbp3"}).text
		except AttributeError:
			self.eatery["eatery_buffet_price"] = None
		
		return

	def eatery_buffet_details(self):
		try:
			self.eatery["eatery_buffet_details"] = self.soup.find("span", {"class": "res-buffet-details"}).text

		except AttributeError:
			self.eatery["eatery_buffet_details"] = None
		return

	def eatery_longitude_latitude(self):
		try:
			coord = re.findall("\d+.\d+,\d+.\d+", self.soup.find("div", {"id": "res-map-canvas"}).find("img").get("data-original"))
			self.eatery["eatery_coordinates"] = coord[-1]

		except AttributeError, TypeError:
			self.eatery["eatery_coordinates"] = None
		return


	def eatery_reviews(self):
		area_or_city = self.eatery.get("eatery_url").split("/")[3]
		instance = Reviews(self.soup, area_or_city)
		self.eatery["reviews"] = instance.reviews_data
		return



def csv_writer(name):
	csvfile = codecs.open('%s.csv'%("-".join(name.split())), 'wb', encoding="utf-8")
	writer = csv.writer(csvfile, delimiter=" ")
	row_one = ['eatery_adddress', 	'eatery_cost', 		'eatery_cuisine', 	'eatery_id', 		'eatery_name', 
			'eatery_F_M_Station', 		'', 		'eatery_S_M_Station', 		'', 		'eatery_highlights', 
			'eatery_buffet_price', 		'eatery_buffet_details', 	'eatery_photos', 	'eatery_should_order', 
			'eatery_popular_reviews', 	'eatery_trending', 		'eatery_opening_hours', 	'eatery_coordinates', 
			'eatery_rating', 	'', 	"eatery_wishlists",	'eatery_title', 	'eatery_url', 		'converted_epoch',
			'eatery_id', 		'review_likes', 	'review_summary', 	'review_text', 		'review_time', 
			'review_url', 		'scraped_epoch', 	'user_followers', 	'user_id', 	'user_name', 
			'user_reviews', 	'user_url',]
	
	row_two = ['', '', '', '', '', 'distance', 'name', 'distance', 'name', '', '', '', '', '', '', '', '', '', 'rating', 'votes', '', '','', '', '','', '', '', '', '', '', '', '', '',]

	writer.writerow(row_one)
	writer.writerow(row_two)
	return (writer, csvfile)


def scrape_links(url, number_of_restaurants, skip, is_eatery):
	"""
	Args:
		url: 
			Url at which the resturants list is present, and is to be scraped 
			example 'http://www.zomato.com/ncr/malviya-nagar-delhi-restaurants?category=1"

		number_of_restaurants:
			The number of restaurants to be scraped, In detail, stop_at argument stop the code from scraping more restaurants 
			by going on the pagination links, And one page has around 30 restaurants, so even if you set stop_at at 1, it will still 
			have 30 restaurants or more, So to stop the code to scrape reviews of restaurants, number of restaurants is used.
			So for example if you set number of restaurants = 2, The code will scrape all the reviews and details of only two 
			restaurants

		skip: If you know how many restaurants has already been scraped then you can enter that number to skip that
			number of restaurants, and then their details and reviews will not be scraped


	Returns:
		a list of restaurants dictionaries with their details required and the review list:
		The keys included in one restaurant doictionary are as follows
		
	"""
	if not skip:
		skip = 0
	
	if not number_of_restaurants:
		number_of_restaurants = 0

	print "These are the number of restaurants {0} and skip is {1}".format(int(number_of_restaurants), int(skip))
	instance = EateriesList(url, int(number_of_restaurants), int(skip), is_eatery)


	eateries_list = instance.get_eateries_list
	
	print "\n {color} Printing Eateries list \n".format(color=bcolors.OKBLUE)
	for eatery in eateries_list:
		print "\n{color} Eatery--<{eatery}>\n".format(color=bcolors.OKBLUE, eatery=eatery)

	return eateries_list	
	
def eatery_specific(eatery_dict):	
	try:
		print "\n {color} Opening Eatery--<{eatery}> with url --<{url}>\n".format(color=bcolors.OKBLUE, eatery=eatery_dict.get("eatery_name"), url=eatery_dict.get("eatery_url"))
	except Exception:
		print "\n {color} Eatery url --<{url}>\n".format(color=bcolors.OKBLUE, url=eatery_dict.get("eatery_url"))


	##If the eatery is already present then there is no need to scrape it again
	##Here we check on the basis of url because it might be a possibility that we want to scrape eatery on the basis of url and in 
	#that case eatery id may not be present in the database
	eatery_collection = collection("eatery")

	instance = EateryData(eatery_dict)
	#eatery_modified_list.append(dict([(key, value) for key, value in instance.eatery.iteritems() if key.startswith("eatery")]))
	#reviews_list.extend(instance.eatery.get("reviews"))
		
	eatery_modified = dict([(key, value) for key, value in instance.eatery.iteritems() if key.startswith("eatery")])
		
	#Creating csvfile witht he name of extery name
	#writer = csv_writer(eatery_modified.get("eatery_name"))[0]
	#csvfile = csv_writer(eatery_modified.get("eatery_name"))[1]
		
	station = lambda x : (x.get("name"), x.get("distance")) if x else (None, None)

	eatery_row = [eatery_modified.get('eatery_adddress'), eatery_modified.get('eatery_cost'), eatery_modified.get('eatery_cuisine'), 
			eatery_modified.get('eatery_id'), eatery_modified.get('eatery_name'), 
			station(eatery_modified.get("eatery_F_M_Station"))[1], 
			station(eatery_modified.get("eatery_F_M_Station"))[0],
			station(eatery_modified.get("eatery_S_M_Station"))[1], 
			station(eatery_modified.get("eatery_S_M_Station"))[0],
			eatery_modified.get("eatery_highlights"), eatery_modified.get("eatery_buffet_price"),
			eatery_modified.get("eatery_buffet_details"), eatery_modified.get("eatery_photos"),
			eatery_modified.get("eatery_should_order"), eatery_modified.get("eatery_popular_reviews"), 
			eatery_modified.get("eatery_trending"), eatery_modified.get("eatery_opening_hours"), 
			eatery_modified.get("eatery_coordinates"), eatery_modified.get('eatery_rating').get('rating'), 
			eatery_modified.get("eatery_rating").get('votes'), eatery_modified.get('eatery_title'), 
			eatery_modified.get("eatery_wishlist"), eatery_modified.get('eatery_url'), 
			eatery_modified.get('converted_to_epoch'),eatery_modified.get('eatery_id')]

	#writer.writerow(eatery_row)
	DBInsert.db_insert_eateries(eatery_modified)
	"""
        if eatery_collection.find_one({"eatery_id": eatery_dict.get("eatery_id")}):
		print "\n {color} The Eatery with the url --<{url} has already been scraped>\n".format(color=bcolors.WARNING, url=eatery_dict.get("eatery_url"))
		return
	"""	
	reviews = instance.eatery.get("reviews")
	
        
        DBInsert.db_insert_reviews(reviews)


	users_list = list()
	for review in  reviews:
		text = review.get("review_text")
		name = review.get("user_name")
		
		try:	
			review["review_text"] = text.decode("ascii", "ignore")
		except Exception:
			review["review_text"] = ''

		try:	
			review["user_name"] = name.decode("ascii", "ignore")

		except Exception:
			review["user_name"] = ''

		review_append = ["" for i in range(0, 22)]
		review_append.extend([value for key, value in review.iteritems()])
		#print review_append
		#writer.writerow(review_append)
		
		users = dict([(key, value) for key, value in review.iteritems()])
		users_list.append(users)
		
	DBInsert.db_insert_users(users_list)

	#csvfile.close()

	return

"""        
if __name__ == "__main__":
        #If you want to scrape a particular restaurant do this
        url = "https://www.zomato.com/ncr/kylin-premier-vasant-kunj-delhi"
	number_of_restaurants = 0
	skip = 0
        is_eatery = True

	scrape_links(url, number_of_restaurants, skip, is_eatery)
        
	number_of_restaurants = 30
	skip = 60
        is_eatery = False

        url = "https://www.zomato.com/ncr/khan-market-delhi-restaurants"
        eateries_list = scrape_links(url, number_of_restaurants, skip, is_eatery) 
        
        print eateries_list
        for element in eateries_list:
                eatery_specific(element)
	instance = EateriesList(url, int(number_of_restaurants), int(skip))
	eateries_list = instance.eateries_list()
	print eateries_list	
        #   scrape("http://www.zomato.com/ncr/malviya-nagar-delhi-restaurants?category=1", 30, 18) 
	###This is the right one for element in scrape_links("https://www.zomato.com/ncr/south-delhi-restaurants", 30, 30):
		print element.get("eatery_name")
		
		#	scrape("http://www.zomato.com/ncr/khan-market-delhi-restaurants?category=1", 28, 1)
        #runn.apply_async(["https://www.zomato.com/ncr/south-delhi-restaurants", 30, 520]), this has been done for south delhi

        #Sun Sep  7 13:31:10 IST 2014


"""

