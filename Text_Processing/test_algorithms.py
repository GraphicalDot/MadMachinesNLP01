#!/usr/bin/env python
#-*- coding: utf-8 -*-
#concatenating multiple feature extraction methods
#http://scikit-learn.org/stable/auto_examples/feature_stacker.html#example-feature-stacker-py
"""
http://scikit-learn.org/stable/modules/generated/sklearn.multiclass.OneVsOneClassifier.html
http://stackoverflow.com/questions/17794313/unexpected-results-when-using-scikit-learns-svm-classification-algorithm-rbf-k?rq=1
http://scikit-learn.org/0.13/auto_examples/grid_search_digits.html#example-grid-search-digits-py
http://scikit-learn.org/stable/auto_examples/grid_search_digits.html
http://scikit-learn.org/0.13/modules/grid_search.html
http://scikit-learn.org/0.13/auto_examples/grid_search_digits.html#example-grid-search-digits-py
http://scikit-learn.org/0.13/auto_examples/grid_search_text_feature_extraction.html#example-grid-search-text-feature-extraction-py
http://stackoverflow.com/questions/23815938/recursive-feature-elimination-and-grid-search-using-scikit-learn?rq=1
http://stackoverflow.com/questions/14866228/combining-grid-search-and-cross-validation-in-scikit-learn?rq=1
http://stackoverflow.com/questions/15254243/different-accuracy-for-libsvm-and-scikit-learn?rq=1

"""

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
from sklearn.feature_extraction.text import TfidfVectorizer
import openpyxl

from sklearn.feature_selection import SelectKBest, chi2
from MainAlgorithms import path_in_memory_classifiers, path_trainers_file, path_parent_dir
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.grid_search import GridSearchCV
from sklearn.svm import SVC
from sklearn.datasets import load_iris
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest
from sklearn.lda import LDA
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC
from sklearn.grid_search import GridSearchCV
from sklearn.svm import SVC

connection = pymongo.Connection()
db = connection.modified_canworks
reviews = db.review


def print_term_frequencies(corpus):
        """
        Corpus shall be in the form of 
        corpus = ["This is very strange",
                          "This is very nice"]

        """
        vectorizer = TfidfVectorizer(min_df=1)
        X = vectorizer.fit_transform(corpus)
        idf = vectorizer._tfidf.idf_
        print dict(zip(vectorizer.get_feature_names(), idf))





def generate_test_data():
        wb = openpyxl.load_workbook("/home/k/Programs/python/canworks/test_data.xlsx")
        sh = wb.get_active_sheet()
        __ = [(element[2].lower(), element[3]) for element in [[cell.value for cell in r if cell.value] for r in sh.rows]][1: ]
        return [element for element in __ if __[1] != "mix"]


def generate_test_data_2():
        wb = openpyxl.load_workbook("/home/k/Programs/python/canworks/test_data.xlsx")
        sh = wb.get_sheet_by_name("15Jan")
        test_data = [[cell.value for cell in r] for r in sh.rows]
        __ = [(element[2].lower(), element[3]) for element in test_data[1:] if element[3] != "mix"]
        return __

def return_tags_training_set():
        tag_list = ["food", "service", "ambience", "cost", "null", "overall",]
        from_db_data_lambda = lambda tag:  np.array([(sent.lower(), tag) for sent in list(itertools.chain(*[post.get(tag) for post in reviews.find() if post.get(tag)]))])
        db_whole_set = list(itertools.chain(*map(from_db_data_lambda, tag_list)))
        [random.shuffle(db_whole_set) for i in range(0, 10)]
        training_sentences, training_target_tags = zip(*db_whole_set)
        return (training_sentences, training_target_tags)

def with_svm_countvectorizer():
        pca = PCA()
        selection = SelectKBest()


        #classifier = Pipeline([('vect', CountVectorizer(ngram_range=(1, 2), min_df=1)), ('tfidf', TfidfTransformer()),
        classifier = Pipeline([ ('vect', TfidfVectorizer(ngram_range=(1, 2), min_df=1,)),
            ('chi2', SelectKBest(chi2, k=900)),
            ('clf', SGDClassifier(loss='hinge', penalty='elasticnet', alpha=1e-3, n_iter=5)),])   


        classifier.fit(TAGS_TRAINING_SENTENCES, TAG_TARGETS)
        print "Accuracy with 200 samples with SVM %.3f"%(classifier.score(TEST_SENTENCES, TEST_TARGET))

       

