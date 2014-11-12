#!/usr/bin/env python
#-*- coding: utf-8 -*-

from NounPhrasesAnalysis import ProcessingWithBlob, PosTags
from helpers import nltk_ngrams
from Sentence_Tokenization import CopiedSentenceTokenizer, SentenceTokenizationOnRegexOnInterjections
from SentimentAnalysis import SentimentClassifier
from RepeatedRecommendedAnalysis import RpRcClassifier
from colored_print import bcolors
from TagAnalysis import TagClassifier
from MainAlgorithms import get_all_algorithms_result, path_parent_dir, path_trainers_file, path_in_memory_classifiers, timeit, cd
