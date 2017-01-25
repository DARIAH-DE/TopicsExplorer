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
from gensim.corpora import MmCorpus, Dictionary
from gensim.models import LdaModel
import logging
from platform import system
import os

log = logging.getLogger('mallet')
log.addHandler(logging.NullHandler())
logging.basicConfig(level = logging.DEBUG,
                    format = '%(asctime)s %(levelname)s %(name)s: %(message)s',
                    datefmt = '%d-%b-%Y %H:%M:%S')

def create_mallet_binary(path_to_corpus, path_to_mallet="mallet", outfolder = "mallet_output", outfile = "malletBinary.mallet"):
    """Create a mallet binary file

    Args:
        path_to_corpus (str): Absolute path to corpus folder, e.g. '/home/workspace/corpus_txt'.
        path_to_mallet (str): If Mallet is not properly installed use absolute path to mallet folder, e.g. '/home/workspace/mallet/bin/mallet'.
        outfolder (str): Folder for Mallet output, default = 'mallet_output'
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
    

    print(param)
        
    try:
       log.info("Accessing Mallet ...")
       p = Popen(param, stdout=PIPE, stderr=PIPE, shell=shell)
       out = p.communicate()
       log.debug("Mallet file available.")
 


    except KeyboardInterrupt:
       log.info("Ending mallet process ...")
       p.terminate()
       log.debug("Mallet terminated.")
       
       
def create_mallet_model(path_to_binary, outfolder, path_to_mallet="mallet", num_topics = "20", outfile = "malletBinary.mallet", doc_topics ="doc_topics.txt", topic_keys="topic_keys"):
    """Import a mallet model

    Args:
        path_to_binary (str): Path to mallet binary
        
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
        log.debug(outfolder)
    else:
        doc_topics = outfolder + "/" + doc_topics
        topic_keys = outfolder + "/" + topic_keys
        log.debug(outfolder)
        
    param.append("--output-doc-topics")
    param.append(doc_topics)
    param.append("--output-topic-keys")
    param.append(topic_keys)
    
    if sys == 'Windows':
        param.append("shell=True")

    try:
       log.info("Accessing Mallet ...")
       p = Popen(param, stdout=PIPE, stderr=PIPE)
       out = p.communicate()
       log.debug("Mallet file available.")


    except KeyboardInterrupt:
       log.info("Ending mallet process ...")
       p.terminate()
       log.debug("Mallet terminated.")
    
   