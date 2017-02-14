#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Topic Modeling.

This module contains various `Mallet`_ related functions for topic modeling provided by `DARIAH-DE`_.

.. _Mallet:
    http://mallet.cs.umass.edu/
.. _DARIAH-DE:
    https://de.dariah.eu
    https://github.com/DARIAH-DE
"""

__author__ = "DARIAH-DE"
__authors__ = "Steffen Pielstroem, Sina Bock"
__email__ = "pielstroem@biozentrum.uni-wuerzburg.de"
__version__ = "0.1"
__date__ = "2017-01-20"

from subprocess import Popen, call, PIPE
import numpy as np
import itertools
import operator
import logging
from platform import system
import os

log = logging.getLogger('mallet')
log.addHandler(logging.NullHandler())
logging.basicConfig(level = logging.WARNING,
                    format = '%(levelname)s %(name)s: %(message)s')

def create_mallet_model(path_to_corpus = os.path.join(os.path.abspath('.'), 'corpus_txt'), path_to_mallet="mallet", outfolder = "tutorial_supplementals/mallet_output", outfile = "malletBinary.mallet"):
    """Create a mallet binary file

    Args:
        path_to_corpus (str): Absolute path to corpus folder, e.g. '/home/workspace/corpus_txt'.
        path_to_mallet (str): If Mallet is not properly installed use absolute path to mallet folder, e.g. '/home/workspace/mallet/bin/mallet'.
        outfolder (str): Folder for Mallet output, default = 'tutorial_supplementals/mallet_output'
        outfile (str): Name of the binary that will be generated, default = 'malletBinary.mallet'
               
    ToDo:
    """

    if not os.path.exists(outfolder):
        log.info("Creating output folder ...")
        os.makedirs(outfolder)
        
    param = []
    param.append(path_to_mallet)
    param.append("import-dir")
    param.append("--input")
    param.append(path_to_corpus)
    
    sys = system()
    if sys == 'Windows':
        output = outfolder + "\\" + outfile
        log.debug(output)
        shell=True
    else:
        output = outfolder + "/" + outfile
        log.debug(output)
        shell=False
        
    param.append("--output")
    param.append(output)
    param.append ("--keep-sequence")
    param.append("--remove-stopwords")
            
    try:
       log.info("Accessing Mallet ...")
       p = Popen(param, stdout=PIPE, stderr=PIPE, shell=shell)
       out = p.communicate()
       log.debug("Mallet file available.")
	   
    except KeyboardInterrupt:
       log.info("Ending mallet process ...")
       p.terminate()
       log.debug("Mallet terminated.")
       
    return output

     
       
def create_mallet_output(path_to_binary, outfolder = os.path.join(os.path.abspath('.'), "tutorial_supplementals/mallet_output"), path_to_mallet="mallet",  num_topics = "20", doc_topics ="doc_topics.txt", topic_keys="topic_keys"):
    """Import a mallet model

    Args:
        path_to_binary (str): Path to mallet binary
        outfolder (str): Folder for Mallet output, default = 'tutorial_supplementals/mallet_output'
        
    Note: Use create_mallet_binary() to generate path_to_binary
        
    ToDo:
    """

    param = []
    param.append(path_to_mallet)
    param.append("train-topics")
    param.append("--input")
    param.append(path_to_binary)
    param.append("--num-topics")
    param.append(num_topics)
    
    sys = system()
    if sys == 'Windows':
        doc_topics = outfolder + "\\" + doc_topics
        topic_keys = outfolder + "\\" + topic_keys
        state = outfolder + "\\" + "state.gz"
        word_top = outfolder + "\\" + "word_top.txt"
        log.debug(outfolder)
        shell = True
    else:
        doc_topics = outfolder + "/" + doc_topics
        topic_keys = outfolder + "/" + topic_keys
        state = outfolder + "/" + "state.gz"
        word_top = outfolder + "/" + "word_top.txt"
        log.debug(outfolder)
        shell = False
        
    param.append("--output-doc-topics")
    param.append(doc_topics)
    param.append("--output-state")
    param.append(state)
    param.append("--output-topic-keys")
    param.append(topic_keys)
    param.append("–word-topic-counts")
    param.append(word_top)
    
    try:
       log.info("Accessing Mallet ...")
       p = Popen(param, stdout=PIPE, stderr=PIPE, shell=shell)
       out = p.communicate()
       log.debug("Mallet file available.")


    except KeyboardInterrupt:
       log.info("Ending mallet process ...")
       p.terminate()
       log.debug("Mallet terminated.")

    return outfolder
       

def grouper(n, iterable, fillvalue=None):
    """Collect data into fixed-length chunks or blocks

    Args:
        
    Note: 
        
    ToDo: Args, From: DARIAH-Tutorial -> https://de.dariah.eu/tatom/topic_model_mallet.html#topic-model-mallet
    """

    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)
    

def create_docTopicMatrix(output_folder):
    """Create Mallet matrix

    Args:
        
    Note: Testversion
        
    ToDo: From: DARIAH-Tutorial -> https://de.dariah.eu/tatom/topic_model_mallet.html#topic-model-mallet
    """
    
    doc_topics = os.path.join(output_folder, "doc_topics.txt")
    assert doc_topics
    
    doctopic_triples = []
    mallet_docnames = []
   
    doctopicMatrix = np.zeros((16, 20))

    with open(doc_topics) as f:
        f.readline()
        for line in f:
            docnum, docname, *values = line.rstrip().split('\t')
            mallet_docnames.append(docname)
            for topic, share in grouper(2, values):
                triple = (docname, int(topic), float(share))
                doctopic_triples.append(triple)
    
    #print(doctopic_triples[0:5]
    
    # sort the triples
    # triple is (docname, topicnum, share) so sort(key=operator.itemgetter(0,1))
    # sorts on (docname, topicnum) which is what we want
    doctopic_triples = sorted(doctopic_triples, key=operator.itemgetter(0,1))
    #print(doctopic_triples[0:5])

    # sort the document names rather than relying on MALLET's ordering
    mallet_docnames = sorted(mallet_docnames)
    #print(mallet_docnames[0:5])

    # collect into a document-term matrix
    num_docs = len(mallet_docnames)
    #print(num_docs)

    num_topics = 20
    #print(num_topics)

    # the following works because we know that the triples are in sequential order
    doctopicMatrix = np.zeros((num_docs, num_topics))

    for triple in doctopic_triples:
        docname, topic, share = triple
        row_num = mallet_docnames.index(docname)
        doctopicMatrix[row_num, topic] = share
        
    return doctopicMatrix
