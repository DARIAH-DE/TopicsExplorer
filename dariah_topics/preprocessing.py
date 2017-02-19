#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Preprocessing.

This module contains functions for various preprocessing steps provided by `DARIAH-DE`_.

.. _DARIAH-DE:
    https://de.dariah.eu
    https://github.com/DARIAH-DE
"""

__author__ = "DARIAH-DE"
__authors__ = "Steffen Pielstroem, Philip Duerholt, Sina Bock, Severin Simmler"
__email__ = "pielstroem@biozentrum.uni-wuerzburg.de"
__version__ = "0.1"
__date__ = "2017-01-20"


import glob
import os
from collections import Counter, defaultdict
import csv
import logging
from lxml import etree
import numpy as np
import pandas as pd
import regex
from itertools import chain


log = logging.getLogger('preprocessing')
log.addHandler(logging.NullHandler())
logging.basicConfig(level = logging.WARNING,
                    format = '%(levelname)s %(name)s: %(message)s')

regular_expression = r'\p{Letter}+\p{Punctuation}?\p{Letter}+'

def create_document_list(path, ext='txt'):
    """Creates a list of files with their full path.

    Args:
        path (str): Path to folder, e.g. '/tmp/corpus'.
        ext (str): File extension, e.g. 'csv'. Defaults to 'txt'.

    Returns:
        list[str]: List of files with full path.
    """
    log.info("Creating document list from %s files ...", ext.upper())
    pattern = os.path.join(path, "*." + ext)
    doclist = glob.glob(pattern)
    log.debug("%s entries in document list.", len(doclist))
    if not doclist:
        raise FileNotFoundError("The pattern %s does not match any files." % pattern)
    return doclist

def read_from_tei(doclist):
    ns = dict(tei="http://www.tei-c.org/ns/1.0")
    for file in doclist:
        tree = etree.parse(file)
        text_el = tree.xpath('//tei:text', namespaces=ns)[0]
        yield "".join(text_el.xpath('.//text()'))

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
                log.debug("Accessing TXT document %s ...", file)
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

def get_labels(doclist):
    """Creates a list of document labels.

    Note:
        Use `create_document_list()` to create `doclist`.

    Args:
        doclist (list[str]): List of file paths.

    Yields:
        Iterable: Document labels.

    ToDo:
        Replace this function with function from Toolbox
    """
    log.info("Creating document labels ...")
    for doc in doclist:
        #label = os.path.basename(doc)
        label = doc
        yield label
    log.debug("Document labels available")

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

def split_paragraphs(doc_txt, sep=regex.compile('\n')):
    """
    Split the given document by paragraphs.

    Args:
        doc_txt (str): Document text
        sep (regex.Regex): separator indicating a paragraph

    Returns:
        List of paragraphs
    """
    if not hasattr(sep, 'match'):
        sep = regex.compile(sep)
    return sep.split(doc_txt)

def segment_fuzzy(document, segment_size=5000, tolerance=0.05):
    """
    Segments a document, tolerating existing chunks (like paragraphs).

    Description:
        Consider you have a document. You wish to split the document into
        segments of about 1000 tokens, but you prefer to keep paragraphs together
        if this does not increase or decrease the token size by more than 5%.

    Args:
        document: The document to process. This is an Iterable of chunks, each
            of which is an iterable of tokens.
        segment_size (int): The target length of each segment in tokens.
        tolerance (Number): How much may the actual segment size differ from
            the segment_size? If 0 < tolerance < 1, this is interpreted as a
            fraction of the segment_size, otherwise it is interpreted as an
            absolute number. If tolerance < 0, chunks are never split apart.

    Yields:
        Segments. Each segment is a list of chunks, each chunk is a list of
        tokens.
    """
    if tolerance > 0 and tolerance < 1:
        tolerance = round(segment_size * tolerance)

    current_segment = []
    current_size = 0
    carry = None
    doc_iter = iter(document)

    try:
        while True:
            chunk = list(carry if carry else next(doc_iter))
            carry = None
            current_segment.append(chunk)
            current_size += len(chunk)

            if current_size >= segment_size:
                too_long = current_size - segment_size
                too_short = segment_size - (current_size - len(chunk))

                if tolerance >= 0 and min(too_long, too_short) > tolerance:
                    chunk_part0 = chunk[:-too_long]
                    carry = chunk[-too_long:]
                    current_segment[-1] = chunk_part0
                elif too_long >= too_short:
                    carry = current_segment.pop()
                yield current_segment
                current_segment = []
                current_size = 0
    except StopIteration:
        pass

    # handle leftovers
    if current_segment:
        yield current_segment


def segment(document, segment_size=1000, tolerance=0, chunker=None,
            tokenizer=None, flatten_chunks=False, materialize=False):
    """
    Segments a document into segments of about `segment_size` tokens, respecting
    existing chunks.

    This is a convenience wrapper around segment_fuzzy.

    Args:
        segment_size (int): The target size of each segment, in tokens.
        tolerance (Number): see `segment_fuzzy`
        chunker (callable): a one-argument function that cuts the document into
            chunks. If this is present, it is called on the given document.
        tokenizer (callable): a one-argument function that tokenizes each chunk.
        flatten_chunks (bool): if True, undo the effect of the chunker by
            chaining the chunks in each segment, thus each segment consists of
            tokens. This can also be a one-argument function in order to
            customize the un-chunking.
    """
    if chunker is not None:
        document = chunker(document)
    if tokenizer is not None:
        document = map(tokenizer, document)

    segments = segment_fuzzy(document, segment_size, tolerance)

    if flatten_chunks:
        if not callable(flatten_chunks):
            def flatten_chunks(segment):
                return list(chain.from_iterable(segment))
        segments = map(flatten_chunks, segments)
    if materialize:
        segments = list(segments)

    return segments



def tokenize(doc_txt, expression=regular_expression, lower=True, simple=False):
    """Tokenizes with Unicode Regular Expressions.

    Args:
        doc_txt (str): Document as string.
        expression (str): Regular expression to find tokens.
        lower (boolean): If True, lowers all words. Defaults to True.
        simple (boolean): Uses simple regular expression (r'\w+'). Defaults to False.
            If set to True, argument `expression` will be ignored.

    Yields:
        Tokens

    Example:
        >>> list(tokenize("This is one example text."))
        ['this', 'is', 'one', 'example', 'text']
    """
    if lower:
        doc_txt = doc_txt.lower()
    if simple:
        pattern = regex.compile(r'\w+')
    else:
        pattern = regex.compile(expression)
    doc_txt = regex.sub("\.", "", doc_txt)
    doc_txt = regex.sub("‒", " ", doc_txt)
    doc_txt = regex.sub("–", " ", doc_txt)
    doc_txt = regex.sub("—", " ", doc_txt)
    doc_txt = regex.sub("―", " ", doc_txt)
    tokens = pattern.finditer(doc_txt)
    for match in tokens:
        yield match.group()

def filter_POS_tags(doc_csv, pos_tags=['ADJ', 'V', 'NN']):
    """Gets lemmas by selected POS-tags from DKPro-Wrapper output.

    Note:
        Use `read_from_csv()` to create `doc_csv`.

    Args:
        doclist (list[str]): List of DKPro output files that should be selected.
        pos_tags (list[str]): List of DKPro POS-tags that should be selected.
            Defaults to '['ADJ', 'V', 'NN']'.

    Yields:
        Lemma.'''
    """
    df = next(doc_csv)
    log.info("Accessing %s lemmas ...", pos_tags)
    for p in pos_tags:
        df = df.loc[df['CPOS'] == p]
        lemma = df.loc[df['CPOS'] == p]['Lemma']
        yield lemma


def find_stopwords(sparse_bow, id_types, mfw = 200):
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
    type2id = {value : key for key, value in id_types.items()}
    sparse_bow_collapsed = sparse_bow.groupby(sparse_bow.index.get_level_values('token_id')).sum()
    sparse_bow_stopwords = sparse_bow_collapsed[0].nlargest(mfw)
    stopwords = [type2id[key] for key in sparse_bow_stopwords.index.get_level_values('token_id')]
    log.debug("%s stopwords found.", len(stopwords))
    return stopwords

def find_hapax(sparse_bow, id_types):
    """Creates list with hapax legommena.

    Note:
        Use `create_TF_matrix` to create `docterm_matrix`.

    Args:
        docterm_matrix (DataFrame): DataFrame with term and term frequency by document.

    Returns:
        Hapax legomena in Series.
    """
    log.info("Find hapax legomena ...")

    type2id = {value : key for key, value in id_types.items()}
    sparse_bow_collapsed = sparse_bow.groupby(sparse_bow.index.get_level_values('token_id')).sum()
    sparse_bow_hapax = sparse_bow_collapsed.loc[sparse_bow_collapsed[0] == 1]
    hapax = [type2id[key] for key in sparse_bow_hapax.index.get_level_values('token_id')]

    log.debug("%s hapax legomena found.", len(hapax))
    return hapax

def remove_features(mm, id_types, features):
    """Removes features.

    Note:
        Use `find_stopwords()` or `find_hapax()` to create `features`.

    Args:
        docterm_matrix (DataFrame): DataFrame with term and term frequency by document.
        features (set): Set with features to remove.
        (not included) features (str): Text as iterable. Use `read_from_txt()` to create iterable.

    Returns:
        Clean corpus.

    ToDo:
        Adapt function to work with mm-corpus format.
    """
    log.info("Removing features ...")

    if type(features) == set:

        stoplist_applied = [word for word in set(id_types.keys()) if word in features]

        clean_term_frequency = mm.drop([id_types[word] for word in stoplist_applied], level="token_id")

    else:

        try:

            features = set(features)

        except:

            log.debug("features must be set or convertible to set")

        stoplist_applied = [word for word in set(id_types.keys()) if word in features]

        clean_term_frequency = mm.drop([id_types[word] for word in stoplist_applied], level="token_id")

    total = len(features)

    log.debug("%s features removed.", total)
    return clean_term_frequency



def create_dictionaries(doc_labels, doc_tokens):
    """create_large_TF_matrix

    Note:


    Args:


    Returns:

    ToDo:
    """

    typeset = set()

    temp_tokens = doc_tokens

    temp_labels = doc_labels

    doc_dictionary = defaultdict(list)

    for label, doc in zip(doc_labels, doc_tokens):

        tempdoc = list(doc)

        tempset = set([token for token in tempdoc])

        typeset.update(tempset)

    type_dictionary = { id_num : token for id_num, token in enumerate(typeset, 1) }
    type_dictionary = { v : k for k, v in enumerate(typeset, 1) }
    doc_ids = { doc : id_num for id_num, doc in enumerate(doc_labels, 1) }


    return type_dictionary, doc_ids

def _create_large_counter(doc_labels, doc_tokens, type_dictionary):
    """create_large_TF_matrix

    Note:


    Args:


    Returns:

    ToDo:
    """

    largecounter = defaultdict(dict)

    for doc, tokens in zip(doc_labels, doc_tokens):

        largecounter[doc] = Counter([type_dictionary[token] for token in tokens])

    return largecounter

def _create_sparse_index(largecounter):
    """create_large_TF_matrix

    Note:


    Args:


    Returns:

    ToDo:
    """

    #tuples = list(zip(largecounter.keys(), largecounter.values().keys()))
    tuples = []

    for key in range(1, len(largecounter)+1):

        for value in largecounter[key]:

            tuples.append((key, value))

    sparse_index = pd.MultiIndex.from_tuples(tuples, names = ["doc_id", "token_id"])

    #sparse_df = pd.DataFrame(largecounter.values(), index= largecounter.keys(), columns = ["token_id", "count"])

    return sparse_index


def create_mm(doc_labels, doc_tokens, type_dictionary, doc_ids):
    """create_large_TF_matrix

    Note:


    Args:


    Returns:

    ToDo:
    """

    temp_counter = _create_large_counter(doc_labels, doc_tokens, type_dictionary)

    largecounter = {doc_ids[key] : value for key, value in temp_counter.items()}

    sparse_index = _create_sparse_index(largecounter)

    sparse_df_filled = pd.DataFrame(np.zeros((len(sparse_index), 1), dtype = int), index = sparse_index)


    index_iterator = sparse_index.groupby(sparse_index.get_level_values('doc_id'))

    for doc_id in range(1, len(sparse_index.levels[0])+1):
        for token_id in [val[1] for val in index_iterator[doc_id]]:

            sparse_df_filled.set_value((doc_id, token_id), 0, int(largecounter[doc_id][token_id]))

    return sparse_df_filled

def save_bow_mm(sparse_bow, output_path):
    """Save bag-of-word model as market matrix

    Note:


    Args:


    Returns:

    ToDo:
    """
    num_docs = max(sparse_bow.index.get_level_values("doc_id"))
    num_types = max(sparse_bow.index.get_level_values("token_id"))
    sum_counts = sum(sparse_bow[0])

    header_string = str(num_docs) + " " + str(num_types) + " " + str(sum_counts) + "\n"

    with open('.'.join([output_path, 'mm']), 'w', encoding = "utf-8") as f:
        pass

    with open('.'.join([output_path, 'mm']), 'a', encoding = "utf-8") as f:
        f.write("%%MatrixMarket matrix coordinate real general\n")
        f.write(header_string)
        sparse_bow.to_csv( f, sep = ' ', header = None)
