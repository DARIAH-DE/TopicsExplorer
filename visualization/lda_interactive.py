#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Function to generate a interactive topic visualization based on gensim

Works with LDA-models only!

This module has been imported from the DARIAH project

To do: global paths,  log run time?
"""

__author__ = "DARIAH-DE"
__authors__ = "Stefan Pernes, Sina Bock"
__email__ = "stefan.pernes@uni-wuerzburg.de, sina.bock@stud-mail.uni-wuerzburg.de"
__license__ = ""
__version__ = "0.1"
__date__ = "2016-09-26"


from gensim import LdaModel
from gensim.corpora import MmCorpus, Dictionary
import os
import pyLDAvis.gensim
import time
import logging

log = logging.getLogger('lda_interactive')
log.addHandler(logging.NullHandler())

# To enable logger, uncomment the following three lines.
#logging.basicConfig(level=logging.INFO,
#                    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
#                    datefmt='%d-%b-%Y %H:%M:%S')

# get path to gensim output files
path = os.path.join(os.getcwd(),"out")

########################################################################
# log run time
########################################################################

_start_time = time.time()

def tic():
    global _start_time 
    _start_time = time.time()

def tac():
    t_sec = round(time.time() - _start_time)
    (t_min, t_sec) = divmod(t_sec,60)
    (t_hour,t_min) = divmod(t_min,60) 
    log.info('Time passed: {}hour:{}min:{}sec'.format(t_hour,t_min,t_sec))
	
########################################################################
# load gensim output files
########################################################################

# load dictionary
log.info('load dictionary \n")
dictionary = Dictionary.load(os.path.join(path,"corpus.dict"))

# load corpus
log.info('load corpus')
corpus = MmCorpus(os.path.join(path,"corpus.mm"))

# load model
log.info('load model')
model = LdaModel.load(os.path.join(path,"corpus.lda"))


log.info('processing ...')


########################################################################
#cf. https://pyldavis.readthedocs.org/en/latest/modules/API.html
########################################################################

tic()
vis = pyLDAvis.gensim.prepare(model, corpus, dictionary)
tac()
log.info('visualization calculated')

log.info('save interactive.html')
pyLDAvis.save_html(vis, "_interactive.html")

log.info('save interactive.json')
pyLDAvis.save_json(vis, "interactive.json")

pyLDAvis.prepared_data_to_html(vis)
log.info('----DONE----')
