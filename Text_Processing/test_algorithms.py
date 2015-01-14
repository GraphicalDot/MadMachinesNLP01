#!/usr/bin/env python
#-*- coding: utf-8 -*-
import pymongo
from Algortihms import  SVMWithGridSearch
from Sentence_Tokenization import SentenceTokenizationOnRegexOnInterjections, CopiedSentenceTokenizer
import random
import itertools
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer 
from sklearn.linear_model import SGDClassifier                                                                                                            
from sklearn.pipeline import Pipeline 
from sklearn.feature_extraction.text import TfidfTransformer 
import openpyxl


connection = pymongo.Connection()
db = connection.modified_canworks
reviews = db.review

def generate_test_data():
        wb = openpyxl.load_workbook("/home/k/Programs/python/canworks/test_data.xlsx")
        sh = wb.get_active_sheet()
        __ = [(element[2].lower(), element[3]) for element in [[cell.value for cell in r if cell.value] for r in sh.rows]][1: ]
        return [element for element in __ if __[1] != "mix"]

def with_svm_countvectorizer(__text):
        tag_list = ["food", "service", "ambience", "cost", "null", "overall",]
        data_lambda = lambda tag:  np.array([(sent.lower(), tag) for sent in list(itertools.chain(*[post.get(tag) for post in reviews.find() if post.get(tag)]))])
        whole_set = list(itertools.chain(*map(data_lambda, tag_list)))
        [random.shuffle(whole_set) for i in range(0, 10)]
        training_sentences, training_target_tags = zip(*whole_set)
        classifier = Pipeline([('vect', CountVectorizer(ngram_range=(1, 3))), ('tfidf', TfidfTransformer()),
            ('clf', SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, n_iter=5)),])   


        classifier.fit(training_sentences, training_target_tags)
        test_sentences, test_target = zip(*generate_test_data())
        predicted = classifier.predict(test_sentences)

        i = len([__tuple for __tuple in zip(test_target, predicted) if __tuple[0] != __tuple[1]])

        for element in zip(test_sentences, test_target, predicted):
                print element[0], "\t", element[1], "\t", element[2], "\n"

        print "accuracy is %.3f"%(float(i)/len(predicted))


        #sent_tokenizer = SentenceTokenizationOnRegexOnInterjections()
        #text = [sent.lower() for sent in sent_tokenizer.tokenize(__text)]
        


def with_svm(__text):
        tag_list = ["food", "service", "ambience", "cost", "null", "overall", "mix"]
        data_lambda = lambda tag:  np.array([(sent.lower(), tag) for sent in list(itertools.chain(*[post.get(tag) for post in reviews.find() if post.get(tag)]))])
        whole_set = list(itertools.chain(*map(data_lambda, tag_list)))
        [random.shuffle(whole_set) for i in range(0, 10)]
        training_sentences, training_target_tags = zip(*whole_set)
        instance = SVMWithGridSearch(training_sentences, training_target_tags)
        classifier = instance.classifier()

        sent_tokenizer = SentenceTokenizationOnRegexOnInterjections()
        test_sentences, test_target = zip(*generate_test_data())
        predicted = classifier.predict(test_sentences)

        i = 0
        for __tuple in zip(test_target, predicted):
            if __tuple[0] != __tuple[1]:
                i += 1

        print "accuracy is %.3f"%(float(i)/len(predicted))


if __name__ == "__main__":
        __text  = """Well this outlet of BBQ Nation is as good as the Kormngla or the J.p.nagar1 one. Amazing BBQ starters and kebabs. Main course and Dessert was good too. But as BBQ Nation is known for their starters and they always fulfill the expectations one foodie comes with. Good and prompt service. Went for family dinner and my brother-in-law was late to reach due to his work, and he reached around their closing time but still they served him properly even though rest all of us were done with our food. The only regret my jiju had was that Bar was closed by then and they dint serve even on request. Though I do not consider that as an issue because I believe rules are rules so it was ok with me. At least they served food properly that was really humble. Overall had a very good experience all over again."""
        with_svm_countvectorizer(__text)
        #with_svm(__text)


