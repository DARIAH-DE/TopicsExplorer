#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Topic Model Evaluation.
This module contains functions to calculate topic coherence provided by `DARIAH-DE`_.
.. _DARIAH-DE:
    https://de.dariah.eu
    https://github.com/DARIAH-DE
"""

__author__ = "DARIAH-DE"
__authors__ = "Severin Simmler"
__email__ = "severin.simmler@stud-mail.uni-wuerzburg.de"

from itertools import permutations, combinations
import numpy as np
import pandas as pd


def token2bow(token, type_dictionary):
    try:
        return type_dictionary[token]
    except KeyError:
        type_dictionary[token] = len(type_dictionary) + 1
        return type_dictionary[token]


class Preprocessing:
    def __init__(self, topics, sparse_bow, type_dictionary):
        self.topics = topics
        self.sparse_bow = sparse_bow
        self.type_dictionary = type_dictionary


    def segment_topics(self, permutation=False):
        bigrams = []
        for topic in self.topics.iterrows():
            topic = [token2bow(token, self.type_dictionary) for token in topic[1]]
            if permutation:
                bigrams.append(list(permutations(topic, 2)))
            else:
                bigrams.append(list(combinations(topic, 2)))
        return pd.Series(bigrams)


    def calculate_occurences(self, bigrams):
        bow = self.sparse_bow.reset_index(level=1)['token_id']
        occurences = pd.Series()
        if isinstance(bigrams, set):
            pass
        else:
            keys = set()
            for topic in bigrams:
                for bigram in topic:
                    keys.add(bigram[0])
                    keys.add(bigram[1])
        for key in keys:
            total = set()
            for doc in bow.groupby(level=0):
                if key in doc[1].values:
                    total.add(doc[0])
            occurences[str(key)] = total
        return occurences

class Measures(Preprocessing):
    def __init__(self, sparse_bow, type_dictionary):
        self.type_dictionary = type_dictionary
        self.sparse_bow = sparse_bow


    def pmi_uci(self, pair, occurences, e=0.1, normalize=False):
        n = len(self.sparse_bow.index.levels[0])
        k1 = occurences[str(pair[0])]
        k2 = occurences[str(pair[1])]
        k1k2 = k1.intersection(k2)
        numerator = len(k1k2) + e / n
        denominator = ((len(k1) + e) / n) * ((len(k2) + e) / n)
        if normalize:
            return np.log(numerator / denominator) / -np.log(numerator)
        else:
            return np.log(numerator / denominator)


    def pmi_umass(self, pair, occurences, e=0.1):
        n = len(self.sparse_bow.count(level=0))
        k1 = occurences[str(pair[0])]
        k2 = occurences[str(pair[1])]
        k1k2 = k1.intersection(k2)
        numerator = len(k1k2) + e / n
        denominator = len(k2) + e / n
        return np.log(numerator / denominator)


class Evaluation(Measures):
    def __init__(self, topics, sparse_bow, type_dictionary):
        self.topics = topics
        self.sparse_bow = sparse_bow
        self.type_dictionary = type_dictionary


    def calculate_umass(self, mean=True, e=0.1):
        scores = []
        N = len(self.topics.T)
        segmented_topics = self.segment_topics()
        occurences = self.calculate_occurences(bigrams=segmented_topics)
        for topic in segmented_topics:
            pmi = []
            for pair in topic:
                pmi.append(self.pmi_umass(pair=pair, occurences=occurences, e=e))
            if mean:
                scores.append((2 / (N * (N - 1))) * np.mean(pmi))
            else:
                scores.append((2 / (N * (N - 1))) * np.median(pmi))
        return pd.Series(scores)


    def calculate_uci(self, mean=True, normalize=False, e=0.1):
        scores = []
        N = len(self.topics.T)
        segmented_topics = self.segment_topics(permutation=True)
        occurences = self.calculate_occurences(bigrams=segmented_topics)
        for topic in segmented_topics:
            pmi = []
            for pair in topic:
                pmi.append(self.pmi_uci(pair=pair, occurences=occurences, normalize=normalize, e=e))
            if mean:
                scores.append((2 / (N * (N - 1))) * np.mean(pmi))
            else:
                scores.append((2 / (N * (N - 1))) * np.median(pmi))
        return pd.Series(scores)
