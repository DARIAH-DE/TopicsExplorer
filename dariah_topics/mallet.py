#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""MALLET wrapper for Python.

This module contains various `MALLET`_ related functions for Topic Modeling
provided by `DARIAH-DE`_.

.. _MALLET:
    http://mallet.cs.umass.edu/
.. _DARIAH-DE:
    https://de.dariah.eu
    https://github.com/DARIAH-DE
"""

__author__ = "DARIAH-DE"
__authors__ = "Steffen Pielstroem, Sina Bock, Severin Simmler"
__email__ = "pielstroem@biozentrum.uni-wuerzburg.de"
__date__ = "2017-03-28"

import itertools
import logging
import numpy as np
import operator
import os
import pandas as pd
from platform import system
from subprocess import Popen, PIPE

log = logging.getLogger('mallet')
log.addHandler(logging.NullHandler())
logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s %(name)s: %(message)s')


def create_mallet_binary(outfile='binary.mallet', outfolder='mallet_output',
                         path_to_file=False, path_to_corpus=os.path.join(os.path.abspath('.'), 'corpus_txt'),
                         path_to_mallet="mallet", keep_sequence=False, preserve_case=False,
                         remove_stopwords=True, stoplist=None, token_regex=False):
    """Creates a MALLET binary file.

    Args:
        outfile (str): Name of the MALLET file that will be generated. Defaults to 'binary.mallet'.
        outfolder (str): Folder for output.
        path_to_file (str): Absolute path to text file, e.g. '/home/workspace/testfile.txt'.
        path_to_corpus (str): Absolute path to corpus folder, e.g. '/home/workspace/corpus_txt'.
        path_to_mallet (str): Path to MALLET. Defaults to 'mallet'.
                              If MALLET is not properly installed use absolute path, e.g. '/home/workspace/mallet/bin/mallet'.
        keep_sequence (bool): Preserves the document as a sequence of word features,
                              rather than a vector of word feature counts. Use this
                              option for sequence labeling tasks. MALLET also requires
                              feature sequences rather than feature vectors. Defaults
                              to False.
        preserve_case (bool): Converts all word features to lowercase. Defaults to False.
        remove_stopwords (bool): Ignores a standard list of very common tokens. Defaults to True.
        stoplist (str): Absolute path to plain text stopword list. Defaults to None.
        token_regex (bool): Divides documents into tokens using a regular expression.
                            Defaults to False.

    Returns:
        String. Absolute path to created MALLET binary file.
    """
    if system() == 'Windows':
        shell = True
    else:
        shell = False

    path_to_binary = os.path.join(outfolder, outfile)

    if not os.path.exists(outfolder):
        log.info("Creating output folder ...")
        os.makedirs(outfolder)

    param = [path_to_mallet]
    if not path_to_file:
        param.append('import-dir')
        param.append('--input')
        param.append(path_to_corpus)
    else:
        param.append('import-file')
        param.append('--input')
        param.append(path_to_file)
    if preserve_case:
        param.append('--preserve-case')
    if remove_stopwords:
        param.append('--remove-stopwords')
        if stoplist is not None:
            param.append('--stoplist-file')
            param.append(stoplist)
    if token_regex:
        param.append('--token-regex')
        param.append(token_regex)

    param.append('--output')
    param.append(os.path.join(path_to_binary))
    param.append('--keep-sequence')

    try:
        log.info("Accessing MALLET with %s ...", param)
        p = Popen(param, stdout=PIPE, stderr=PIPE, shell=shell)
        out = p.communicate()[0].decode('utf-8')
        log.debug(out)
    except KeyboardInterrupt:
        p.terminate()
        log.error(out)
    return path_to_binary


def create_mallet_model(path_to_binary, outfolder, path_to_mallet='mallet', num_topics=False,
                        num_top_words=False, num_iterations=False, num_threads=False,
                        num_icm_iterations=False, no_inference=False, random_seed=False,
                        optimize_interval=False, optimize_burn_in=False, use_symmetric_alpha=False,
                        alpha=False, beta=False, output_topic_keys=True, topic_word_weights_file=False,
                        word_topic_counts_file=False, diagnostics_file=False, xml_topic_report=False,
                        xml_topic_phrase_report=False, output_topic_docs=False, num_top_docs=False,
                        output_doc_topics=True, doc_topics_threshold=False, output_model=False,
                        output_state=True, doc_topics_max=False):
    """Creates MALLET model.

    Note: Use `create_mallet_binary()` to create `path_to_binary`.

    Args:
        path_to_binary (str): Path to MALLET binary.
        outfolder (str): Folder for MALLET output.
        path_to_mallet (str): Path to MALLET. Defaults to 'mallet'.
                              If MALLET is not properly installed use absolute path, e.g. '/home/workspace/mallet/bin/mallet'.
        num_topics (int): Number of topics. Defaults to False.
        num_interations (int): Number of iterations. Defaults to False.
        num_top_words (int): Number of keywords for each topic. Defaults to False.
        num_threads (int): Number of threads for parallel training.  Defaults to False.
        num_icm_iterations (int): Number of iterations of iterated conditional modes (topic maximization).  Defaults to False..
        no_inference (bool): Load a saved model and create a report. Equivalent to `num_iterations = 0`. Defaults to False.
        random_seed (int): Random seed for the Gibbs sampler.  Defaults to False.
        optimize_interval (int): Number of iterations between reestimating dirichlet hyperparameters. Defaults to False.
        optimize_burn_in (int): Number of iterations to run before first estimating dirichlet hyperparameters. Defaults to False.
        use_symmetric_alpha (bool): Only optimize the concentration parameter of the prior over document-topic
                                    distributions. This may reduce the number of very small, poorly estimated
                                    topics, but may disperse common words over several topics. Defaults to False.
        alpha (float): Sum over topics of smoothing over doc-topic distributions. alpha_k = [this value] / [num topics]. Defaults to False.
        beta (float): Smoothing parameter for each topic-word. Defaults to False.
        output_topic_keys (bool): Write the top words for each topic and any Dirichlet parameters. Defaults to True.
        topic_word_weights_file (bool): Write unnormalized weights for every topic and word type. Defaults to False.
        word_topic_counts_file (bool): Write a sparse representation of topic-word assignments. By default this is
                                       null, indicating that no file will be written. Defaults to False.
        diagnostics_file (bool): Write measures of topic quality, in XML format. By default this is null,
                                 indicating that no file will be written. Defaults to False.
        xml_topic_report (bool): Write the top words for each topic and any Dirichlet parameters in XML format. Defaults to False.
        xml_topic_phrase_report (bool): Write the top words and phrases for each topic and any Dirichlet parameters in XML format. Defaults to False.
        output_topic_docs (bool): Write the most prominent documents for each topic, at the end of the iterations. Defaults to False.
        num_top_docs (int): Number of top documents for `output_topic_docs`. Defaults to False.
        output_doc_topics (bool): Write the topic proportions per document, at the end of the iterations. Defaults to True.
        doc_topics_threshold (float): Do not print topics with proportions less than this threshold value within `output_doc_topics`. Defaults to False.
        doc_topics_max (int): Do not print more than `int` number of topics. A negative value indicates that all topics should be printed. Defaults to False.
        output_model (bool): Write a serialized MALLET topic trainer object. This type of output is appropriate for pausing
                             and restarting training, but does not produce data that can easily be analyzed. Defaults to False.
        output_state (bool): Output a compressed text file containing the words in the corpus with their topic assignments.
                             The file format can easily be parsed and used by non-Java-based software. Defaults to True.

    Returns:
        None
    """
    if system() == 'Windows':
        log.debug(outfolder)
        shell = True
    else:
        log.debug(outfolder)
        shell = False

    outfolder = os.path.join(os.path.abspath('.'), outfolder)
    param = [path_to_mallet, 'train-topics', '--input', path_to_binary]

    # parameter:
    if num_topics is not False:
        param.append('--num-topics')
        param.append(str(num_topics))
    if num_iterations is not False:
        param.append('--num-iterations')
        param.append(str(num_iterations))
    if num_threads is not False:
        param.append('--num-threads')
        param.append(str(num_threads))
    if num_top_words is not False:
        param.append('--num-top-words')
        param.append(str(num_top_words))
    if num_icm_iterations is not False:
        param.append('--num-icm-iterations')
        param.append(str(num_icm_iterations))
    if no_inference is not False:
        param.append('--no-inference')
        param.append(str(no_inference))
    if random_seed is not False:
        param.append('--random-seed')
        param.append(str(random_seed))

    # hyperparameter:
    if optimize_interval is not False:
        param.append('--optimize-interval')
        param.append(optimize_interval)
    if optimize_burn_in is not False:
        param.append('--optimize-burn-in')
        param.append(optimize_burn_in)
    if use_symmetric_alpha is not False:
        param.append('--use-symmetric-alpha')
        param.append(use_symmetric_alpha)
    if alpha is not False:
        param.append('--alpha')
        param.append(alpha)
    if beta is not False:
        param.append('--beta')
        param.append(beta)

    # output:
    if output_topic_keys:
        param.append('--output-topic-keys')
        param.append(os.path.join(outfolder, 'topic_keys.txt'))
    if topic_word_weights_file:
        param.append('--topic-word-weights-file')
        param.append(os.path.join(outfolder, 'topic_word_weights.txt'))
    if word_topic_counts_file:
        param.append('--word-topic-counts-file')
        param.append(os.path.join(outfolder, 'word_topic_counts.txt'))
    if diagnostics_file:
        param.append('--diagnostics-file')
        param.append(os.path.join(outfolder, 'diagnostics.txt'))
    if xml_topic_report:
        param.append('--xml-topic-report')
        param.append(os.path.join(outfolder, 'topic_report.xml'))
    if xml_topic_phrase_report:
        param.append('--xml-topic-phrase-report')
        param.append(os.path.join(outfolder, 'topic_phrase_report.xml'))
    if output_topic_docs:
        param.append('--output-topic-docs')
        param.append(os.path.join(outfolder, 'topic_docs.txt'))
        if num_top_docs is not False:
            param.append('--num-top-docs')
            param.append(topic_word_weights_file)
    if output_doc_topics:
        param.append('--output-doc-topics')
        param.append(os.path.join(outfolder, 'doc_topics.txt'))
        if doc_topics_threshold:
            param.append('--doc-topics-threshold')
            param.append(topic_word_weights_file)
        if doc_topics_max:
            param.append('--doc-topics-max')
            param.append(topic_word_weights_file)
    if output_model:
        param.append('--output-model')
        param.append(os.path.join(outfolder, 'mallet.model'))
    if output_state:
        param.append('--output-state')
        param.append(os.path.join(outfolder, 'state.gz'))

    try:
       log.info("Accessing Mallet with %s ...", param)
       p = Popen(param, stdout=PIPE, stderr=PIPE, shell=shell)
       out = p.communicate()[1].decode('utf-8')
       log.debug(out)
    except KeyboardInterrupt:
        p.terminate()
        log.error(out)

def _grouper(n, iterable, fillvalue=None):
    """Collects data into fixed-length chunks or blocks.

    Args:

    Returns:

    """

    args=[iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)


def show_doc_topic_matrix(output_folder, doc_topics='doc_topics.txt', topic_keys='topic_keys.txt',
                          easy_file_format=False):
    """Shows document-topic-mapping.

    Args:
        outfolder (str): Folder for MALLET output.
        doc_topics (str): Name of MALLET's doc_topic file. Defaults to 'doc_topics.txt'.
        topic_keys (str): Name of MALLET's topic_keys file. Defaults to 'topic_keys.txt'.

    ToDo: Prettify docnames
    """

    doc_topics=os.path.join(output_folder, doc_topics)
    assert doc_topics
    topic_keys=os.path.join(output_folder, topic_keys)
    assert topic_keys

    doctopic_triples=[]
    mallet_docnames=[]
    topics=[]

    df=pd.read_csv(topic_keys, sep='\t', header=None, encoding='utf-8')
    labels=[]
    for index, item in df.iterrows():
        label=' '.join(item[2].split()[:3])
        labels.append(label)

    with open(doc_topics, encoding='utf-8') as f:
        for line in f:
            li=line.lstrip()
            if li.startswith("#"):
                lines=f.readlines()
                for line in lines:
                    docnum, docname, *values=line.rstrip().split('\t')
                    mallet_docnames.append(docname)
                    for topic, share in _grouper(2, values):
                        triple=(docname, int(topic), float(share))
                        topics.append(int(topic))
                        doctopic_triples.append(triple)
            else:
                easy_file_format=True
                break

    if easy_file_format:
        newindex=[]
        doc_topic_matrix=pd.read_csv(
            doc_topics, sep='\t', names=labels[0:], encoding='utf-8')
        for eins, zwei in doc_topic_matrix.index:
            newindex.append(os.path.basename(zwei))
        doc_topic_matrix.index=newindex
    else:
        # sort the triples
        # triple is (docname, topicnum, share) so sort(key=operator.itemgetter(0,1))
        # sorts on (docname, topicnum) which is what we want
        doctopic_triples=sorted(
            doctopic_triples, key=operator.itemgetter(0, 1))

        # sort the document names rather than relying on MALLET's ordering
        mallet_docnames=sorted(mallet_docnames)

        # collect into a document-term matrix
        num_docs=len(mallet_docnames)

        num_topics=max(topics) + 1

        # the following works because we know that the triples are in
        # sequential order
        data=np.zeros((num_docs, num_topics))

        for triple in doctopic_triples:
            docname, topic, share=triple
            row_num=mallet_docnames.index(docname)
            data[row_num, topic]=share

        topicLabels=[]

        # creates list of topic lables consisting of the 3 most weighed topics
        df=pd.read_csv(topic_keys, sep='\t', header=None, encoding='utf-8')
        labels=[]
        for index, item in df.iterrows():

            topicLabel=' '.join(item[2].split()[:3])
            topicLabels.append(topicLabel)

        shortened_docnames=[]
        for item in mallet_docnames:
            shortened_docnames.append(os.path.basename(item))

        '''
        for topic in range(max(topics)+1):
        topicLabels.append("Topic_" + str(topic))
        '''
        doc_topic_matrix=pd.DataFrame(data=data[0:, 0:],
                                      index=shortened_docnames[0:],
                                      columns=topicLabels[0:])
    return doc_topic_matrix.T

def show_topics_keys(output_folder, topicsKeyFile="topic_keys.txt", num_topics=10):
    """Show topic-key-mapping.

    Args:
        outfolder (str): Folder for Mallet output,
        topicsKeyFile (str): Name of Mallets' topic_key file, default "topic_keys"

    #topic-model-mallet
    Note: FBased on DARIAH-Tutorial -> https://de.dariah.eu/tatom/topic_model_mallet.html

    ToDo: Prettify index
    """

    path_to_topic_keys=os.path.join(output_folder, topicsKeyFile)
    assert path_to_topic_keys

    with open(path_to_topic_keys, encoding='utf-8') as input:
        topic_keys_lines=input.readlines()

    topic_keys=[]
    topicLabels=[]


    for line in topic_keys_lines:
        _, _, words=line.split('\t')  # tab-separated
        words=words.rstrip().split(' ')  # remove the trailing '\n'
        topic_keys.append(words)

    topicKeysMatrix=pd.DataFrame(topic_keys)
    topicKeysMatrix.index=['Topic ' + str(x + 1) for x in range(num_topics)]
    topicKeysMatrix.columns=['Key ' + str(x + 1) for x in range(10)]
    return topicKeysMatrix
