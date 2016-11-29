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
__version__ = "0.1"
__date__ = "2016-11-24"

from collections import Counter
import csv
from gensim.corpora import MmCorpus, Dictionary
from gensim.models import LdaModel
import glob
from itertools import dropwhile
import logging
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pyLDAvis.gensim
import re
import sys
import regex as re

log = logging.getLogger('collection')
log.addHandler(logging.NullHandler())
logging.basicConfig(level = logging.DEBUG,
                    format = '%(asctime)s %(levelname)s %(name)s: %(message)s',
                    datefmt = '%d-%b-%Y %H:%M:%S')

def create_document_list(path, ext='txt'):
    """Creates a list of files with their full path.

    Args:
        path (str): Path to folder, e.g. '/tmp/corpus'.
        ext (str): File extension, e.g. 'csv'. Defaults to 'txt'.

    Returns:
        list[str]: List of files with full path.
    """
    log.info("Creating document list from %s files ...", ext.upper())
    doclist = glob.glob(path + "/*." + ext)
    log.debug("%s entries in document list.", len(doclist))
    return doclist

def get_labels(doclist):
    """Creates a list of document labels.

    Note:
        Use `create_document_list()` to create `doclist`.

    Args:
        doclist (list[str]): List of file paths.

    Yields:
        Iterable: Document labels.
    """
    log.info("Creating document labels ...")
    for doc in doclist:
        label = os.path.basename(doc)
        yield label
    log.debug("Document labels available.")

def read_from_txt(doclist):
    """Opens files using a list of paths or one single path.

    Note:
        Use `create_document_list()` to create `doclist`.

    Args:
        doclist (list[str]): List of all documents in the corpus.
        doclist (str): Path to TXT file.

    Yields:
        Iterable: Document.

    Todo:
        * Seperate metadata (author, header)?
    """
    if type(doclist) == str:
        with open(doclist, 'r', encoding='utf-8') as f:
            log.debug("Accessing TXT document ...")
            doc = f.read()
            yield doc
    else:
        for file in doclist:
            with open(file, 'r', encoding='utf-8') as f:
                log.debug("Accessing TXT document ...")
                doc_txt = f.read()
                yield doc_txt

def read_from_csv(doclist, columns=['ParagraphId', 'TokenId', 'Lemma', 'CPOS', 'NamedEntity']):
    """Opens files using a list of paths.

    Note:
        Use `create_document_list()` to create `doclist`.

    Args:
        doclist (list[str]): List of all documents in the corpus.
        columns (list[str]): List of CSV column names.
            Defaults to '['ParagraphId', 'TokenId', 'Lemma', 'CPOS', 'NamedEntity']'.

    Yields:
        Document.

    Todo:
        * Seperate metadata (author, header)?
    """
    for file in doclist:
        df = pd.read_csv(file, sep="\t", quoting=csv.QUOTE_NONE)
        log.info("Accessing CSV documents ...")
        doc_csv = df[columns]
        yield doc_csv

def segmenter(doc_txt, length=1000):
    """Segments documents.

    Note:
        Use `read_from_txt()` to create `doc_txt`.

    Args:
        doc_txt (str): Document as iterable.
        length (int): Target size of segments. Defaults to '1000'.

    Yields:
        Document slizes with length words.

    Todo:
        * Implement fuzzy option to consider paragraph breaks.
    """
    doc = next(doc_txt)
    log.info("Segmenting document ...")
    for i, word in enumerate(doc):
        if i % length == 0:
            log.debug("Segment has a length of %s characters.", length)
            segment = doc[i : i + length]
            yield segment

def tokenizer(doc_txt):
    """Tokenizes text documents.
    Note:
        Use `read_from_txt()` to create `doc_txt`.

    Args:
        doc_txt (str): Document as iterable.

    Yields:
        List of Strings

    Todo:
        * Tokenize with regex and not with split()
    """

    for doc in doc_txt:
        yield re.findall("[A-Z][a-z][0-9]+(?=[A-Z])|[\w]+",doc)
            
def filter_POS_tags(doc_csv, pos_tags=['ADJ', 'V', 'NN']):
    """Gets lemmas by selected POS-tags from DKPro-Wrapper output.

    Note:
        Use `read_from_csv()` to create `doc_csv`.

    Args:
        doclist (list[str]): List of DKPro output files that should be selected.
        pos_tags (list[str]): List of DKPro POS-tags that should be selected.
            Defaults to '['ADJ', 'V', 'NN']'.

    Yields:
        Lemma.
    """
    df = next(doc_csv)
    log.info("Accessing %s lemmas ...", pos_tags)
    for p in pos_tags:
        df = df.loc[df['CPOS'] == p]
        lemma = df.loc[df['CPOS'] == p]['Lemma']
        yield lemma

#
# Next 3 operations have to be changed because of TF-Matrix
#
    
def find_stopwords(docterm_matrix, mfw):
    """Creates a stopword list.

    Note:
        Use `create_TF_matrix` to create `docterm_matrix`.

    Args:
        docterm_matrix (DataFrame): DataFrame with term and term frequency by document.
        mfw (int): Target size of most frequent words to be considered.

    Returns:
        Most frequent words in DataFrame.
    """
    log.info("Finding stopwords ...")
    stopwords = set(docterm_matrix.T.max().sort_values(ascending = False)[:mfw].index)
    log.debug("%s stopwords found.", len(stopwords))
    return stopwords

def find_hapax(term_frequency):
    """Creates list with hapax legommena.

    Note:
        Use `calculate_term_frequency()` to create `term_frequency`.

    Args:
        term_frequency (Series): Series with term and term frequency.

    Returns:
        Hapax legomena in Series.
    """
    log.info("Find hapax legomena ...")
    hapax = term_frequency.loc[term_frequency == 1]
    log.debug("%s hapax legomena found.", len(hapax))
    return hapax

