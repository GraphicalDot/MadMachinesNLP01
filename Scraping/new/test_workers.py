#!/usr/bin/env ipython

import random
import subprocess
from ZomatoScrapeTasks import GenerateEateriesList, StartScrapeChain, ScrapeEachEatery
from ip_renew import generate_new_proxy
#GenerateEateriesList.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 0, False])

generate_new_proxy()
"""
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 0, False])
"""
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 1, False])
"""
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 2, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 3, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 4, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 5, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 6, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 7, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 8, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 9, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 10, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 11, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 12, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 13, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 14, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 15, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 16, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 17, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 18, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 19, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 20, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 21, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 22, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 23, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 24, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 25, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 26, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 27, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 28, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 29, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 30, False])
for e in range(32, 100):
        StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, e, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 101, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 102, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 103, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 104, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 105, False])
for e in range(109, 180):
        StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, e, False])

StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 501, False])

StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 502, False])
"""


#ScrapeEachEatery.apply_async([{"eatery_url": "https://www.zomato.com/ncr/dilli-19-kalkaji-new-delhi"}])
