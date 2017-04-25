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


def _segment_topics(topics, permutation=False):
    bigrams = []
    for n in range(len(topics)):
        if permutation:
            bigrams.append(
                list(itertools.permutations(topics.T[n].tolist(), 2)))
        else:
            bigrams.append(
                list(itertools.combinations(topics.T[n].tolist(), 2)))
    return pd.Series(bigrams)


def _calculate_occurences(corpus, segmented_topics):
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


def calculate_umass(corpus, topics, e=0.1):
    scores = []
    N = len(topics.T)
    n_corpus = len(corpus)
    segmented_topics = _segment_topics(topics, permutation=True)
    occurences = _calculate_occurences(corpus, segmented_topics)
    for topic in segmented_topics:
        log = []
        for bigram in topic:
            k1 = occurences[bigram[0]]
            k2 = occurences[bigram[1]]
            collocation = k1.intersection(k2)
            try:
                numerator = len(collocation) / n_corpus + e
                denominator = len(k2) / n_corpus
                log.append(math.log(numerator / denominator))
            except ZeroDivisionError:
                log.append(0)
        scores.append(log)
    return [(2 / (N * (N - 1))) * sum(umass) for umass in scores]


def calculate_pmi(corpus, topics, normalize=False, e=0.1):
    pmi = []
    segmented_topics = _segment_topics(topics, permutation=False)
    occurences = _calculate_occurences(corpus, segmented_topics)
    for topic in segmented_topics:
        scores = []
        for bigram in topic:
            k1 = occurences[bigram[0]]
            k2 = occurences[bigram[1]]
            collocation = k1.intersection(k2)
            try:
                numerator = len(collocation) / len(corpus) + e
                denominator = (len(k1) / len(corpus) * (len(k2) / len(corpus)))
                if normalize:
                    scores.append(
                        math.log(numerator / denominator) / -math.log(numerator))
                else:
                    scores.append(math.log(numerator / denominator))
            except ZeroDivisionError:
                scores.append(0)
        pmi.append(scores)
    return pmi


def calculate_uci(corpus, topics, pmi):
    N = len(topics.T)
    return [(2 / (N * (N - 1))) * sum(scores) for scores in pmi]
