#!/usr/bin/env python
from Text_Processing.MainAlgorithms.paths import path_parent_dir, path_in_memory_classifiers 
from sklearn.externals import joblib

TAG_CLASSIFIER = "svm_linear_kernel_classifier_tag.lib"
SENTI_CLASSIFIER = "svm_linear_kernel_classifier_sentiment_new_dataset_30April.lib"
FOOD_SB_TAG_CLASSIFIER = "svm_linear_kernel_classifier_food_sub_tags_8May.lib"
COST_SB_TAG_CLASSIFIER = "svm_linear_kernel_classifier_cost.lib"
SERV_SB_TAG_CLASSIFIER = "svm_linear_kernel_classifier_service.lib"
AMBI_SB_TAG_CLASSIFIER =  "svm_linear_kernel_classifier_ambience.lib"
NOUN_PHSE_ALGORITHM_NAME = "topia"

TAG_CLASSIFY_ALG_NME = TAG_CLASSIFIER.replace(".lib", "")
SENTI_CLSSFY_ALG_NME = SENTI_CLASSIFIER.replace(".lib", "")
FOOD_SB_CLSSFY_ALG_NME = FOOD_SB_TAG_CLASSIFIER.replace(".lib", "")
SERV_SB_CLSSFY_ALG_NME = SERV_SB_TAG_CLASSIFIER.replace(".lib", "")
AMBI_SB_CLSSFY_ALG_NME = AMBI_SB_TAG_CLASSIFIER.replace(".lib", "")
COST_SB_CLSSFY_ALG_NME = COST_SB_TAG_CLASSIFIER.replace(".lib", "")

TAG_CLASSIFIER_LIB = joblib.load("{0}/{1}".format(path_in_memory_classifiers, TAG_CLASSIFIER)) 
SENTI_CLASSIFIER_LIB = joblib.load("{0}/{1}".format(path_in_memory_classifiers, SENTI_CLASSIFIER)) 
FOOD_SB_TAG_CLASSIFIER_LIB = joblib.load("{0}/{1}".format(path_in_memory_classifiers, FOOD_SB_TAG_CLASSIFIER))
COST_SB_TAG_CLASSIFIER_LIB = joblib.load("{0}/{1}".format(path_in_memory_classifiers, COST_SB_TAG_CLASSIFIER))
SERV_SB_TAG_CLASSIFIER_LIB = joblib.load("{0}/{1}".format(path_in_memory_classifiers, SERV_SB_TAG_CLASSIFIER))
AMBI_SB_TAG_CLASSIFIER_LIB = joblib.load("{0}/{1}".format(path_in_memory_classifiers, AMBI_SB_TAG_CLASSIFIER))
