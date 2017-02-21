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
__version__ = "0.1"
__date__ = "2017-01-31"

from bs4 import BeautifulSoup
from dariah_topics import preprocessing as pre
import itertools
import math
import pandas as pd
import urllib.request as urllib
import wikipedia


def topic_segmenter(model, type2id, num_topics, permutation=False):
    """
    Combination:
    (W',W∗)|W' = {wi};
    W∗ = {wj};wi,wj ∈ W;i > j
    
    Permutation:
    (W',W*)|W' = {wi};
    W* = {wj};wi,wj ∈ W;i != j
    """
    bigrams = []
    for topic in range(num_topics):
        topic_nr_x = model.get_topic_terms(topic)
        tokens = [type2id[i[0]] for i in topic_nr_x]
        if permutation:
            bigrams.append(list(itertools.permutations(tokens, 2)))
        else:
            bigrams.append(list(itertools.combinations(tokens, 2)))
    return bigrams

def token_probability(corpus, segmented_topics):
    score = pd.Series()
    tokens = set()
    for topic in segmented_topics:
        for t1, t2 in topic:
            tokens.add(t1)
            tokens.add(t2)
    for token in tokens:
        temp_score = set()
        for n, document in enumerate(corpus):
            if token in document:
                temp_score.add(n)
        score[token] = temp_score
    return score

def calculate_umass(segmented_topics, token_probability, corpus, num_topics, top_words=10, e=0.1):
    pre_umass = []
    n = len(corpus)
    N = top_words*num_topics
    for topic in segmented_topics:
        for topic_bigram in topic:
            t1 = token_probability[topic_bigram[0]]
            t2 = token_probability[topic_bigram[1]]
            collocation = t1.intersection(t2)
            numerator = len(collocation)/n + e
            denominator = len(t2)/n
            pre_umass.append(math.log(numerator/denominator))
    return (2/(N*(N-1)))*sum(pre_umass)

def wikipedia_table_crawler(wiki_url='https://en.wikipedia.org/wiki/Wikipedia:5000', total_columns=15, select_cell=1):
    page_list = []
    page = urllib.urlopen(wiki_url)
    soup = BeautifulSoup(page, "lxml")
    table = soup.find("table", {"class": "wikitable sortable"})
    for row in table.findAll("tr"):
        cells = row.findAll("td")
        if len(cells) == total_columns:
            page_title = str(cells[select_cell].findAll(text=True))
            page_list.append(page_title)
    return page_list

def wikipedia_crawler(wiki_list, size=5000):
    wiki_corpus = []
    for site in wiki_list[:size]:
        try:
            full_site = wikipedia.page(site)
            tokens = list(pre.tokenize(full_site.content))
            wiki_corpus.append(tokens)
        except wikipedia.exceptions.DisambiguationError:
            pass
        except wikipedia.exceptions.HTTPTimeoutError:
            pass
        except wikipedia.exceptions.RedirectError:
            pass
        except wikipedia.exceptions.PageError:
            pass
        except wikipedia.exceptions.ConnectionError:
            pass
    return wiki_corpus

def calculate_pointwise_mutual_information(segmented_topics, corpus, score, e=0.1, normalize=False):
    PMI = []
    n = len(corpus)
    try:
        for topic in segmented_topics:
            for topic_bigram in topic:
                t1 = score[topic_bigram[0]]
                t2 = score[topic_bigram[1]]
                collocation = t1.intersection(t2)
                numerator = len(collocation)/n + e
                denominator = (len(t1)/n) * (len(t2)/n)
                if normalize:
                    PMI.append(math.log(numerator/denominator)/-math.log(numerator))
                else:
                    PMI.append(math.log(numerator/denominator))
    except ZeroDivisionError:
        PMI.append(0)
    return PMI

def calculate_uci(PMI, corpus, num_topics, top_words=10):
    n = len(corpus)
    N = num_topics*top_words
    score = (2/(N*(N-1)))*sum(PMI)
    return score
