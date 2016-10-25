#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Topic Modeling and LDA visualization.

This module contains various `Gensim`_ related functions for topic modeling and
LDA visualization provided by `DARIAH-DE`_.

.. _Gensim:
    https://radimrehurek.com/gensim/index.html
.. _DARIAH-DE:
    https://de.dariah.eu
    https://github.com/DARIAH-DE
"""

__author__ = "DARIAH-DE"
__authors__ = "Stefan Pernes, Steffen Pielstroem, Philip Duerholt, Sina Bock, Severin Simmler"
__email__ = "stefan.pernes@uni-wuerzburg.de, pielstroem@biozentrum.uni-wuerzburg.de"
__version__ = "0.3"
__date__ = "2016-10-25"

import pandas as pd
import re
import os
import csv
import glob
import pyLDAvis.gensim
import numpy as np
import matplotlib.pyplot as plt
import sys
import logging
from gensim.corpora import MmCorpus, Dictionary
from gensim.models import LdaModel

log = logging.getLogger('collection')
log.addHandler(logging.NullHandler())
logging.basicConfig(level = logging.INFO,
                    format = '%(asctime)s %(levelname)s %(name)s: %(message)s',
                    datefmt = '%d-%b-%Y %H:%M:%S')

def create_document_list(path, ext='.txt'):
    """Creates a list of files with their full path.

    Args:
        path (str): Path to folder, e.g. '/tmp/corpus'.
        ext (str): File extension, e.g. '.csv'. Defaults to '.txt'.

    Returns:
        list[str]: List of files with full path.
    """
    
    log.info("Creating document list from %s files ...", ext)
    doclist = glob.glob(path + "/*" + ext)
    log.debug("Document list successfully created.")
    return doclist

def read_from_txt(doclist):
    """Opens files using a list of paths.

    Note:
        Use `create_document_list()` to create `doclist`.
        
    Args:
        doclist (list[str]): List of all documents in the corpus.
        
    Yields:
        Documents in `doclist`.

    Todo:
        Seperate metadata (author, header)?
    """
    log.info("Accessing documents ...")
    for file in doclist:
        with open(file, 'r', encoding = 'utf-8') as f:
            yield f.read()
    log.debug("Documents successfully accessed.")

def segmenter(doc, length):
    """Segments documents.

    Note:
        Use `ReadFromTXT` to create `doc`.
        
    Args:
        doc (str): Document as iterable.
        length (int): Target size of segments, e.g. 1000.
    
    Yields:
        Document slizes with length words.

    Todo:
        Implement fuzzy option to consider paragraph breaks.              
    """
    log.info("Segmenting documents ...")
    doc = next(doc)
    for i, word in enumerate(doc):
        if i % length == 0:
            yield doc[i : i + length]
    log.debug("Documents successfully segmented.")

def filter_POS_tags(doclist_csv, pos_tags, columns):
    """Gets selected POS-tags from DKPro-Wrapper output.

    Args:
        doclist (list[str]): List of DKPro output files that should be selected
        pos_tags (list[str]): List of DKPro pos_tags that should be selected
        columns (list[str]): List of columns that should be selected
        
    Yields:
        Lemma from DKPro output.

    ToDo:
        columns (List): List of DKPro columns that should be selected?
        Default values for parameters
        readCSV-function?
        Parameter `file` missing?!?
    """
    
    log.info("Accessing selected POS-tags ...")
    #pos_tags = ['ADJ', "V", "NN"]
    #columns = ['ParagraphId', 'TokenId', 'Lemma', 'CPOS', 'NamedEntity']
    df = pd.DataFrame()
    df = pd.read_csv(file, sep="\t", quoting=csv.QUOTE_NONE)
    df = df[columns]

    for p in pos_tags:
       df = df.loc[df["CPOS"] == p]
       yield df.loc[df["CPOS"] == p]["Lemma"]
    log.debug("POS-tags successfully accessed.")

def get_labels(files):
    """Gets document labels.
    
    Args:
        files (list[str]): List of file paths.

    Yields:
        Iterable: Document labels.
    """
    
    log.info("Creating document labels ...")
    labels = []
    for file in files:
        label = os.path.basename(file)
        yield label
    log.debug("Document labels successfully created.")

class Visualization:
    def __init__(self, lda_model, corpus, dictionary, doc_labels, interactive):
        """Loads Gensim output for further processing.

        The output folder should contain ``corpus.mm``, ``corpus.lda``, as well as
        ``corpus_doclabels.txt`` (for heatmap) or ``corpus.dict`` (for interactive
        visualization).

        Args:
            path (str): Path to output folder.
            interactive (bool, optional): True if interactive visualization,
                False if heatmap is desired. Defaults to False.

        Returns:
            If `interactive == False`: corpus, model, doc_labels.
            If `interactive == True`: corpus, model, dictionary.

        Raises:
            OSError: If directory or files not found.
            ValueError: If no matching values found.
            Unexpected error: Everything else.
        """
        try:
            log.info("Accessing corpus ...")
            self.corpus = MmCorpus(corpus)
            log.debug("Corpus successfully accessed.")

            log.info("Accessing model ...")
            self.model = LdaModel.load(lda_model)
            log.debug("Model successfully accessed.")

            if interactive == False:
                log.debug("`interactive` set to False.")
                log.info("Accessing doc_labels ...")
                self.doc_labels = doc_labels
                log.debug("doc_labels successfully accessed.")
                with open(self.doc_labels, 'r', encoding='utf-8') as f:
                    self.doc_labels = [line for line in f.read().split()]
                    log.debug("Accessed %s doc_labels.", len(doc_labels))
                log.info("Corpus, model, doc_labels for heatmap visualization successfully created.")

            elif interactive == True:
                log.debug("`interactive` set to True.")
                log.info("Accessing dictionary ...")
                self.dictionary = Dictionary.load(dictionary)
                log.debug("Dictionary successfully accessed.")
                log.info("Corpus, model, dictionary for interactive visualization successfully created.")

        except OSError as err:
            log.error("OS error: {0}".format(err))
        except ValueError:
            log.error("Value error: No matching value found.")
        except:
            import sys
            log.error("Unexpected error:", sys.exc_info()[0])
            sys.exit(1)
            raise

    def make_heatmap(self):
        """Generates heatmap from LDA model.

        The ingested data (e.g. with `load_gensim_output()`) has to be transmitted
        as parameters.

        Args:
            corpus: Corpus created by Gensim, e.g. corpus.mm.
            model: LDA model created by Gensim, e.g. corpus.lda.
            doc_labels (list[str]): List of document labels, e.g. corpus_doclabels.txt.

        Returns:
            Matplotlib heatmap figure.

        ToDo:
            create figure dynamically?
            -> http://stackoverflow.com/questions/23058560/plotting-dynamic-data-using-matplotlib
        """
        no_of_topics = self.model.num_topics
        no_of_docs = len(self.doc_labels)
        doc_topic = np.zeros((no_of_docs, no_of_topics))

        log.info("Loading topic distribution from model ...")
        for doc, i in zip(self.corpus, range(no_of_docs)):
            topic_dist = self.model.__getitem__(doc)
        log.debug("Topic distribution successfully loaded from model.")

        log.info("Saving topic probability ...")
        for topic in topic_dist: # topic_dist is a list of tuples (topic_id, topic_prob)
            doc_topic[i][topic[0]] = topic[1]
        log.debug("Topic probability successfully saved.")

        log.info("Loading plot labels ...")
        topic_labels = []
        for i in range(no_of_topics):
            topic_terms = [x[0] for x in self.model.show_topic(i, topn=3)] # show_topic() returns tuples (word_prob, word)
            topic_labels.append(" ".join(topic_terms))
        log.debug("Saved %s topic_labels.", len(topic_labels))

        log.info("Creating heatmap figure ...")
        if no_of_docs > 20 or no_of_topics > 20:
            plt.figure(figsize=(20,20))    # if many items, enlarge figure
        plt.pcolor(doc_topic, norm=None, cmap='Reds')
        plt.yticks(np.arange(doc_topic.shape[0])+1.0, doc_labels)
        plt.xticks(np.arange(doc_topic.shape[1])+0.5, topic_labels, rotation='90')
        plt.gca().invert_yaxis()
        plt.colorbar(cmap='Reds')
        heatmap = plt.tight_layout()
        log.debug("Heatmap figure successfully created.")
        return heatmap

    def save_heatmap(self, path):
        """Saves Matplotlib heatmap figure.

        The created visualization (e.g. with `make_heatmap()`) has to be
        transmitted as parameter.

        Args:
            heatmap: plt.figure created by ``matplotlib.pyplot``.
            path(str): Path to output folder. Defaults to global variable `path`.

        Returns:
            ~/out/corpus_heatmap.png
        """
        log.info("Saving heatmap figure...")
        plt.savefig(os.path.join(path, 'corpus_heatmap.png'), dpi= 200)
        log.debug("Heatmap figure successfully saved as corpus_heatmap.png")

    def make_interactive(self):
        """Generates interactive visualization from LDA model.

        The ingested data (e.g. with `load_gensim_output()`) has to be transmitted
        as parameters.

        Args:
            corpus: Corpus created by Gensim, e.g. corpus.mm.
            model: LDA model created by Gensim, e.g. corpus.lda.
            dictionary(dict): Dictionary created by Gensim, e.g. corpus.dict.

        Returns:
            pyLDAvis visualization.
        """
        log.info("Loading model, corpus, dictionary ...")
        vis = pyLDAvis.gensim.prepare(self.model, self.corpus, self.dictionary)
        log.debug("Interactive visualization successfully created.")
        return vis


    def save_interactive(self, path):
        """Saves interactive visualization.

        The created visualization (e.g. with `make_interactive()`) has to be
        transmitted as parameter.

        Args:
            vis: Interactive visualization created by pyLDAvis.
            path(str): Path to output folder. Defaults to global variable `path`.

        Returns:
            ~/out/corpus_interactive.html
            ~/out/corpus_interactive.json
        """
        log.info("Saving interactive visualization ...")
        pyLDAvis.save_html(vis, os.path.join(path, 'corpus_interactive.html'))
        pyLDAvis.save_json(vis, os.path.join(path, 'corpus_interactive.json'))
        pyLDAvis.prepared_data_to_html(vis)
        log.info("Interactive visualization successfully saved as corpus_interactive.html and corpus_interactive.json.")
