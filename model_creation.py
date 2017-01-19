# -*- coding: utf-8 -*-
# DEPRECATED: All functions from this file should be migrated into or replaced
# with either:
#  * generic toolbox module             ---- currently both are collection.py
#  * topic modelling toolbox module     /

"""
This script creates a LDA model plus heatmap
"""

import os
import logging
import numpy as np
import matplotlib.pyplot as plt
from gensim import corpora, models, similarities

__author__ = "DARIAH-DE"
__authors__ = "Steffen Pielstroem"
__email__ = "pielstroem@biozentrum.uni-wuerzburg.de"
__version__ = "0.2"
__date__ = "2016-09-27"


########################################################################
# Prearrangements
########################################################################

# Enable gensim logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.INFO)

########################################################################
# Gensim model creation
########################################################################

def gensimModel(texts,
                topics=10,
                ldaSource='gensim',
                mallet_path='~/Software/mallet/bin/mallet'
                ):
    """
    Create model with gensim or mallet and return the model,
    dictionary, corpus and topics.

    Args:
        texts (List[str]): List of tokenized texts.
        topics (Optional[int]): Number of topics. Defaults to 10.
        ldaSource (Optional[str]): Which software? Defaults to gensim.
            ``gensim``
                For more information: http://radimrehurek.com/gensim/
            ``mallet``
                For more information: http://mallet.cs.umass.edu
        mallet_path (Optional[str]): Path to mallet.
        Defaults to `~/Software/mallet/bin/mallet`

    Todo:
        * Not sure yet if wrapping function is the optimal solution.
        * Future default `mallet_path = 'UNKNOWN'` or docker solution.
        * Mallet: find a function that opens a selection window
        * Store more info about model specifications

    Author:
        DARIAH-DE
    """

    # create dictionary and vectorize
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]

    # create a gensim type topic model
    if ldaSource == 'gensim':
        model = models.LdaModel(corpus,
                                id2word=dictionary,
                                num_topics=topics,
                                passes=10)
    else:
        if mallet_path == 'UNKNOWN':
            mallet_path = '~/Software/mallet/bin/mallet'
        model = models.wrappers.LdaMallet(
            mallet_path,  # Path to local mallet binary
            corpus,  # Vectorized copus object
            id2word=dictionary,
            num_topics=topics,  # Number of topics
            iterations=100  # Number of iterations in Gibbs sampling
        )

    # return results
    return [model, dictionary, corpus, topics]


def topicLabels(model, no_of_topics):
    """
    Generate topic labels from model.

    Args:
        model: Model created by :func:`gensimModel`.
        no_of_topics (Optional[int]): Number of topics. Defaults to 10.

    Todo:
        * Extract no_of_topics from corpus

    Author:
        DARIAH-DE
    """

    labels = []
    for i in range(no_of_topics):
        terms = [x[0] for x in model.show_topic(i, topn=3)]
        labels.append(" ".join(terms))
    return labels


def saveGensimModel(model,
                    corpus,
                    dictionary,
                    no_of_topics,
                    doc_labels,
                    foldername='corpus'
                    ):
    """
    Save all the gensim output in folder "out" (will be created if it
    doesn't exist yet).

    Args:
        model: Model created by :func:`gensimModel`.
        corpus: Corpus created by :func:`gensimModel`.
        dictionary: Dictionary created by :func:`gensimModel`.
        no_of_topics (Optional[int]): Number of topics. Defaults by 10.
        doc_labels (List[str]): Labels created by :func:`docLabels`.
        foldername (Optional[str]): Name of corpus folder.
        Defaults by corpus.

    Todo:
        * Extract no_of_topics from corpus

    Author:
        DARIAH-DE
    """

    topics = model.show_topics(num_topics=no_of_topics)
    if not os.path.exists("out"):
        os.makedirs("out")
    with open("out/" + foldername + "_doclabels.txt", "w") as f:
        for item in doc_labels:
            f.write(item + "\n")
    with open("out/" + foldername + "_topics.txt", "w") as f:
        for item, i in zip(topics, enumerate(topics)):
            f.write("topic #" + str(i[0]) + ": " + str(item) + "\n")
    dictionary.save("out/" + foldername + ".dict")
    corpora.MmCorpus.serialize("out/" + foldername + ".mm", corpus)
    model.save("out/" + foldername + ".lda")

########################################################################
# Doc-Topic matrix
########################################################################

def gensim_to_dtm(model, corpus, no_of_topics):
    """
    Create a doc-topic matrix from gensim output.

    Args:
        model: Model created by :func:`gensimModel`.
        corpus: Corpus created by :func:`gensimModel`.
        dictionary: Dictionary created by :func:`gensimModel`.
        no_of_topics (Optional[int]): Number of topics. Defaults by 10.

    Author:
        DARIAH-DE
    """

    no_of_docs = len(corpus)
    doc_topic = np.zeros((no_of_docs, no_of_topics))
    for doc, i in zip(corpus, range(no_of_docs)):
        # to get topic distribution from model
        topic_dist = model.__getitem__(doc)
        # topic_dist is a list of tuples (topic_id, topic_prob)
        for topic in topic_dist:
            doc_topic[i][topic[0]] = topic[1]   # save topic probability
    return doc_topic

########################################################################
# Topic visualization
########################################################################

def docTopHeatmap(doc_topic, doc_labels, topic_labels):
    """
    Create doc-topic heatmap (graph).

    Args:
        doc_topic: Doc-topic matrix created by :func:`gensim_to_dtm`.
        doc_labels: Labels created by :func:`docLabels`.
        topic_labels: Labels created by :func:`topicLabels`.

    Todo:
        * LDAvis not convinient on MS Windows, pip installation on
        Ubuntu failed too
        * http://nlp.stanford.edu/events/illvi2014/papers/sievert-illvi2014.pdf

    Author:
        DARIAH-DE
    """

    no_of_topics = len(doc_labels)
    no_of_topics = len(doc_labels)
    if no_of_topics > 20 or no_of_topics > 20:
        plt.figure(figsize=(20, 20))    # if many items, enlarge figure
    plt.pcolor(doc_topic, norm=None, cmap='Reds')
    plt.yticks(np.arange(doc_topic.shape[0])+1.0, doc_labels)
    plt.xticks(np.arange(doc_topic.shape[1])+0.5, topic_labels, rotation='90')
    plt.gca().invert_yaxis()
    plt.colorbar(cmap='Reds')
    plt.tight_layout()
    plt.show()
