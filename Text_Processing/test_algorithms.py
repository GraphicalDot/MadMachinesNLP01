#!/usr/bin/env python
#-*- coding: utf-8 -*-
#concatenating multiple feature extraction methods
#http://scikit-learn.org/stable/auto_examples/feature_stacker.html#example-feature-stacker-py


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
        sh = wb.get_sheet_by_name("14Jan")
        __ = [(element[2].lower(), element[3]) for element in [[cell.value for cell in r if cell.value] for r in sh.rows]][1: ]
        return [element for element in __ if __[1] != "mix"]


def generate_test_data_2():
        wb = openpyxl.load_workbook("/home/k/Programs/python/canworks/test_data.xlsx")
        sh = wb.get_sheet_by_name("15Jan")
        test_data = [[cell.value for cell in r] for r in sh.rows]
        __ = [(element[2].lower(), element[3]) for element in test_data[1:] if element[3] != "mix"]
        return __




def with_svm_countvectorizer(__text):
        tag_list = ["food", "service", "ambience", "cost", "null", "overall",]

        ##This is a lambda function which will extract reviews from the mongodb database and then extract list of sentences
        #Entered into every review corresponding to the tag given to it as an argument 
        from_db_data_lambda = lambda tag:  np.array([(sent.lower(), tag) for sent in list(itertools.chain(*[post.get(tag) for post in reviews.find() if post.get(tag)]))])
        
        #Our custom sentence tokenizer
        sent_tokenizer = SentenceTokenizationOnRegexOnInterjections()


        ##This is a lambda function which will extract text sentences from the manually_classified_files andtokenized them according
        #to sent_tokenizer
        data_lambda = lambda tag: np.array([(sent, tag) for sent in sent_tokenizer.tokenize(open("{0}/manually_classified_{1}.txt".format(path_trainers_file, tag), "rb").read(),) if sent != ""])             
        
       

        #This gives a list of tuples with every first element of the tuple as the sentence and 
        #second element as its tag 
        files_whole_set = list(itertools.chain(*map(data_lambda, tag_list)))
        #db_whole_set = list(itertools.chain(*map(from_db_data_lambda, tag_list)))
        whole_set = files_whole_set

        [random.shuffle(whole_set) for i in range(0, 10)]
        training_sentences, training_target_tags = zip(*whole_set)
        
        
        pca = PCA()
        selection = SelectKBest()


        combined_features = FeatureUnion([("pca", pca), ("univ_select", selection)])
        #classifier = Pipeline([('vect', CountVectorizer(ngram_range=(1, 2), min_df=1)), ('tfidf', TfidfTransformer()),
        classifier = Pipeline([ ('vect', TfidfVectorizer(ngram_range=(1, 2), min_df=1,)),
            ('chi2', SelectKBest(chi2, k=900)),
           # ("features", combined_features),
            ('clf', SGDClassifier(loss='hinge', penalty='elasticnet', alpha=1e-3, n_iter=5)),])   


        classifier.fit(training_sentences, training_target_tags)
        test_sentences, test_target = zip(*generate_test_data())
        predicted = classifier.predict(test_sentences)

        i = len([__tuple for __tuple in zip(test_target, predicted) if __tuple[0] != __tuple[1]])

        """
        for element in zip(test_sentences, test_target, predicted):
                if element[1] != element[2]:
                        print element[0], "\t", element[1], "\t", element[2]
        """



        print "Accuracy is with 200 samples %.3f"%(1 - float(i)/len(predicted))
        
        i = 0
        test_sentences, test_target = zip(*generate_test_data_2())
        predicted = classifier.predict(test_sentences)

        i = len([__tuple for __tuple in zip(test_target, predicted) if __tuple[0] != __tuple[1]])
        
        
        print "Accuracy is with 300 samples %.3f"%( 1 - float(i)/len(predicted))


        #sent_tokenizer = SentenceTokenizationOnRegexOnInterjections()
        #text = [sent.lower() for sent in sent_tokenizer.tokenize(__text)]
        


def with_svm(__text):
        tag_list = ["food", "service", "ambience", "cost", "null", "overall"]
        sent_tokenizer = SentenceTokenizationOnRegexOnInterjections()
        
        from_db_data_lambda = lambda tag:  np.array([(sent.lower(), tag) for sent in list(itertools.chain(*[post.get(tag) for post in reviews.find() if post.get(tag)]))])
        data_lambda = lambda tag: np.array([(sent, tag) for sent in sent_tokenizer.tokenize(open("{0}/manually_classified_{1}.txt".format(path_trainers_file, tag), "rb").read(),) if sent != ""])             
        
        
        files_whole_set = list(itertools.chain(*map(data_lambda, tag_list)))
        #db_whole_set = list(itertools.chain(*map(from_db_data_lambda, tag_list)))
        whole_set = files_whole_set

        whole_set = list(itertools.chain(*map(data_lambda, tag_list)))
        [random.shuffle(whole_set) for i in range(0, 10)]
        training_sentences, training_target_tags = zip(*whole_set)
        instance = SVMWithGridSearch(training_sentences, training_target_tags)
        classifier = instance.classifier()

        test_sentences, test_target = zip(*generate_test_data())
        predicted = classifier.predict(test_sentences)

        i = 0
        for __tuple in zip(test_target, predicted):
            if __tuple[0] != __tuple[1]:
                i += 1

        print "Accuracy with 200 samples with SVM grid search %.3f"%(1 - float(i)/len(predicted))
        
        i = 0
        test_sentences, test_target = zip(*generate_test_data_2())
        predicted = classifier.predict(test_sentences)

        i = len([__tuple for __tuple in zip(test_target, predicted) if __tuple[0] != __tuple[1]])
        
        print "Accuracy is with 300 samples with SM grid search%.3f"%(1 - float(i)/len(predicted))


if __name__ == "__main__":
        __text  = """Well this outlet of BBQ Nation is as good as the Kormngla or the J.p.nagar1 one. Amazing BBQ starters and kebabs. Main course and Dessert was good too. But as BBQ Nation is known for their starters and they always fulfill the expectations one foodie comes with. Good and prompt service. Went for family dinner and my brother-in-law was late to reach due to his work, and he reached around their closing time but still they served him properly even though rest all of us were done with our food. The only regret my jiju had was that Bar was closed by then and they dint serve even on request. Though I do not consider that as an issue because I believe rules are rules so it was ok with me. At least they served food properly that was really humble. Overall had a very good experience all over again."""
        with_svm_countvectorizer(__text)
        with_svm(__text)


