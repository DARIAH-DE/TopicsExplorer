################################################################################
# Load all dependencies
################################################################################

import glob
import logging
import re
from collections import defaultdict
from gensim import corpora, models, similarities

################################################################################
# Preprocessing
################################################################################

def readCorpus(path):
    files = glob.glob(path)
    documents = []
    for file in files:
        document = open(file)
        document = document.read()
        documents.append(document)
    return documents

################################################################################
# Preprocessing
################################################################################

# Tokenize texts
def tokenize(documents):
    # define regular expression for tokenization
    myRegEx = re.compile('\w+') # compile regex for fast repetition
    texts = []
    for document in documents:
        text = myRegEx.findall(document.lower())
        texts.append(text)
    # Version from Gensim-Tutorial: whithout regex
    #texts = [[word for word in document.lower().split()]
    #         for document in documents]
    return texts

# Remove hapax legomena
def removeHapaxLeg(texts):
    frequency = defaultdict(int)
    for text in texts:
        for token in text:
            frequency[token] += 1
    texts = [[token for token in text if frequency[token] > 1]
            for text in texts]
    return texts

# Remove stopwords according to stopword list
def removeStopWords(texts, stoplist):
    if isinstance(stoplist, str):
        file = open('./helpful_stuff/stopwords/' + stoplist)
        stoplist = file.read()
        stoplist = [word for word in stoplist.split()]
        stoplist = set(stoplist)
    texts = [[word for word in text if word not in stoplist]
             for text in texts]
    return texts

################################################################################
# Model creation
################################################################################

def getTopics(texts, # list of tokenized texts
               topics = 10, # number of topics
               ldaSource = 'gensim', # 'gensim' or 'mallet'
               mallet_path = '~/Software/mallet/bin/mallet' #future default 'UNKNOWN', or docker solution
              ):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                        level=logging.INFO)

    # create dictionary and vectorize
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]

    # create a gensim type topic model
    if ldaSource == 'gensim':
        model = models.LdaModel(corpus,
                                id2word=dictionary,
                                num_topics = topics,
                                passes = 10
                               )
    else:
        if mallet_path == 'UNKNOWN':
            mallet_path = '~/Software/mallet/bin/mallet'# TODO: find a function that opens a selection window
        model = models.wrappers.LdaMallet(
            mallet_path, # Path to local mallet binary
            corpus, # Vectorized copus object
            id2word = dictionary,
            num_topics = topics, # Number of topics
            iterations = 100 # Number of iterations in Gibbs sampling
        )

    # return results
    return model

################################################################################
# Topic visualization
################################################################################
