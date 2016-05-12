################################################################################
# Load all dependencies
################################################################################

import glob
import os
import logging
import re
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from gensim import corpora, models, similarities

# Enable gensim logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.INFO)

################################################################################
# Corpus ingestion
################################################################################

# Read corpus into a list of lists
def readCorpus(path):
    files = glob.glob(path)
    documents = []
    for file in files:
        document = open(file)
        document = document.read()
        documents.append(document)
    return documents

# Create a list of document labels from file names
def docLabels(path):
    labels = [os.path.basename(x) for x in glob.glob(path)]
    labels = [x.split('.')[0] for x in labels]
    return labels

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
# Gensim model creation
################################################################################

# Not sure yet if this wrapping function is the optimal solution.
def gensimModel(texts, # list of tokenized texts
               topics = 10, # number of topics
               ldaSource = 'gensim', # 'gensim' or 'mallet'
               mallet_path = '~/Software/mallet/bin/mallet' #future default 'UNKNOWN', or docker solution
               ):

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
    return [model, dictionary, corpus, topics] #TODO: store more info about model specifications

# Generate topic labels from gensim model
def topicLabels(model, no_of_topics): #TODO: extract no_of_topics from corpus
    labels = []
    for i in range(no_of_topics):
        terms = [x[1] for x in model.show_topic(i, topn=3)]
        labels.append(" ".join(terms))
    return labels

# Save all the gensim output
def saveGensimModel(model,
    corpus,
    dictionary,
    no_of_topics,
    doc_labels,
    foldername = 'corpus'
    ):
    print("saving ...\n")
    topics = model.show_topics(num_topics = no_of_topics)
    if not os.path.exists("out"): os.makedirs("out")
    with open("out/"+foldername+"_doclabels.txt", "w") as f:
        for item in doc_labels: f.write(item+"\n")
    with open("out/"+foldername+"_topics.txt", "w") as f:
        for item, i in zip(topics, enumerate(topics)):
            f.write("topic #"+str(i[0])+": "+item+"\n")
    dictionary.save("out/"+foldername+".dict")
    corpora.MmCorpus.serialize("out/"+foldername+".mm", corpus)
    model.save("out/"+foldername+".lda")

################################################################################
# Doc-Topic matrix
################################################################################

# Create a doc-topic matrix from gensim output
def gensim_to_dtm(model, corpus, no_of_topics):
    no_of_docs = len(corpus)
    doc_topic = np.zeros((no_of_docs, no_of_topics))
    for doc, i in zip(corpus, range(no_of_docs)):   # Use document bow from corpus
        topic_dist = model.__getitem__(doc)         # to get topic distribution from model
        for topic in topic_dist:                    # topic_dist is a list of tuples (topic_id, topic_prob)
            doc_topic[i][topic[0]] = topic[1]       # save topic probability
    return doc_topic

################################################################################
# Topic visualization
################################################################################
#
#LDAvis
#Not convinient on MS Windows, pip installation on Ubuntu failed too
#http://nlp.stanford.edu/events/illvi2014/papers/sievert-illvi2014.pdf

# Document-topic heatmap
def docTopHeatmap(doc_topic, doc_labels, topic_labels):
    no_of_topics = len(doc_labels)
    if no_of_topics > 20 or no_of_topics > 20: plt.figure(figsize=(20,20))    # if many items, enlarge figure
    plt.pcolor(doc_topic, norm=None, cmap='Reds')
    plt.yticks(np.arange(doc_topic.shape[0])+1.0, doc_labels)
    plt.xticks(np.arange(doc_topic.shape[1])+0.5, topic_labels, rotation='90')
    plt.gca().invert_yaxis()
    plt.colorbar(cmap='Reds')
    plt.tight_layout()
    plt.show()
