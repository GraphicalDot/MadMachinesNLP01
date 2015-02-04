#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author: Kaali
Dated: 3 february, 2015
For the pos tagging of the list of sentences
"""
import os
import sys
import subprocess
import warnings
from textblob import TextBlob                                              
from nltk import wordpunct_tokenize
from nltk import pos_tag as nltk_pos_tag
from nltk.tag.hunpos import HunposTagger
from nltk.tag.stanford import POSTagger
stanford_file_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))                                    
sys.path.append(os.path.join(stanford_file_path))  



class PosTaggers:
        os.environ["JAVA_HOME"] = "{0}/ForStanford/jdk1.8.0_31/jre/bin/".format(stanford_file_path)
        stanford_jar_file = "{0}/ForStanford/stanford-postagger.jar".format(stanford_file_path) 
        stanford_tagger = "{0}/ForStanford/models/english-bidirectional-distsim.tagger".format(stanford_file_path) 
        def __init__(self, list_of_sentences, default_pos_tagger=None):
                """
                Args:
                    list_of_sentences:
                        list of lists with each element in the main list as the sentence which is word_tokenized

                        if you want to pos tag on multithread just pass the word tokenized sentence in a list, 
                        that obviously will be considered as a list of length a length one
                
                    default_pos_tagger:
                        type: string
                        options:
                                stan_pos_tagger
                                hunpos_pos_tagger
                                nltk_pos_tagger
                                textblob_pos_tagger
                """

                self.check_if_hunpos() 
                self.hunpos_tagger = HunposTagger('hunpos-1.0-linux/en_wsj.model','hunpos-1.0-linux/hunpos-tag')
                self.stanford_tagger = POSTagger(self.stanford_tagger, self.stanford_jar_file) 
                
                self.list_of_sentences = list_of_sentences
                self.pos_tagged_sentences = list()
                self.pos_tagger = ("stan_pos_tagger", default_pos_tagger)[default_pos_tagger != None]                
                eval("self.{0}()".format(self.pos_tagger))

                self.pos_tagged_sentences = {self.pos_tagger: self.pos_tagged_sentences}
                return 

        def check_if_hunpos(self):
                """
                This method checks if the executabled of hunpos exists or not
                """
                if not os.path.exists("hunpos-1.0-linux"):
                        warnings.warn("Downloading the hun pos tagger files as they werent here,to be used for tagging")
                        subprocess.call(["wget", "https://hunpos.googlecode.com/files/hunpos-1.0-linux.tgz"])
                        subprocess.call(["wget", "https://hunpos.googlecode.com/files/en_wsj.model.gz"])
                        subprocess.call(["tar", "xvfz", "hunpos-1.0-linux.tgz"])
                        subprocess.call(["gunzip", "en_wsj.model.gz"])
                        subprocess.call(["mv", "en_wsj.model", "hunpos-1.0-linux"])
                        subprocess.call(["rm", "-rf", "en_wsj.model.gz.1"])
                        subprocess.call(["rm", "-rf", "hunpos-1.0-linux.tgz"]) 


        def hunpos_pos_tagger(self):
                for __sentence in self.list_of_sentences:
                        self.pos_tagged_sentences.append(self.hunpos_tagger.tag(__sentence))
                return

        def stan_pos_tagger(self):
                for __sentence in self.list_of_sentences:
                        try:
                            __tagged_sentence = self.stanford_tagger.tag(__sentence)
                            print __tagged_sentence
                            self.pos_tagged_sentences.append(__tagged_sentence)
                        except Exception:
                            pass
                return

        def textblob_pos_tagger(self):
                for __sentence in self.list_of_sentences:
                        __sentence = " ".join([ element for element in __sentence])
                        blob = TextBlob(__sentence)
                        self.pos_tagged_sentences.append(blob.pos_tags)
                return 

        def nltk_pos_tagger(self):
                for __sentence in self.list_of_sentences:
                        self.pos_tagged_sentences.append(nltk_pos_tag(__sentence))
                return
"""
if __name__ == "__main__":
        p = PosTaggers([wordpunct_tokenize("I went there to have chicken pizza")], default_pos_tagger="nltk_pos_tagger")
        print p.pos_tagged_sentences
"""

