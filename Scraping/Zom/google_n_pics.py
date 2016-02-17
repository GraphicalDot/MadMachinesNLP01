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
import hashlib
import urllib2 as urllib
import shutil
from cStringIO import StringIO
from boto.s3.connection import S3Connection
from boto.exception import S3ResponseError, S3CreateError
import PIL
from PIL import Image
import requests
import base64
import time 

terminal= Terminal()
FILE = os.path.basename(__file__)

config = ConfigParser.RawConfigParser()
config.read("zomato_dom.cfg")

driver_exec_path = "/home/%s/Downloads/chromedriver"%(getpass.getuser())
print driver_exec_path
DRIVER_NAME = "CHROME"
connection = pymongo.MongoClient(config.get("zomato", "host"), config.getint("zomato", "port"))
ZomatoReviewsCollection = connection[config.get("zomato", "database")][config.get("zomato", "reviews")]
ZomatoEateriesCollection = connection[config.get("zomato", "database")][config.get("zomato", "eatery")]

PicturesCollection = connection[config.get("zomato", "picsdatabase")][config.get("zomato", "picscollection")]


class GoogleNPics(object):
        def __init__(self, eatery_id, __eatery_id, url):
                self.url = url
                self.eatery_id = eatery_id
                self.__eatery_id = __eatery_id
                s3_connection = S3Connection(config.get("aws", "key"), config.get("aws", "secret"))
                self.bucket = s3_connection.get_bucket(config.get("aws", "bucket"))
                self.basewidth = 400
                self.image_format = "jpeg"



        def run(self):
                ##check if the image links  from website has already been scraped
                
                if ZomatoEateriesCollection.find_one({"eatery_id": self.eatery_id}).get("pictures"):
                        print terminal.blue("Pictures for the eatery_id %s has already been found"%self.eatery_id)
                        self.pictures = ZomatoEateriesCollection.find_one({"eatery_id": self.eatery_id}).get("pictures")
                else:
                        self.get_image_urls()
                        ZomatoEateriesCollection.update({"eatery_id": self.eatery_id}, {"$set": {"pictures": self.pictures}}, upsert=False, multi=False)
                
                print terminal.blue("Total number of pics found %s"%len(self.pictures))
                zomato_cdn_pics = [image for image in self.pictures if image.startswith("https://b.zmtcdn.com")]
                print terminal.blue("Total number of pics  found  on zomato cdn %s"%len([image for image in self.pictures if image.startswith("https://b.zmtcdn.com")]))

                if PicturesCollection.find({"eatery_id": self.eatery_id}).count() > 25:
                        print terminal.red("Images for eatery_id %s has already been stored on s3"%self.eatery_id)
                        return 



                for image_link in zomato_cdn_pics[-30:]:
                            try:
                                    key, s3_url, image_contents, height, width = self.each_image(image_link)
                                    ##convert the image contents into base64 encoding
                                    image_contents = base64.b64encode(image_contents)
                                    print PicturesCollection.insert({"s3_url": s3_url, "url": image_link, "contents": image_contents, 
                                        "height": height, "width": width, "image_id": key, "source": "zomato", "time": time.time()})

                            
                            except Exception as e:
                                    print terminal.red(str(e))
                                    pass
                return 

        def each_image(self, image_link):
                print "Image link is %s\n\n"%image_link
                proxy_dict = {"http": config.get("proxy", "proxy_addr"), 
                            "https": config.get("proxy", "proxy_addr")}
                try:
                        if config.getboolean("proxy", "use_proxy"):

                                proxy = urllib.ProxyHandler(proxy_dict)
                                opener = urllib.build_opener(proxy)
                                urllib.install_opener(opener)
                                try:
                                        response = urllib.urlopen("http://www.icanhazip.com")
                                        source = response.read()
                                        print terminal.red("From proxy %s"%source)
                                except Exception as e:
                                        print terminal.red("Could scrape icanhazip")
                                        pass
                        response = urllib.urlopen(image_link)
                        source = response.read()
                        img = Image.open(StringIO(source))
                
                except Exception as e:
                        print terminal.red(str(e))
                        return None

                print terminal.yellow("This is the image object %s for eatery_id <<%s>>"%(img, self.eatery_id))
                return self.generate_link(img, image_link)




        def generate_link(self, eatery_image, image_link):
                wpercent = (self.basewidth/float(eatery_image.size[0]))
                hsize = int((float(eatery_image.size[1])*float(wpercent)))
                
                ##resizing an pil image according to the basewidth wihch happend to be 400
                resized_img = eatery_image.resize((self.basewidth, hsize), PIL.Image.ANTIALIAS)

                output = StringIO()
                
                ##saving the resized image to output string io string
                resized_img.save(output, self.image_format, optimize=True, quality=85)
                
                ##contents of the image 
                ###saving original image to a stringIO
                original_image = StringIO()
                eatery_image.save(original_image, self.image_format, optimize=True, quality=85)
                eatery_image_contents = original_image.getvalue()


                ##generateing a unique key for the image
                __key = "%s_zcdn_%s"%(self.eatery_id, hashlib.sha224(eatery_image_contents).hexdigest())

                s3_key = self.bucket.new_key(__key)
                s3_key.set_metadata('Content-Type', 'image/jpg')
                s3_key.set_contents_from_string(output.getvalue())
                s3_key.set_canned_acl('public-read')
                s3_image_url = s3_key.generate_url(0, query_auth=False, force_http=True)
               
                print terminal.yellow("This is the url for the image %s for eatery_id <<%s>>"%(s3_image_url, self.eatery_id))
                return (__key, s3_image_url, eatery_image_contents, eatery_image.height, eatery_image.width)


        def get_image_urls(self):
                """
                if config.getboolean("proxy", "use_proxy"):
                        chrome_options = webdriver.ChromeOptions()
                        chrome_options.add_argument('--proxy-server=%s' % config.get("proxy", "proxy_addr"))
                        driver = webdriver.Chrome(driver_exec_path, chrome_options=chrome_options)
                        driver.get(self.url)

                else:
                        driver = webdriver.Chrome(driver_exec_path)
                        driver.get(self.url)

                """
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
                self.pictures = list()
                for e in self.soup.find("div", {"class": "photos_container_load_more"}).findAll("a"):
                        self.pictures.append(e.find("img")["data-original"].replace("_200_thumb", ""))

                return 









if __name__ == "__main__":
        ##eateries.find({ "eatery_area_or_city": "Delhi NCR", "eatery_photo_link" : { "$exists" : True, "$ne" :None }})
        """
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

        """
        instance = GoogleNPics("300716", "bbf65a1cae67598b9fcd0ed45e7e272fd405456985a51642e16bce59661f626e", "https://www.zomato.com/ncr/cocktails-dreams-speakeasy-sector-15-gurgaon/photos#tabtop")
        instance.run()








