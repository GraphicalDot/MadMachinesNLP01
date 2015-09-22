#!/usr/bin/env python

import os
import jsonrpclib

from simplejson import loads

import nltk
from nltk import Tree
from nltk.draw.util import CanvasFrame
from nltk.draw import TreeWidget
from nltk.corpus import wordnet
import hashlib
import subprocess



server = jsonrpclib.Server("http://localhost:3456")
result =  loads(server.parse("Bell, based in Los Angeles, it distributes electronic, computer and building products"))
filepath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(filepath, "treeFiles")

if not os.path.exists(path):
        print "path doesnt exists"
        os.mkdir(path)







"""
for sent in tokenized_sentences:
        result = loads(server.parse(sent))
        sentences = result["sentences"]
        location = list()
        try:

                for __sent in sentences[0].get("words"):
                        if __sent[1].get("NamedEntityTag") == 'LOCATION':
                                location.append(__sent[0])
                if location:
                        print sent, "<------>", " ".join(location)
                        result.append([sent, " ".join(location)])
        except Exception as e:
                pass

"""
class cd:
        """Context manager for changing the current working directory"""
        def __init__(self, newPath):
                self.newPath = os.path.expanduser(newPath)

        def __enter__(self):
                self.savedPath = os.getcwd()
                os.chdir(self.newPath)

        def __exit__(self, etype, value, traceback):
                os.chdir(self.savedPath)









def save_tree(sentence):
        result = loads(server.parse(sentence))
        tree = result["sentences"][0]["parsetree"]
        cf = CanvasFrame()
                                
        name = hashlib.md5(sentence).hexdigest()

        t = nltk.tree.Tree.fromstring(tree)
        tc = TreeWidget(cf.canvas(), t)
        cf.add_widget(tc, 10,10) # (10,10) offsets
        with cd(path):
                cf.print_to_file('{0}.ps'.format(name))
                subprocess.call(["convert",  "-density",  "100",  "{0}.ps".format(name), "-resize", "100%", "-gamma",  "2.2", "-quality",  "92", "{0}.jpg".format(name)])
                #subprocess.call(["convert",  "{0}.ps".format(name), "{0}.jpg".format(name)])
        cf.destroy()

        print "{0}/{1}.jpg".format(path, name)
        return "{0}/{1}.jpg".format(path, name)





if __name__ == "__main__":
        save_tree("Hey man")
