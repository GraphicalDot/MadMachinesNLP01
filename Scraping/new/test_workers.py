#!/usr/bin/env ipython

import random
import subprocess
from ZomatoScrapeTasks import GenerateEateriesList, StartScrapeChain, ScrapeEachEatery


#GenerateEateriesList.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 0, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 34, False])
#ScrapeEachEatery.apply_async([{"eatery_url": "https://www.zomato.com/ncr/dilli-19-kalkaji-new-delhi"}])

