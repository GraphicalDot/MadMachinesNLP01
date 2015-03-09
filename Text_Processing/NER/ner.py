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
from nltk import ne_chunk
from nltk.tag.stanford import NERTagger
import nltk
file_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(file_path)) 

base_file_path = os.path.dirname(os.path.abspath(__file__))

STANFORD_NER_LINK = "http://nlp.stanford.edu/software/stanford-ner-2015-01-29.zip"

class NERs:
        os.environ["JAVA_HOME"] = "{0}/jdk1.8.0_31/jre/bin/".format(file_path)
        def __init__(self, list_of_sentences, default_ner=None):
                self.check_if_stanford_ner()
                self.ners = list()
                self.list_of_sentences = list_of_sentences
                self.ner = ("stanford_ner", default_ner)[default_ner != None]
                eval("self.{0}()".format(self.ner))
                self.ners = {self.ner: self.ners}
                return

            
        def stanford_ner(self):
                st = NERTagger('{0}/stanford-ner-2015-01-30/classifiers/english.all.3class.distsim.crf.ser.gz'.format(base_file_path),
                                       '{0}/stanford-ner-2015-01-30/stanford-ner.jar'.format(base_file_path))
                for __sentence in self.list_of_sentences:
                        ##TODO: the passes list will be a pos tagged sentenc, make it to a simple sentence
                        #__sentence = " ".join([element[0] for element in __sentence])
                        output = st.tag(__sentence.split())
                        chunked, pos, prev_tag = [], "", ""
                        for i, word_pos in enumerate(output): 
                                word, pos = word_pos
                                if pos in ['PERSON', 'ORGANIZATION', 'LOCATION'] and pos == prev_tag:
                                        chunked[-1]+=word_pos
                                else:
                                        chunked.append(word_pos)
                                prev_tag = pos

                        clean_chunked = [tuple([" ".join(wordpos[::2]), wordpos[-1]]) if len(wordpos)!=2 else wordpos for wordpos in chunked]
                        for element in clean_chunked:
                            if element[1] == "LOCATION" or element[1] == "ORGANIZATION":
                                self.ners.append(element[0])
                return


        def nltk_maxent_ner(self):
                for __sentence in self.list_of_sentences:
                       tree =  ne_chunk(__sentence) 
                       for subtree in tree.subtrees(filter = lambda t: t.label()=='ORGANIZATION' or t.label() == "LOCATION"):
                                self.ners.append(" ".join([e[0] for e in subtree.leaves()]))


        def check_if_stanford_ner(self):
                """
                This method checks if the stanford ner is available or not
                """
                if not os.path.exists("{0}/stanford-ner-2015-01-30".format(base_file_path)):
                        warnings.warn("Downloading the stanford ner") 
                        subprocess.call(["wget", STANFORD_NER_LINK])
                        subprocess.call(["unzip", "stanford-ner-2015-01-30.zip"])
                        subprocess.call(["rm", "-rf", "stanford-ner-2015-01-30.zip"])
                
                return



if __name__ == "__main__":
        sentence = "I went to South Delhi last night"
        pp = NERs([sentence])
        p = NERs([nltk.pos_tag(nltk.wordpunct_tokenize(sentence))],  default_ner="nltk_maxent_ner")
        print "From NLTK Maxent chunker"
        print pp.ners, "\n"
        print "From standford NER"
        print p.ners, "\n"