def remove_features(term_frequency, features):
    """Removes features.

    Note:
        Use `find_stopwords()` or `find_hapax()` to create `features`.

    Args:
        term_frequency (Series): Series with term and term frequency.
        features (Series): Series with features to remove.
        features (str): Text as iterable. Use `read_from_txt()` to create iterable.

    Returns:
        Clean corpus.
    """
    log.info("Removing features ...")
    total = 0
    if type(features) == pd.Series:
        for term in features.index:
            if term in term_frequency:
                del term_frequency[term]
                total += 1
    elif type(features) != pd.Series:
        features = next(features)
        stoplist = [word for word in features.split()] # replace with final tokenize function
        for term in stoplist:
            if term in term_frequency:
                del term_frequency[term]
                total += 1
    clean_term_frequency = term_frequency
    log.debug("%s features removed.", total)
    return clean_term_frequency


def create_TF_matrix(doc_tokens, doc_labels):
    """Creates Document to Term Frequency Matrix.

    Note:
        Use `tokenizer()` to create `doc_tokens`.

    Args:
       doc_tokens (Generator): Generator with Lists of String.
       doc_labels: List of String.

    Returns:
        Term-Doc-Matrix as pandas Dataframe

    To do:
        * TBA
    """

    termdocmatrix = pd.DataFrame()

    for label, doc in zip(doc_labels, doc_tokens):
        try:
            termdocmatrix[label] = pd.Series(Counter(doc))

        except:
            log.debug("Error while trying to count tokens in %s .", label)
            pass
    
    log.info("Term Document Matrix successfully created.")
            
    return termdocmatrix.fillna(0)

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
            log.debug("Corpus available.")

            log.info("Accessing model ...")
            self.model = LdaModel.load(lda_model)
            log.debug("Model available.")

            if interactive == False:
                log.debug(":param: interactive == False.")
                log.info("Accessing doc_labels ...")
                self.doc_labels = doc_labels
                log.debug("doc_labels accessed.")
                with open(self.doc_labels, 'r', encoding='utf-8') as f:
                    self.doc_labels = [line for line in f.read().split()]
                    log.debug("%s doc_labels available.", len(doc_labels))
                log.debug("Corpus, model and doc_labels available.")

            elif interactive == True:
                log.debug(":param: interactive == True.")
                log.info("Accessing dictionary ...")
                self.dictionary = Dictionary.load(dictionary)
                log.debug("Dictionary available.")
                log.debug("Corpus, model and dictionary available.")

        except OSError as err:
            log.error("OS error: {0}".format(err))
            raise
        except ValueError:
            log.error("Value error: No matching value found.")
            raise
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
            * add colorbar
            * create figure dynamically?
                http://stackoverflow.com/questions/23058560/plotting-dynamic-data-using-matplotlib
        """
        no_of_topics = self.model.num_topics
        no_of_docs = len(self.doc_labels)
        doc_topic = np.zeros((no_of_docs, no_of_topics))

        log.info("Accessing topic distribution ...")
        for doc, i in zip(self.corpus, range(no_of_docs)):
            topic_dist = self.model.__getitem__(doc)
        log.debug("Topic distribution available.")

        log.info("Accessing topic probability ...")
        for topic in topic_dist: # topic_dist is a list of tuples (topic_id, topic_prob)
            doc_topic[i][topic[0]] = topic[1]
        log.debug("Topic probability available.")

        log.info("Accessing plot labels ...")
        topic_labels = []
        for i in range(no_of_topics):
            topic_terms = [x[0] for x in self.model.show_topic(i, topn=3)] # show_topic() returns tuples (word_prob, word)
            topic_labels.append(" ".join(topic_terms))
        log.debug("%s plot labels available.", len(topic_labels))

        log.info("Creating heatmap figure ...")
        if no_of_docs > 20 or no_of_topics > 20:
            fig = plt.figure(figsize=(20,20))    # if many items, enlarge figure
        else:
            fig = plt.figure()
            ax = fig.add_subplot(1,1,1)
            ax.pcolor(doc_topic, norm=None, cmap='Reds')
            ax.set_yticks(np.arange(doc_topic.shape[0])+1.0)
            ax.set_yticklabels(self.doc_labels)
            ax.set_xticks(np.arange(doc_topic.shape[1])+0.5)
            ax.set_xticklabels(topic_labels, rotation='90')
            ax.invert_yaxis()
            fig.tight_layout()
            self.heatmap_vis = fig
            log.debug("Heatmap figure available.")


    def save_heatmap(self, path, filename='heatmap', ext='png', dpi=200):
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
        try:
            self.heatmap_vis.savefig(os.path.join(path, filename + '.' + ext), dpi=dpi)
            log.debug("Heatmap figure available at %s/%s.%s", path, filename, ext)
        except AttributeError:
            log.error("Run make_heatmap() before save_heatmp()")
            raise

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
        log.info("Accessing model, corpus and dictionary ...")
        self.interactive_vis = pyLDAvis.gensim.prepare(self.model, self.corpus, self.dictionary)
        log.debug("Interactive visualization available.")


    def save_interactive(self, path, filename='corpus_interactive'):
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
        try:
            log.info("Saving interactive visualization ...")
            pyLDAvis.save_html(self.interactive_vis, os.path.join(path, 'corpus_interactive.html'))
            pyLDAvis.save_json(self.interactive_vis, os.path.join(path, 'corpus_interactive.json'))
            pyLDAvis.prepared_data_to_html(self.interactive_vis)
            log.debug("Interactive visualization available at %s/corpus_interactive.html and %s/corpus_interactive.json", path, path)
        except AttributeError:
            log.error("Running make_interactive() before save_interactive() ...")
            raise
