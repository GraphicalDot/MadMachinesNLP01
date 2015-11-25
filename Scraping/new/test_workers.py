#!/usr/bin/env ipython

import random
import subprocess
from ZomatoScrapeTasks import GenerateEateriesList, StartScrapeChain, ScrapeEachEatery


#GenerateEateriesList.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 0, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 0, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 1, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 2, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 3, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 4, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 5, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 6, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 7, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 8, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 9, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 10, False])
#ScrapeEachEatery.apply_async([{"eatery_url": "https://www.zomato.com/ncr/dilli-19-kalkaji-new-delhi"}])
