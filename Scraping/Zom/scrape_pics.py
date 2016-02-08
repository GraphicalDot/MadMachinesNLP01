#!/usr/bin/env python
#-*- coding: utf-8 -*-
import time
import os
from selenium import webdriver
from BeautifulSoup import BeautifulSoup
import ConfigParser
import getpass
from blessings import Terminal
import pymongo
terminal= Terminal()
FILE = os.path.basename(__file__)

config = ConfigParser.RawConfigParser()
config.read("zomato_dom.cfg")

driver_exec_path = "/home/%s/Downloads/chromedriver"%(getpass.getuser())
print driver_exec_path
DRIVER_NAME = "CHROME"
#PROXY_ADDRESS ="localhost:8118"
PROXY_ADDRESS = "52.74.21.248:8118"
connection = pymongo.MongoClient(config.get("zomato", "host"), config.getint("zomato", "port"))
ZomatoReviewsCollection = connection[config.get("zomato", "database")][config.get("zomato", "reviews")]
ZomatoEateriesCollection = connection[config.get("zomato", "database")][config.get("zomato", "eatery")]

class ScrapePics(object):
        def __init__(self, eatery_id, url):
                self.url = url
                self.eatery_id = eatery_id


        def run(self):
                if config.getboolean("proxy", "use_proxy"):
                        chrome_options = webdriver.ChromeOptions()
                        chrome_options.add_argument('--proxy-server=%s' % PROXY_ADDRESS)
                        driver = webdriver.Chrome(driver_exec_path, chrome_options=chrome_options)
                        driver.get(self.url)

                else:
                        driver = webdriver.Chrome(driver_exec_path)
                        driver.get(self.url)


                time.sleep(20)
                while True:
                        try:
                                driver.find_element_by_class_name("picLoadMore").click()
                                time.sleep(2)
                        except Exception as e:
                                break
                                pass
                                
                self.html =  driver.page_source
                self.__prepare_soup()
                self.__get_photo_url()
                driver.close()

        def __prepare_soup(self):
                self.soup = BeautifulSoup(self.html)


        def __get_photo_url(self):
                self.photo_urls = list()
                for e in self.soup.find("div", {"class": "photos_container_load_more"}).findAll("a"):
                        self.photo_urls.append(e.find("img")["data-original"].replace("_200_thumb", ""))

                return 





if __name__ == "__main__":
        ##eateries.find({ "eatery_area_or_city": "Delhi NCR", "eatery_photo_link" : { "$exists" : True, "$ne" :None }})
        for eatery in ZomatoEateriesCollection.find({ "eatery_area_or_city": "Delhi NCR", "Pictures" : { "$exists" : False}}):
                eatery_id = eatery.get("eatery_id")
                if eatery.get("eatery_photo_link"):
                        try:
                                instance = ScrapePics(eatery_id, eatery.get("eatery_photo_link"))
                                instance.run()
                                ZomatoEateriesCollection.update({"eatery_id": eatery_id}, {"$set": {"Pictures": instance.photo_urls}}, upsert=False, multi=False)
                                print terminal.blue("eatery_id <<%s>> updated with <<%s>> pictures\n\n"%(eatery_id, len(instance.photo_urls)))
                        except Exception as e:
                                print terminal.red("Error in eatery_id <<%s>> on eatery_url <<%s>>\n\n"%(eatery["eatery_id"], eatery["eatery_url"]))
                                pass












