#/usr/bin/anv python
#-*- coding: utf-8 -*-

import BeautifulSoup
import goose
from selenium import web_driver
def images(soup):
	"""
	Args:
		Soup: This is the html soup of the eatery on which the url for the eaterie sis present.

	Returns:
		List of the images url

	paination not been implemented yet
	"""
	if not isinstance(soup, BeautifulSoup.BeautifulSoup):
		raise StandardError("The soup provided is not an instance of BeautifulSoup")
	try:
		url = soup.find("div", {"class": "right res-info-menu-div"}).find("a")["href"]
		instance = goose.Goose()
		return instance.raw_html
		
	except Exception:
		url = None
	return url



