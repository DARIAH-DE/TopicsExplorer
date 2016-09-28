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
    print('Time passed: {}hour:{}min:{}sec'.format(t_hour,t_min,t_sec))
	
########################################################################
# load gensim output files
########################################################################

# load dictionary
print("\n load dictionary \n")
dictionary = Dictionary.load(os.path.join(path,"corpus.dict"))

# load corpus
print("\n load corpus \n")
corpus = MmCorpus(os.path.join(path,"corpus.mm"))

# load model
print("\n load model \n")
model = LdaModel.load(os.path.join(path,"corpus.lda"))


print("processing")


########################################################################
#cf. https://pyldavis.readthedocs.org/en/latest/modules/API.html
########################################################################

tic()
vis = pyLDAvis.gensim.prepare(model, corpus, dictionary)
tac()
print("\n visualization calculated \n")

print("\n save interactive.html \n")
pyLDAvis.save_html(vis, "_interactive.html")

print("\n save interactive.json \n")
pyLDAvis.save_json(vis, "interactive.json")

pyLDAvis.prepared_data_to_html(vis)
print("\n done \n")
