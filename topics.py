#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "DARIAH-DE"
__authors__ = "Steffen Pielstroem"
__email__ = "pielstroem@biozentrum.uni-wuerzburg.de"
__license__ = ""
__version__ = "0.1"
__date__ = "2016-06-13"

########################################################################
# Load all dependencies
########################################################################

import glob
import os
import logging
import re
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from gensim import corpora, models, similarities

# Enable gensim logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.INFO)


def testing():
    """
    Check whether required packages (numpy, matplotlib, gensim) are
    correctly installed or not.

    Args:
        None

    Todo:
        * replace pkg_resources by another, more lightweighted module?

    Author:
        DARIAH-DE
    """

    try:
        import pkg_resources as pkg
        print(pkg.get_distribution("numpy").version, "\n",
              pkg.get_distribution("matplotlib").version, "\n",
              pkg.get_distribution("gensim").version)
    except ImportError:
        print("ERROR: Make sure all required packages are installed.")

########################################################################
# Corpus ingestion
########################################################################


def readCorpus(path):
    """
    Read corpus into a list of lists.

    Args:
        path (str): Path / glob pattern of the text files to process.

    Author:
        DARIAH-DE
    """

    files = glob.glob(path)
    documents = []
    for file in files:
        with open(file, 'r', encoding='utf-8') as document:
            document = document.read()
            documents.append(document)
    return documents


def docLabels(path):
    """
    Create a list of names (of the files) using paths and return a
    list.

    Args:
        path (str): Path/glob pattern of the text files to process.

    Author:
        DARIAH-DE
    """

    labels = [os.path.basename(x) for x in glob.glob(path)]
    labels = [x.split('.')[0] for x in labels]
    return labels

########################################################################
# Preprocessing
########################################################################


def tokenize(documents):
    """
    Tokenize (means breaking a stream of text up into words) text and
    return in a list of lists.

    Args:
        documents (List[str]): List of lists containing text.

    Todo:
        * Using version from gensim tutorial without regex?
            `texts = [[word for word in document.lower().split()]
                     for document in documents]`

    Author:
        DARIAH-DE
    """

    # define regular expression for tokenization
    myRegEx = re.compile('\w+')  # compile regex for fast repetition
    texts = []
    for document in documents:
        text = myRegEx.findall(document.lower())
        texts.append(text)
    return texts


def removeHapaxLeg(texts):
    """
    Remove hapax legomena (words that occurs only once within a
    context) and return text.

    Args:
        texts (List[str]): List of lists containing tokens.

    Author:
        DARIAH-DE
    """

    frequency = defaultdict(int)
    for text in texts:
        for token in text:
            frequency[token] += 1
        texts = [[token for token in text if frequency[token] > 1]
                 for text in texts]
    return texts


def removeStopWords(texts, stoplist):
    """
    Remove stopwords (usually refer to the most common words) according
    to selected stopword list and return text.

    Args:
        texts (List[str]): List of lists containing tokens.
        stoplist (str): Corpus language?

            ``de``
                German
            ``en``
                English
            ``es``
                Spanish
            ``fr``
                French

    Todo:
        * Replace `.helpful_stuff/stopwords/`

    Author:
        DARIAH-DE
    """

    if isinstance(stoplist, str):
        file = open('./helpful_stuff/stopwords/' + stoplist)
        stoplist = file.read()
        stoplist = [word for word in stoplist.split()]
        stoplist = set(stoplist)
    texts = [[word for word in text if word not in stoplist]
             for text in texts]
    return texts

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

    print("saving ...\n")
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
