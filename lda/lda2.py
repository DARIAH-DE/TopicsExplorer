#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Functions to prepare a corpus and to do topic modeling with gensim.
This module has been imported from the DARIAH-DE project.
ToDo: Global variables
"""


__author__ = "DARIAH-DE"
__authors__ = "Steffen Pielstroem, Philip Duerholt, Sina Bock"
__email__ = "pielstroem@biozentrum.uni-wuerzburg.de, philip.duerholt@stud-mail.uni-wuerzburg.de, sina.bock@stud-mail.uni-wuerzburg.de"
__license__ = ""
__version__ = "0.2"
__date__ = "2016-09-22"



from gensim.corpora import MmCorpus, Dictionary
from gensim.models import LdaMulticore, LdaModel
from gensim import corpora
import pandas as pd
import re
import os
import csv
import glob
import logging

log = logging.getLogger('lda2')
log.addHandler(logging.NullHandler())

# To enable logger, uncomment the following three lines.
#logging.basicConfig(level=logging.INFO,
#                    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
#                    datefmt='%d-%b-%Y %H:%M:%S')

########################################################################
# input generally needed
########################################################################

# path to the corpus
path = os.path.join(os.getcwd(), 'corpus_off')
# name of the folder that includes the corpus
foldername = os.path.basename(path)

# document size (in words)
doc_size = 1000  

# uses the pipeline's ParagraphId to split text into documents, 
# overrides doc_size - 1: on, 0: off 
doc_split = 0                                    
 
# no. of topics to be generated
no_of_topics = 30

# no. of lda iterations - usually, the more the better, but increases computing time
no_of_passes = 10                              
 
# perplexity estimation every n chunks - 
# the smaller the better, but increases computing time
eval = 1  

# documents to process at once
chunk = 100                                     
 
# "symmetric", "asymmetric", "auto", or array (default: a symmetric 1.0/num_topics prior)
# affects sparsity of the document-topic (theta) distribution
alpha = "symmetric" 


# custom alpha may increase topic coherence, but may also produce more topics with zero probability
# alpha = np.array([ 0.02, 0.02, 0.02, 0.03, 0.03, 0.03, 0.04, 0.04, 0.04, 0.05,
# 0.05, 0.04, 0.04, 0.04, 0.03, 0.03, 0.03, 0.02, 0.02, 0.02])

# can be a number (int/float), an array, or None
# affects topic-word (lambda) distribution - not necessarily beneficial to topic coherence
eta = None  

########################################################################
# input needed for files that are not tagged with DKProWrapper
########################################################################

# Path to stopwordlist
stopwordlist = os.path.join(os.getcwd(), 'stopwords.txt')  


########################################################################
# additional input for files that are tagged with DKProWrapper
########################################################################

# columns to read from csv file
columns = ['ParagraphId', 'TokenId', 'Lemma', 'CPOS', 'NamedEntity']

# parts-of-speech to include into the model
pos_tags = ['ADJ','NN', 'V']                        
    




def preprocessing(path, columns, pos_tags, doc_size, doc_split, stopwordlist):
    """
    Remove stopwords and hapax legomena. If files tagged collect the specified parts-of-speech-tags only.
    Args:
        path (str): Path / glob pattern of the text files to process.
		columns (str[]): Columns to read from csv file - if file is tagged.
		pos_tags (str[]): Parts-of-speech to include into the model - if file is tagged.
		doc_size (int): Document size (in words)
		doc_split (int): Uses the pipeline's ParagraphId to split text into documents, overrides doc_size - 1: on, 0: off
		stopwordlist: (str): Path to stopwordlist
		
	To Do: Global variables, ignore key_error for tagged files, print("stopwords removed")
    Author:
        DARIAH-DE
    """
	
    docs = []
    doc_labels = []
    stopwords = ""
	
    log.info('reading files ...')

    try:
        with open(stopwordlist, 'r') as f: stopwords = f.read()
    except OSError:
        log.error("stopwordlist could not be read ...")
        pass
    stopwords = sorted(set(stopwords.split("\n")))

    for file in os.listdir(path=path):
        if not file.startswith("."):
            filepath = os.path.join(path, file)

            df = pd.read_csv(filepath, sep="\t", quoting=csv.QUOTE_NONE)
            df = df[columns]
            df = df.groupby('CPOS')

            doc = pd.DataFrame()
			# collect only the specified parts-of-speech
            for p in pos_tags:                          
                doc = doc.append(df.get_group(p))  
            # construct documents
            if doc_split:
				# size according to paragraph id
                doc = doc.groupby('ParagraphId')
                for para_id, para in doc:
                    docs.append(para['Lemma'].values.astype(str))
					# use filename + doc id as plot label
                    doc_labels.append(''.join([file.split(".")[0]," #",str(para_id)]))     
            else:
				# size according to doc_size
                doc = doc.sort_values(by='TokenId')
                i = 1
                while(doc_size < doc.shape[0]):
                    docs.append(doc[:doc_size]['Lemma'].values.astype(str))
                    doc_labels.append(''.join([file.split(".")[0]," #",str(i)]))
					# drop doc_size rows
                    doc = doc.drop(doc.index[:doc_size])        
                    i += 1
                docs.append(doc['Lemma'].values.astype(str))
				# add the rest				
                doc_labels.append(''.join([file.split(".")[0]," #",str(i)]))
            
            # save processed corpus for further use
            if not os.path.exists(os.path.join(os.getcwd(),"swcorp")):
                    os.makedirs(os.path.join(os.getcwd(),"swcorp"))
            
            swpath = os.path.join('swcorp', ".".join((os.path.basename(file), "txt")))
  
            with open(swpath, 'w', encoding = "utf-8") as text:
                text.write(" ".join(word for word in doc['Lemma'].values.astype(str) if word not in stopwords))

    log.info('stopwords removed ...')

	#read processed corpus
    for file in glob.glob(swpath):
        with open(os.path.join(os.getcwd(), file), 'r+', encoding = "utf-8") as f:
            all_tokens = f.read().split()

            # remove hapax legomena
            tokens_once = [word for word in set(all_tokens) if all_tokens.count(word) == 1]
            texts = [word for word in all_tokens if word not in tokens_once]

            f.write(" ".join(texts))
            f.truncate()
			
    log.info('hapax legomena removed ...')
	
    
    log.info('writing processed corpus ...')

    mastercorpus = os.path.join(os.getcwd(), 'mycorpus.txt')
    
    with open(mastercorpus, 'w', encoding = "utf-8") as data:
        folder = glob.glob("swcorp/*")
        for text in folder:
            with open(text, 'r', encoding = "utf-8") as text:
                textline = [re.sub(r'\\n\\r', '', document) for document in ' '.join(text.read().split())]
                if text != folder[-1]:
                    data.write("".join(textline) + "\n")
                else:
                    data.write("".join(textline))
   
def makeDocLabels(path):
    
    """
    Creates list of filenames
    Args:
        path (str): Path / glob pattern of the text files to process.
		
    Author:
        DARIAH-DE
    """
    path = path + "/*"
    doc_labels = [os.path.basename(name) for name in glob.glob(path)]
    return doc_labels

preprocessing(path, columns, pos_tags, doc_size, doc_split, stopwordlist)

# processed and optimized corpus
mastercorpus = os.path.join(os.getcwd(), 'mycorpus.txt')

# dictionary containing words of the corpus
dictionary = corpora.Dictionary(line.lower().split() for line in open(mastercorpus, encoding="utf-8"))


class MyCorpus(object):
     def __iter__(self):
         for line in open('mycorpus.txt'):
             # assume there's one document per line, tokens separated by whitespace
             yield dictionary.doc2bow(line.lower().split())
        
corpus = MyCorpus()

#create output folder
if not os.path.exists("out"): os.makedirs("out")

corpusPath = os.path.join(os.path.join(os.getcwd(), "out"), '.'.join([foldername, 'mm']))

MmCorpus.serialize(corpusPath, corpus)

mm = MmCorpus(corpusPath)

doc_labels = makeDocLabels(path)

log.info('fitting the model ...')

# fitting the model
model = LdaModel(corpus=mm, id2word=dictionary, num_topics=no_of_topics, passes=no_of_passes,
                 eval_every=eval, chunksize=chunk, alpha=alpha, eta=eta)

log.info('generated topics...')

# print topics
topics = model.show_topics(num_topics=no_of_topics)

for item, i in zip(topics, enumerate(topics)):
    log.info('topic #%s: %s', i[0], item)


log.info('saving results...')

# create output folder
if not os.path.exists("out"): os.makedirs("out")

# save doc_labels for further use
with open(os.path.join(os.path.join(os.getcwd(), "out"),''.join([foldername, "_doclabels.txt"])), "w", encoding="utf-8") as f:
    for item in doc_labels: f.write(item+"\n")
	
# save topics for further use
with open(os.path.join(os.path.join(os.getcwd(), "out"), ''.join([foldername, "_topics.txt"])), "w", encoding="utf-8") as f:
    for item, i in zip(topics, enumerate(topics)):
        f.write("".join(["topic #",str(i[0]),": ",str(item),"\n"]))

# save dictionary for further use
dictionary.save(os.path.join(os.path.join(os.getcwd(), "out"), '.'.join([foldername, 'dict'])))

# save model for further use
model.save(os.path.join(os.path.join(os.getcwd(), "out"), '.'.join([foldername, 'lda'])))

log.info('topic modeling finished')
