#!/usr/bin/env python
#-*- coding: utf-8 -*-


import sys
import os
import urllib2
import socket
from redis_storage import RedisProxy

class ProxyHealthCheck:
	"""
	This class checks whether the proxies stored in redis database are working fine or not
	This is done by fetching the proxies with the status healthy from the redis 
	The proxies which arent healthy will then have their status changed as unhealthy
	"""
	def __init__(self):
		instance = RedisProxy()	
		self.healthy_proxies = instance.healthy_proxies()
		self.unhealthy_proxies = instance.unhealthy_proxies()
		print self.healthy_proxies

	def is_bad_proxy(self, proxy_dict):
		ip = "{ip}:{port_number}".format(ip=proxy_dict.get("ip"), port_number=proxy_dict.get("port"))
		print ip
		try:
			proxy_handler = urllib2.ProxyHandler({'http': ip})
			opener = urllib2.build_opener(proxy_handler)
			opener.addheaders = [('User-agent', 'Mozilla/5.0')]
			urllib2.install_opener(opener)
			req=urllib2.Request('http://www.google.com')  # change the URL to test here
			sock=urllib2.urlopen(req)
		
		except urllib2.HTTPError, e:
			print 'Error code: ', e.code
			return e.code
    
    		except Exception, detail:
			print "ERROR:", detail
			return True
		return False

	def check_proxy(self):
		socket.setdefaulttimeout(120)
		
		# two sample proxy IPs
		for currentProxy in self.unhealthy_proxies:
			if self.is_bad_proxy(currentProxy):
				print "Bad Proxy %s" % (currentProxy)
			else:
				print "%s is working" % (currentProxy)

if __name__ == '__main__':
	instance = ProxyHealthCheck()
	instance.check_proxy()
