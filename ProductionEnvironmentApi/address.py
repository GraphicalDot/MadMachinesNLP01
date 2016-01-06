#!/usr/bin/env python

import os
import sys
import geocoder

"""
file_path = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(file_path)                                                                                                                                                                                                                                                     sys.path.append(parent_dir)                                                                                                                                                                                                                                                                 
os.chdir(parent_dir)
from connections import reviews, eateries, reviews_results_collection, eateries_results_collection, discarded_nps_collection, bcolors, short_eatery_result_collection                                                                                 
os.chdir(file_path)     




for address in list(set(result)): 
            g = geocoder.google(address)
                    try:
                                    print address, g.geojson, area_list.append((address, g.geojson.get("geometry").get("coordinates"))), "\n\n"
                                            except Exception as e:        
                                                            print "failed"


"""







result = list()
for (eatery_id, location, address, geo_address) in c:
        """
        Because sometime the address after splitting only has one element in the list 
        like  ['sector 56']
        """
        if geo_address.get("city"):
                city = geo_address.get("city")

        else:
                city = ("", geo_address.get("suburb"))[geo_address.get("suburb") != None] + ", " + ("", geo_address.get("county"))[geo_address.get("county") != None]
		print "city==%s"%(city)
		print "geo_address==%s"%geo_address
		print "address==%s"%address
		print "suburb==%s"%geo_address.get("suburb")
		print "\n"        

        try:
                area =  address.split(",")[-2]
        except Exception as e:
                area = address
        

	__result = area.lstrip() + "," +  city.lstrip()

        
	result.append(__result)



print set(result)





def edit_location(latitude, longitude, , address):
	"""
	This function was made bacuse of the incomptency of various websites to 
	even acutally write proper address, 

	they didnt even tries to reverse the geocode, Bloody jokers!!

	{'status': 'OK', 
		'city': u'New Delhi', 
		'confidence': 9, 'ok': True, 'encoding': 'utf-8', 'country': u'IN', 'provider': 'google', 
		'location': 'upreme Plaza, Main Market, Sector 6, Dwarka, New Delhi', 
		'county': u'South West Delhi', 'state': u'DL', 'street': u'Mall Rd', 
		'bbox': {'northeast': [28.5928047302915, 77.06019673029151], 'southwest': [28.5901067697085, 77.0574987697085]}, 
		'status_code': 200, 
		'address': u'Odeon Plaza, Mall Rd, Sec-6 Market, Sector 6 Dwarka, Dwarka, New Delhi, Delhi 110075, India', 'lat': 28.5914558, 'lng': 77.0588478, 
		'postal': u'110075', 'quality': u'premise', 'sublocality': u'Dwarka', 'accuracy': u'ROOFTOP'}

	"""

        if int(latitude) == 0:
                g  = geocoder.google(address)
                location = g.ltalng

	else:
		g = geocoder.google([latitude, longitude], method='reverse')
		g = geocoder.google(address)
	
	
	county = g.geojson["properties"].get("county")
	city = g.geojson["properties"].get("city")
	sublocality = g.geojson["properties"].get("sublocality")
	pincode = g.geojson["properties"].get("postal")
	street = g.geojson["properties"].get("street")
        
	return location, address, (street, sublocality, county, city, postal)




