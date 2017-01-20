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
#from platform import system
#import os

log = logging.getLogger('mallet')
log.addHandler(logging.NullHandler())
logging.basicConfig(level = logging.DEBUG,
                    format = '%(asctime)s %(levelname)s %(name)s: %(message)s',
                    datefmt = '%d-%b-%Y %H:%M:%S')

def create_mallet_model(path_to_corpus, num_topics = 10, num_iter = 10):
    """Create a mallet model

    Args:
        path_to_corpus (str): Path to corpus folder, e.g. 'corpus_txt'.
        num_topics (int): Number of topics, default = 10
        num_iter (int): Number of iterations, default = 10

    ToDo:
    """

    #path_to_mallet = os.environ['Mallet_HOME'] + '\\bin\\mallet'

    print(path_to_mallet)

    param = "mallet import-dir --input " + path_to_corpus + " --output corpus.mallet --keep-sequence --remove-stopwords"

    try:
       log.info("Accessing Mallet ...")
       p = Popen(param.split(), stdout=PIPE, stderr=PIPE, shell = True)
       out = p.communicate()
       log.debug("Mallet file available.")


    except KeyboardInterrupt:
       log.info("Ending mallet process ...")
       p.terminate()
       log.debug("Mallet terminated.")
       
       
def import_mallet_model(path_to_model):
    """Import a mallet model

    Args:
        path_to_model (str): Path to mallet model
        
    ToDo:
    """