def sgd_with_grid_search():
        pipeline = Pipeline([ ('vect', CountVectorizer()),
                                        ('tfidf', TfidfTransformer()),
                                        ('chi2', SelectKBest(chi2, k="all")),
                                        ('clf', SGDClassifier()),
                                        ])

        parameters = { 'vect__max_df': (0.5, 0.75, 1.0),
                                'vect__max_features': (None, 500, 1000),
                                'vect__ngram_range': [(1, 1), (1,4)],  # unigrams or bigrams
                                'tfidf__use_idf': (True, False),
                                'tfidf__norm': ('l1', 'l2'),
                                'clf__alpha': (0.00001, 0.000001),
                                'clf__penalty': ('l1', 'elasticnet'),
                                'clf__n_iter': (10, 50, 80),
                                }
        
        classifier= GridSearchCV(pipeline, parameters, verbose=1)



        classifier.fit(TAGS_TRAINING_SENTENCES, TAG_TARGETS)
        print "Accuracy with 200 samples with LDA %.3f"%(classifier.score(TEST_SENTENCES, TEST_TARGET))
        print "Best score: %0.3f" % classifier.best_score_
        print "Best parameters set:"
        best_parameters = classifier.best_estimator_.get_params()
        for param_name in sorted(parameters.keys()):
                print "\t%s: %r" % (param_name, best_parameters[param_name])



def with_svm():
        
        training_sentences, training_target_tags = return_tags_training_set()

        instance = SVMWithGridSearch(TAGS_TRAINING_SENTENCES, TAG_TARGETS)
        classifier = instance.classifier()


        print "Accuracy with 200 samples with SVM grid search %.3f"%(classifier.score(TEST_SENTENCES, TEST_TARGET))
        classifier= GridSearchCV(pipeline, tuned_parameters, verbose=1)



        classifier.fit(TAGS_TRAINING_SENTENCES, TAG_TARGETS)
        print "Accuracy with 200 samples with LDA %.3f"%(classifier.score(TEST_SENTENCES, TEST_TARGET))
        print "Best score: %0.3f" % classifier.best_score_
        print "Best parameters set:"
        best_parameters = classifier.best_estimator_.get_params()
        for param_name in sorted(parameters.keys()):
                print "\t%s: %r" % (param_name, best_parameters[param_name])

        


def with_lda():
                                        
        pipeline = Pipeline([ ('vect', CountVectorizer()),
                                    ('tfidf', TfidfTransformer()),
                                        #('chi2', SelectKBest(chi2, k="all")),
                                        ('clf', SVC()),
                                        #('clf', SGDClassifier()),
                                        ])


        parameters = {'clf__kernel': ['linear', 'rbf',], 
                            'clf__gamma': [1e-3, 1e-4],
                            'clf__C': [1, 10, 100, 1000]
                                 }



        classifier= GridSearchCV(pipeline, parameters, verbose=1)



        classifier.fit(TAGS_TRAINING_SENTENCES, TAG_TARGETS)
        print "Accuracy with 200 samples with LDA %.3f"%(classifier.score(TEST_SENTENCES, TEST_TARGET))
        print "Best score: %0.3f" % classifier.best_score_
        print "Best parameters set:"
        best_parameters = classifier.best_estimator_.get_params()
        for param_name in sorted(parameters.keys()):
                print "\t%s: %r" % (param_name, best_parameters[param_name])



if __name__ == "__main__":
        TAGS_TRAINING_SENTENCES, TAG_TARGETS = return_tags_training_set()
        TEST_SENTENCES, TEST_TARGET = zip(*generate_test_data())
        #with_svm_countvectorizer()
        #:with_svm()
        #with_lda()
        sgd_with_grid_search()

