#!/usr/bin/env python
import requests
import BeautifulSoup
import warnings
import sys
import os
import hashlib
import time
from selenium import webdriver
file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(file_path)
from colored_print import bcolors

                                                                                                                                                       
def encoding_help(obj):
        if not isinstance(obj, unicode):
                obj = unicode(obj)
        obj = obj.encode("ascii", "xmlcharrefreplace")
        return obj 






class PerCity:
        def __init__(self, url, start, end, do_print):
                self.url = url 

                r = requests.get(self.url)
                self.url_soup = BeautifulSoup.BeautifulSoup(r.text)
                self.start = start
                self.end = end
                self.__print = (True, False)[do_print == False]
                print self.__print

        def __number_of_pages(self):
                number_of_pages = self.url_soup.find("div", {"class": "page-of-pages arrange_unit arrange_unit--fill"}).text.replace('Page 1 of ', "")
                if self.__print:
                        print number_of_pages
                return number_of_pages

    
        def __make_links(self):
                pages = self.__number_of_pages()
                links = ["{0}&start={1}0".format(self.url, number) for number in  range(1, int(pages) + 1)]
                if self.__print:
                        print links
                return links


        def __filter_links(self):
                links_to_be_scraped = self.__make_links()[int(self.start): int(self.end)]
                if self.__print:
                        print links_to_be_scraped
                return links_to_be_scraped



        def scrape_links(self):
                restaurants = list()
                links_to_be_scraped = self.__filter_links()
                for link in links_to_be_scraped:
                        restaurants.append(self.__per_page_data(link))

                if self.__print:
                        print restaurants

                return restaurants

        def __per_page_data(self, page_url):
                """
                Extracts resturant information from one page which approximately yelp 
                has 10 restaurants per page
                """
                __per_page_restaurants = list()

                __html = requests.get(page_url)
                
                __soup = BeautifulSoup.BeautifulSoup(__html.text)

                for __res in __soup.findAll("div", {"class": "biz-listing-large"}):
                        __per_page_restaurants.append(self.__each_restaurant_data(__res))


                return __per_page_restaurants[1: ]

        def catch_exception(func):
                def deco(self, review):
                        try:
                                return func(self, review)
                        except Exception as e:
                                warnings.warn("{color} ERROR <{error}> in function <{function}> {Reset}".format(\
                                        color=bcolors.FAIL, error=e, function=func.__name__ , Reset=bcolors.RESET))
                                  
                                return ""
                return deco       


        def __each_restaurant_data(self, restaurant_soup):
                res_data = dict()
                res_data["site"] = "yelp"
                res_data["eatery_name"] = self.__res_name(restaurant_soup)
                res_data["eatery_rating"] = self.__res_rating(restaurant_soup)
                res_data["eatery_categories"] = self.__res_rating(restaurant_soup)
                res_data["eatery_phone_number"]= self.__res_phone_number(restaurant_soup)
                res_data["eatery_city"] = self.__res_city(restaurant_soup)
                res_data["eatery_address"] = self.__res_address(restaurant_soup)
                res_data["eatery_link"] = self.__res_link(restaurant_soup)
                __str = encoding_help(res_data["eatery_name"]) + res_data["eatery_city"] + res_data["eatery_address"]
                print __str
                res_data["eatery_id"] = hashlib.md5(__str).hexdigest()
                return res_data

               
        @catch_exception
        def __res_name(self, __soup):
                return __soup.find("a", {"class": "biz-name"}).text
                
        @catch_exception
        def __res_rating(self, __soup):
                return __soup.find("div", {"class": "rating-large"}).find("i")["title"].replace(" star rating", "")

        @catch_exception
        def __res_categories(self, __soup):
                return [__a.text for __a in __soup.find("span", {"class": "category-str-list"}).findAll("a")]
                
        @catch_exception
        def __res_phone_number(self, __soup):
                return __soup.find("span", {"class": "biz-phone"}).text

        @catch_exception
        def __res_city(self, __soup):
                return __soup.find("div", {"class": "secondary-attributes"}).\
                        find("span", {"class": "neighborhood-str-list"}).text
                
        @catch_exception
        def __res_address(self, __soup):
                return __soup.find("div", {"class": "secondary-attributes"}).find("address").text
    
        @catch_exception
        def __res_link(self, __soup):
                return "http://www.yelp.com{0}".format(__soup.find("a", {"class": "biz-name"}).get("href"))


class PerRestaurant:
        def __init__(self, res_dict):
                """
                Args:
                    res_dict:
                            {'eatery_address': u'133 Wythe AveBrooklyn, NY 11211', 
                            'eatery_rating': u'4.5', 
                            'eatery_link': 'http://www.yelp.com/biz/cafe-mogador-brooklyn', 
                            'eatery_categories': u'4.5', 
                            'eatery_site': 'yelp', 
                            'eatery_phone_number': u'(718) 486-9222', 
                            'eatery_name': u'Cafe Mogador', 
                            'eatery_city': u'Williamsburg - North Side'
                            }
                """
                self.res_dict = res_dict
                __html = requests.get(self.res_dict.get("eatery_link"))
                self.soup = BeautifulSoup.BeautifulSoup(__html.text)
                self.no_of_review_pages = self.soup.find("div",  {"class": "page-of-pages arrange_unit arrange_unit--fill"}).\
                        text.replace("Page 1 of ", "")

        


        def __make_links(self):
                pages = list()
                i = 40
                pages.append(self.res_dict.get("eatery_link"))
                for page in range(1, int(self.no_of_review_pages)):
                        pages.append("{0}?start={1}".format(self.res_dict["eatery_link"], i))
                        i+= 40
                return pages

        def __prepare_soup_from_url(self, link):
                __html = requests.get(link)
                return BeautifulSoup.BeautifulSoup(__html.text)


        def scrape_reviews(self):
                for page_link in self.__make_links():
                        __soup = self.__prepare_soup_from_url(page_link)
                        

        def __per_page_reviews(self, page_soup):
                review_list = list()
                reviews = page_soup.find("ul", {"class": "ylist ylist-bordered reviews"}).findAll("div", {"class": "review-wrapper"})
                for review_soup in reviews:
                        review_dict = __dict()
                        review_dict.update({"date_published": self.__date_published(review_soup)})
                        review_dict.update({"eatery_rating": self.__rating_value(review_soup)})
                        review_dict.update({"review_text": self.__review_text(review_soup)})
                        review_dict.update({"scraped_epoch": self.__scraped_epoch()})
                        review_dict.update(self.__votings(review_soup))
                        review_list.append(review_dict)

        def __date_published(self, review_soup):
                return review_soup.find("meta", {"itemprop": "datePublished"})["content"]

        def __rating_value(self, review_soup):
                return eatery_soup.find("meta", {"itemprop": "ratingValue"})["content"]

        def __review_text(self, review_soup):
                return  review_soup.review.find("p", {"itemprop": "description"}).text

        def __scraped_epoch(self):
                return int(time.time())

        def __votings(self, review_soup):
                voting_dict = dict()
                for button in review_soup.findAll("li", {"class": "vote-item inline-block"}):
                        voting_dict.update({
                            button.find("span", {"class": "vote-type"}).text: button.find("span",  {"class": "count"}).text})

                return voting_dict




if __name__ == "__main__":
        instance = PerCity("http://www.yelp.com/search?find_loc=New+York%2C+NY&cflt=food", 1, 2, True)
        eatries = instance.scrape_links()
        for eatery_dict in eatries[0:1]:
                __ins = PerRestaurant(eatery_dict)


