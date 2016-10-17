#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Topic Modeling and LDA visualization.

This module provivdes various `Gensim`_ functions for topic modeling and LDA
visualization.

.. _Gensim:
    https://radimrehurek.com/gensim/index.html
.. _DARIAH-DE:
    https://de.dariah.eu
    https://github.com/DARIAH-DE
"""

__author__ = "DARIAH-DE"
__authors__ = "Stefan Pernes, Steffen Pielstroem, Philip Duerholt, Sina Bock, Severin Simmler"
__email__ = "stefan.pernes@uni-wuerzburg.de, pielstroem@biozentrum.uni-wuerzburg.de"
__version__ = "0.2"
__date__ = "2016-10-16"

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

def create_document_list(path):
    """Creates a list of files with their full path.

    Args:
        path (str): Path to folder, e.g. "/tmp/corpus".

    Returns:
        list[str]: List of files with full path.

    Author:
        DARIAH-DE
    """
    doclist = glob.glob(path + "/*")
    return doclist


class ReadFromTXT:
    """Opens files using a list of paths.

    """

    def __init__(self, doclist):
        """
        Note:
            Use `create_document_list()` to create instance attributes.
        """

        self.doclist = doclist

    def __iter__(self):
        """Yields document slizes with length words.

        Args:
            doclist (:obj:`list[str]`): List of all documents in the corpus.

        Todo:
            Seperate metadata (author, header)?
        """
        for file in self.doclist:
            with open(file, 'r', encoding = 'utf-8') as f:
                yield f.read()

class Segmenter:
    """Segments documents.
    """
    def __init__(self, doc, length):
        """
        Args:
            doc (str): Strings.
            length (int):
        """

        self.doc = doc
        self.length = length

    def __iter__(self):

        """Yields document slizes with length words.

        Args:
            doc (iterable): An iterable of tokens that is to be segmented.
            length (int): Target size of segments.

        Todo:
            Implement fuzzy option to consider paragraph breaks.
        """

        doc = self.doc.split()
        for i, word in enumerate(doc):
            if i % self.length == 0:
                yield doc[i : i + self.length]




#files = sorted(os.listdir(path=path)

class FilterPOS(object):

    """Get selected POS-tags from DKPRO-wrapper output

    Args:
        path (String): Path to DKPro-Wrapper output folder
        pos_tags (List): List of DKPro pos_tags that should be selected

    ToDo:
        columns (List): List of DKPro columns that should be selected?
        default values for parameters
        readCSV-function?

    """

    def __init__(self, path, pos, files):

        self.path = path
        self.files = files
        self.pos_tags = pos
        #self.pos_tags = ['ADJ', "V", "NN"]
        self.columns = ['ParagraphId', 'TokenId', 'Lemma', 'CPOS', 'NamedEntity']
        self.doc = pd.DataFrame()
        self.labels = []




    def get_labels(self):

        """
        Get document labels

        """

        for self.file in self.files:
            if not self.file.startswith("."):
                filepath = os.path.join(self.path, self.file)

                label = os.path.basename(self.file)

                df = pd.read_csv(filepath, sep="\t", quoting=csv.QUOTE_NONE)
                df = df[self.columns]

                for p in pos_tags:
                    self.doc = self.doc.append(df.loc[df["CPOS"] == p])

                yield label




    def get_lemma(self):

        """
        Get lemma from DKPro-Wrapper output

        """
        for self.file in self.files:
            if not self.file.startswith("."):
                filepath = os.path.join(self.path, self.file)

                label = os.path.basename(self.file)

                df = pd.read_csv(filepath, sep="\t", quoting=csv.QUOTE_NONE)
                df = df[self.columns]

                for p in pos_tags:
                    yield df.loc[df["CPOS"] == p]["Lemma"]





class Visualization():


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

        Author:
            DARIAH-DE
        """
        try:
            log.info("Accessing corpus ...")
            corpus = MmCorpus(self.corpus)

            log.info("Accessing model ...")
            model = LdaModel.load(lda_model)

            if interactive == False:
                log.debug("`interactive` set to False.")
                log.info("Accessing doc_labels ...")
                with open(doc_labels, 'r', encoding='utf-8') as f:
                    doc_labels = [line for line in f.read().split()]
                    log.debug("Saved %s doc_labels.", len(doc_labels))
                log.info("Successfully created corpus, model, doc_labels for heatmap visualization.")
                return {'corpus':corpus, 'model':model ,'doc_labels':doc_labels }

            else:
                log.debug("`interactive` set to True.")
                log.info("Accessing dictionary ...")
                dictionary = Dictionary.load(dictionary)
                log.info("Successfully created corpus, model, dictionary for interactive visualization.")
                return {'corpus':corpus, 'model':model ,'dictionary':dictionary }

        except OSError as err:
            log.error("OS error: {0}".format(err))
        except ValueError:
            log.error("Value error: No matching value found.")
        except:
            import sys
            log.error("Unexpected error:", sys.exc_info()[0])
            sys.exit(1)
            raise
        self.__lda_model = lda_model
        self.__corpus = corpus
        self.__dictionary = dictionary
        self.__doc_labels = doc_labels


    def make_heatmap(corpus, model, doc_labels):
        """Generates heatmap from LDA model.

        The ingested data (e.g. with `load_gensim_output()`) has to be transmitted
        as parameters.

        Args:
            corpus: Corpus created by Gensim, e.g. corpus.mm.
            model: LDA model created by Gensim, e.g. corpus.lda.
            doc_labels(list[str]): List of document labels, e.g. corpus_doclabels.txt.

        Returns:
            Matplotlib heatmap figure.

        ToDo:
            create figure dynamically?
            -> http://stackoverflow.com/questions/23058560/plotting-dynamic-data-using-matplotlib
        """

        no_of_topics = model.num_topics
        no_of_docs = len(doc_labels)
        doc_topic = np.zeros((no_of_docs, no_of_topics))

        log.info("Loading topic distribution from model ...")
        for doc, i in zip(corpus, range(no_of_docs)):
            topic_dist = model.__getitem__(doc)

        log.info("Saving topic probability ...")
        for topic in topic_dist: # topic_dist is a list of tuples (topic_id, topic_prob)
            doc_topic[i][topic[0]] = topic[1]

        log.info("Loading plot labels ...")
        topic_labels = []
        for i in range(no_of_topics):
            topic_terms = [x[0] for x in model.show_topic(i, topn=3)] # show_topic() returns tuples (word_prob, word)
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
        log.info("Successfully created heatmap figure.")
        return heatmap

    def save_heatmap(heatmap, path):
        """Saves Matplotlib heatmap figure.

        The created visualization (e.g. with `make_heatmap()`) has to be
        transmitted as parameter.

        Args:
            heatmap: plt.figure created by ``matplotlib.pyplot``.
            path(str): Path to output folder. Defaults to global variable `path`.

        Returns:
            ~/out/corpus_heatmap.png
        """
        log.info("Saving heatmap ...")
        plt.savefig(os.path.join(path, 'corpus_heatmap.png'), dpi= 200)
        log.info("Successfully saved heatmap as corpus_heatmap.png")

    def make_interactive(corpus, model, dictionary):
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
        vis = pyLDAvis.gensim.prepare(model, corpus, dictionary)
        log.info("Successfully created interactive visualization.")
        return vis


    def save_interactive(vis, path):
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
        log.info("Successfully saved interactive visualization.")
