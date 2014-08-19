#!/usr/bin/env python

from urllib2 import Request, urlopen

import sys, lxml

from lxml import etree
from io import StringIO
from contextlib import closing

import unicodecsv

playcount_path = etree.XPath("playcount")
name_path = etree.XPath("name")

username = sys.argv[1]

sources = ["artist","track"]
link_fmt = "http://ws.audioscrobbler.com/2.0/user/%s/top%ss.xml"
item_fmt = "%s"

links = [link_fmt % (username, source) for source in sources]
item_paths = [etree.XPath(item_fmt % source) for source in sources]

headers = ["rank","name","playcount"]

for link,item_path,source in zip(links,item_paths,sources):
	page = 1
	pages = 1
	while page <= pages:
		print "Fetching",source,"page",page,"of",("?" if page == 1 else pages),"...\t",
		req = Request("%s?page=%d"%(link,page))
		with closing(urlopen(req)) as response:
			the_page = response.read()
			print "done."
			
			root = etree.fromstring(the_page)
			pages = int(root.get("totalPages"))
			
			print "Reading",source,"page",page,"of",pages,"...\t",
			items = item_path(root)
			rows = [[item.get("rank"), name_path(item)[0].text, playcount_path(item)[0].text] for item in items]
			print "done."
			print "Writing",source,"page",page,"of",pages,"...\t",
	
			with open("%s.csv" % source ,'w' if page == 1 else "a") as f:
				writer = unicodecsv.writer(f,dialect='excel')
				for row in ([headers] if page == 1 else [])+rows:
					writer.writerow(row)
			print "done."
		#print (page,type(page)),(pages,type(pages)),page<=pages
		page += 1
