#!/usr/bin/env python3
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
import pandas as pd

log = logging.getLogger('mallet')
log.addHandler(logging.NullHandler())
logging.basicConfig(level = logging.WARNING,
                    format = '%(levelname)s %(name)s: %(message)s')

def create_mallet_model(outfolder, path_to_corpus = os.path.join(os.path.abspath('.'), 'corpus_txt'), path_to_mallet="mallet", outfile = "malletModel.mallet",
                        stoplist = None):
    """Create a mallet binary file

    Args:
        path_to_corpus (str): Absolute path to corpus folder, e.g. '/home/workspace/corpus_txt'.
        path_to_mallet (str): Path to mallet; default = mallet. 
                              If Mallet is not properly installed use absolute path to mallet folder, e.g. '/home/workspace/mallet/bin/mallet'.
        outfolder (str): Folder for Mallet output
        outfile (str): Name of the allet file that will be generated, default = 'malletModel.mallet'
               
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
        shell=True
    else:       
        shell=False
        
    output = os.path.join(outfolder, outfile)
    log.debug(output)    
    param.append("--output")
    param.append(output)
    param.append ("--keep-sequence")
    param.append("--remove-stopwords")
    
    #if(tokens == "True"):
            #param.append("--token-regex")
            #token_regex = "'\p{L}[\p{L}\p{P}]*\p{L}'"
            #param.append(token_regex)
    
    if(stoplist != None):
            param.append("--stoplist-file")
            param.append(stoplist)
            
    log.debug(print(param))
         
    try:
       log.info("Accessing Mallet ...")
       p = Popen(param, stdout=PIPE, stderr=PIPE, shell=shell)
       out = p.communicate()
       log.debug(out)
       log.debug("Mallet file available.")
	   
    except KeyboardInterrupt:
       log.info("Ending mallet process ...")
       p.terminate()
       log.debug("Mallet terminated.")
       
    return output
     
       
def create_mallet_output(path_to_malletModel, outfolder, path_to_mallet="mallet",  num_topics = "10", 
                         #num_iterations = "10", num_top_words = "10"
                         ):
    """Create mallet model

    Args:
        path_to_malletModel(str): Path to mallet model
        outfolder (str): Folder for Mallet output
        path_to_mallet(str): Path to mallet; default = mallet. 
                             Note: If Mallet is not properly installed use absolute path to mallet folder, e.g. '/home/workspace/mallet/bin/mallet'.
        num_topics(str): Number of Topics that should be created
        num_interations(str): Number of Iterations
        num_top_words(str): Number of keywords for each topic
        
    Note: Use create_mallet_model() to generate path_to_malletModel
        
    ToDo: **kwargs() for individual params
    """
    outfolder = doc_topics = os.path.join(os.path.abspath('.'), outfolder)
    
    param = []
    param.append(path_to_mallet)
    param.append("train-topics")
    param.append("--input")
    param.append(path_to_malletModel)
    param.append("--num-topics")
    param.append(num_topics)
    #param.append("--num-iterations")
    #param.append(num_iterations)
    #param.append("--num-top-words")
    #param.append(num_top_words)
    
    sys = system()
    if sys == 'Windows':
        log.debug(outfolder)
        shell = True
    else:
        log.debug(outfolder)
        shell = False
        
    doc_topics = os.path.join(outfolder, "doc_topics.txt")
    topic_keys = os.path.join(outfolder, "topic_keys.txt") 
    state = os.path.join(outfolder, "state.gz")
    word_topics_counts = os.path.join(outfolder, "word_topic_counts.txt") 
    word_topics_weights = os.path.join(outfolder, "word_topic_weights.txt")
        
    param.append("--output-doc-topics")
    param.append(doc_topics)
    param.append("--output-state")
    param.append(state)
    param.append("--output-topic-keys")
    param.append(topic_keys)
#    param.append("--word-topic-counts-file")
#    param.append(word_topic_counts)
#    param.append("--topic-word-weights-file")
#    param.append(word_topics_weights)
    
    log.debug(print(param))

    try:
       log.info("Accessing Mallet ...")
       p = Popen(param, stdout=PIPE, stderr=PIPE, shell=shell)
       out = p.communicate()
       #log.debug(out)
       log.debug("Mallet file available.")


    except KeyboardInterrupt:
       log.info("Ending mallet process ...")
       p.terminate()
       log.debug("Mallet terminated.")

       

def grouper(n, iterable, fillvalue=None):
    """Collect data into fixed-length chunks or blocks

    Args:
        
    Note: 
        
    ToDo: Args, From: DARIAH-Tutorial -> https://de.dariah.eu/tatom/topic_model_mallet.html#topic-model-mallet
    """

    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)
    

def show_docTopicMatrix(output_folder, docTopicsFile = "doc_topics.txt"):
    """Show document-topic-mapping

    Args:
        outfolder (str): Folder for Mallet output, default = 'tutorial_supplementals/mallet_output'
        docTopicsFile (str): Name of Mallets' doc_topic file, default doc_topics.txt
        
    Note: Based on DARIAH-Tutorial -> https://de.dariah.eu/tatom/topic_model_mallet.html#topic-model-mallet
        
    ToDo: Prettify docnames
    """
    
    doc_topics = os.path.join(output_folder, docTopicsFile)
    assert doc_topics
    
    topic_keys = os.path.join(output_folder, "topic_keys.txt")
    assert topic_keys
    
    doctopic_triples = []
    mallet_docnames = []
    topics = []
    
    df = pd.read_csv(topic_keys, sep='\t', header=None)
    labels=[]
    for index, item in df.iterrows():
        label= ' '.join(item[2].split()[:3])
        labels.append(label)
        
    easy_file_format = False

    with open(doc_topics) as f:
        for line in f:
            li=line.lstrip()
            if li.startswith("#"):
                lines = f.readlines()
                for line in lines:
                    docnum, docname, *values = line.rstrip().split('\t')
                    mallet_docnames.append(docname)
                    for topic, share in grouper(2, values):
                        triple = (docname, int(topic), float(share))
                        topics.append(int(topic))
                        doctopic_triples.append(triple)
            else:
                easy_file_format = True
                break


    if(easy_file_format == True):
        newindex=[]
        docTopicMatrix = pd.read_csv(doc_topics, sep='\t', names=labels[0:])
        #print(list(docTopicMatrix.index))
        for eins, zwei in docTopicMatrix.index:
            newindex.append(os.path.basename(zwei))
        docTopicMatrix.index = newindex
        
    else:
        # sort the triples
        # triple is (docname, topicnum, share) so sort(key=operator.itemgetter(0,1))
        # sorts on (docname, topicnum) which is what we want
        doctopic_triples = sorted(doctopic_triples, key=operator.itemgetter(0,1))

        # sort the document names rather than relying on MALLET's ordering
        mallet_docnames = sorted(mallet_docnames)

        # collect into a document-term matrix
        num_docs = len(mallet_docnames) 

        num_topics = max(topics) + 1

        # the following works because we know that the triples are in sequential order
        data = np.zeros((num_docs, num_topics))

        for triple in doctopic_triples:
            docname, topic, share = triple
            row_num = mallet_docnames.index(docname)
            data[row_num, topic] = share
        
        topicLabels = []
    
        #creates list of topic lables consisting of the 3 most weighed topics
        df = pd.read_csv('tutorial_supplementals/mallet_output/topic_keys.txt', sep='\t', header=None)
        labels=[]
        for index, item in df.iterrows():

            topicLabel= ' '.join(item[2].split()[:3])
            topicLabels.append(topicLabel)
        
        shortened_docnames=[]
        for item in mallet_docnames:
            shortened_docnames.append(os.path.basename(item))

        '''
        for topic in range(max(topics)+1):
        topicLabels.append("Topic_" + str(topic))
        '''                   
        docTopicMatrix = pd.DataFrame(data=data[0:,0:],
                  index=shortened_docnames[0:],
                  columns=topicLabels[0:])
        
    return docTopicMatrix.T

def show_topics_keys(output_folder, topicsKeyFile = "topic_keys.txt"):
    """Show topic-key-mapping

    Args:
        outfolder (str): Folder for Mallet output,
        topicsKeyFile (str): Name of Mallets' topic_key file, default "topic_keys"
        
    Note: FBased on DARIAH-Tutorial -> https://de.dariah.eu/tatom/topic_model_mallet.html#topic-model-mallet
        
    ToDo: Prettify index
    """
    
    path_to_topic_keys = os.path.join(output_folder, topicsKeyFile)
    assert path_to_topic_keys

    with open(path_to_topic_keys) as input:
        topic_keys_lines = input.readlines()

    topic_keys = []
    topicLabels = []


    for line in topic_keys_lines:
        _, _, words = line.split('\t')  # tab-separated
        words = words.rstrip().split(' ')  # remove the trailing '\n'
        topic_keys.append(words) 
        
    topicKeysMatrix = pd.DataFrame(topic_keys)

    return topicKeysMatrix


