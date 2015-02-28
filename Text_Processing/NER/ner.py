#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
Author: Kaali
Dated: 4th february, 2015
This file has a NERs class which extarcts the name, entity out of the text
"""
import os
import sys
import subprocess
import warnings
from nltk.tag.stanford import NERTagger

stanford_file_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print stanford_file_path
sys.path.append(os.path.join(stanford_file_path)) 

STANFORD_NER_LINK = "http://nlp.stanford.edu/software/stanford-ner-2015-01-29.zip"

class NERs:
        os.environ["JAVA_HOME"] = "{0}/jdk1.8.0_31/jre/bin/".format(stanford_file_path)
        def __init__(self, list_of_sentences, default_ner=None):
                self.ners = list()
                self.list_of_sentences = list_of_sentences
                self.ner = ("stanford_ner", default_ner)[default_ner != None]
                eval("self.{0}()".format(self.ner))
                self.ners = {self.ner: self.ners}
                return

            
        def stanford_ner(self):
                st = NERTagger('stanford-ner-2015-01-30/classifiers/english.all.3class.distsim.crf.ser.gz',
                                       'stanford-ner-2015-01-30/stanford-ner.jar')
                for __sentence in self.list_of_sentences:
                        self.ners.append(st.tag(__sentence.upper().split()))
                return

        def check_if_stanford_ner(self):
                """
                This method checks if the stanford ner is available or not
                """
                print "checking"
                if not os.path.exists("stanford-ner-2015-01-30"):
                        warnings.warn("Downloading the stanford ner") 
                        subprocess.call(["wget", STANFORD_NER_LINK])
                        subprocess.call(["unzip", "stanford-ner-2015-01-30.zip"])
                        subprocess.call(["rm", "-rf", "stanford-ner-2014-06-16.zip"])
                
                return



"""
if __name__ == "__main__":
        pp = NERs(['farzi cafe is decent restaurant located in south delhi'])
"""
