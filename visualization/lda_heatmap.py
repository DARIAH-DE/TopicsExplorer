#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Function to generate a heatmap based on gensim

This module has been imported from the DARIAH project

To do: global paths, create figure dynamically, only show n-topics?
"""

__author__ = "DARIAH-DE"
__authors__ = "Stefan Pernes, Sina Bock"
__email__ = "stefan.pernes@uni-wuerzburg.de, sina.bock@stud-mail.uni-wuerzburg.de"
__license__ = ""
__version__ = "0.1"
__date__ = "2016-09-26"

from gensim.corpora import MmCorpus
from gensim.models import LdaModel
import numpy as np
import matplotlib.pyplot as plt
import os



# get path to gensim output files
path = os.path.join(os.getcwd(),"out")

########################################################################
# load gensim output files
########################################################################

doc_labels = []

# get document labels
print("\n get labels \n")
with open(os.path.join(path, "corpus_doclabels.txt"), "r") as f:
    for line in f: doc_labels.append(line)

# load corpus
print("\n load corpus \n")
corpus = MmCorpus(os.path.join(path,"corpus.mm"))

# load model
print("\n load model \n")
model = LdaModel.load(os.path.join(path,"corpus.lda"))

no_of_topics = model.num_topics
no_of_docs = len(doc_labels)


########################################################################
# get doc-topic matrix
########################################################################

doc_topic = np.zeros((no_of_docs, no_of_topics))

for doc, i in zip(corpus, range(no_of_docs)):           
    topic_dist = model.__getitem__(doc)                 # to get topic distribution from model
    for topic in topic_dist:                            # topic_dist is a list of tuples (topic_id, topic_prob)
        doc_topic[i][topic[0]] = topic[1]               # save topic probability


########################################################################
# get plot labels
########################################################################

topic_labels = []

for i in range(no_of_topics):
    topic_terms = [x[0] for x in model.show_topic(i, topn=3)]           # show_topic() returns tuples (word_prob, word)
    topic_labels.append(" ".join(topic_terms))


# cf. https://de.dariah.eu/tatom/topic_model_visualization.html

if no_of_docs > 20 or no_of_topics > 20: plt.figure(figsize=(20,20))    # if many items, enlarge figure
plt.pcolor(doc_topic, norm=None, cmap='Reds')
plt.yticks(np.arange(doc_topic.shape[0])+1.0, doc_labels)
plt.xticks(np.arange(doc_topic.shape[1])+0.5, topic_labels, rotation='90')
plt.gca().invert_yaxis()
plt.colorbar(cmap='Reds')
plt.tight_layout()

plt.savefig(os.path.join(path,"_heatmap.png"), dpi= 200)


