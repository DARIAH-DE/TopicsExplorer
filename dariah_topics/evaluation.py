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

import itertools
import math
import numpy as np


def segment_topics(topics, permutation=False):
    bigrams = []
    for n in range(len(topics)):
        if permutation:
            bigrams.append(
                list(itertools.permutations(topics.T[n].tolist(), 2)))
        else:
            bigrams.append(
                list(itertools.combinations(topics.T[n].tolist(), 2)))
    return pd.Series(bigrams)


def calculate_occurences(corpus, segmented_topics):
    occurences = pd.Series()
    keys = set()
    for topic in segmented_topics:
        for k1, k2 in topic:
            keys.add(k1)
            keys.add(k2)
    for key in keys:
        key_occurence = set()
        for n, document in enumerate(corpus):
            if key in document:
                key_occurence.add(n)
        occurences[key] = key_occurence
    return occurences


def calculate_umass_log(pair, occurences, corpus, e=0.1):
    k1 = occurences[pair[0]]
    k2 = occurences[pair[1]]
    k1k2 = k1.intersection(k2)
    numerator = len(k1k2) / len(corpus) + e
    denominator = len(k2) / len(corpus)
    return math.log(numerator / denominator)

def calculate_umass(corpus, topics, e=0.1):
    scores = []
    N = len(topics.T)
    segmented_topics = segment_topics(topics)
    occurences = calculate_occurences(corpus, segmented_topics)
    for topic in segmented_topics:
        logs = []
        for pair in topic:
            logs.append(calculate_umass_log(pair, occurences, corpus, e=e))
        scores.append((2 / (N * (N - 1))) * np.mean(logs))
    return scores


def calculate_pmi(pair, occurences, corpus, normalize=False, e=0.1):
    k1 = occurences[pair[0]]
    k2 = occurences[pair[1]]
    k1k2 = k1.intersection(k2)
    numerator = len(k1k2) / len(corpus) + e
    denominator = (len(k1) / len(corpus)) * ((len(k2) / len(corpus)))
    if normalize:
        return math.log(numerator / denominator) / -math.log(numerator)
    else:
        return math.log(numerator / denominator)


def calculate_uci(corpus, topics, normalize=False, e=0.1):
    scores = []
    N = len(topics.T)
    segmented_topics = segment_topics(topics)
    occurences = calculate_occurences(corpus, segmented_topics)
    for topic in segmented_topics:
        pmi = []
        for pair in topic:
            pmi.append(calculate_pmi(pair, occurences, corpus, normalize=normalize, e=e))
        scores.append((2 / (N * (N - 1))) * np.mean(pmi))
    return scores
