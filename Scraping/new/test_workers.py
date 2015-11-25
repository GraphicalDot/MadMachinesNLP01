#!/usr/bin/env ipython

import random
import subprocess
from ZomatoScrapeTasks import GenerateEateriesList, StartScrapeChain


#GenerateEateriesList.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 0, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 0, False])

