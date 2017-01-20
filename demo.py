#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Demonstrator.

This module contains pre-processing functions, various `Gensim`_ related functions for
topic modeling and LDA visualization provided by `DARIAH-DE`_.

.. _Gensim:
    https://radimrehurek.com/gensim/index.html
.. _DARIAH-DE:
    https://de.dariah.eu
    https://github.com/DARIAH-DE
"""

import threading
import collection
import webbrowser
import matplotlib.pyplot as plt
from flask import Flask, request, render_template, send_file
from werkzeug.utils import secure_filename
from gensim import corpora, models, similarities
from gensim.corpora import MmCorpus, Dictionary
from gensim.models import LdaMulticore, LdaModel

__author__ = "DARIAH-DE"
__email__ = "severin.simmler@stud-mail.uni-wuerzburg.de"
__version__ = "0.2"
__date__ = "2017-01-16"

app = Flask(__name__)


@app.route('/')
def index():
    """
    Render template ~/static/index.html
    """
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Upload csv files and create:
        * ~/out/corpus.dict
        * ~/out/corpus.lda
        * ~/out/corpus.lda.state
        * ~/out/corpus.mm
        * ~/out/corpus.mm.index
        * ~/out/corpus_doclabels.txt
        * ~/out/corpus_topics.txt
        * ~/mycorpus.txt

    As well as (for example):
        * ~/swcorp/Doyle_AStudyinScarlet.txt
        * ~/swcorp/Lovecraft_AttheMountainofMadness.txt
        * etc.
    """

    # stopwords
    stopwords = request.files['stoplist']

    # PREPROCESSING
    files = request.files.getlist('files')
    docs = []
    doc_labels = []

    print("\n reading files ...\n")

    for file in files:
        file_label = secure_filename(file.filename).split('.')[0]
        text_file = file.read().decode('utf-8')
        # tokenize
        tokens = list(collection.tokenize(text_file))
        print(request.data['segments'])
        segments = collection.segmenter(text_file, int(request.data['segments']))
        print(segments)
        doc = pd.DataFrame()
        for p in pos_tags:  # collect only the specified parts-of-speech
            doc = doc.append(df.get_group(p))
            # construct documents
            if doc_split:  # size according to paragraph id
                doc = doc.groupby('ParagraphId')
                for para_id, para in doc:
                    docs.append(para['Lemma'].values.astype(str))
                    doc_labels.append(
                        ''.join([file_label, " #", str(para_id)]))
            else:  # size according to doc_size
                doc = doc.sort_values(by='TokenId')
                i = 1
                while(doc_size < doc.shape[0]):
                    docs.append(
                        doc[:doc_size]['Lemma'].values.astype(str))
                    doc_labels.append(
                        ''.join([file_label, " #", str(i)]))
                    doc = doc.drop(doc.index[:doc_size])
                    i += 1
                docs.append(doc['Lemma'].values.astype(str))
                doc_labels.append(''.join([file_label, " #", str(i)]))

            if not os.path.exists(os.path.join(os.getcwd(), "swcorp")):
                os.makedirs(os.path.join(os.getcwd(), "swcorp"))

            swpath = os.path.join('swcorp', "".join(file_label))

            with open(swpath + ".txt", 'w', encoding="utf-8") as text:
                text.write(" ".join(
                    word for word in doc['Lemma'].values.astype(str)
                    if word not in stopwords))

    print("\n normalizing and vectorizing ...\n")

    # texts = [
    #   [word for word in doc if word not in stopwords] for doc in docs]

    print("\n stopwords removed ...\n")

    print("\n writing mastercorpus ...\n")

    mastercorpus = os.path.join(os.getcwd(), 'mycorpus.txt')

    with open(mastercorpus, 'w', encoding="utf-8") as data:
        folder = glob.glob("swcorp/*")
        for text in folder:
            with open(text, 'r', encoding="utf-8") as text:
                textline = [re.sub(
                    r'\\n\\r', '', document) for document in ' '.join(
                        text.read().split())]
                if text != folder[-1]:
                    data.write("".join(textline) + "\n")
                else:
                    data.write("".join(textline))

    # MAIN PART
    mastercorpus = os.path.join(os.getcwd(), 'mycorpus.txt')

    dictionary = corpora.Dictionary(
        line.lower().split() for line in open(
            mastercorpus, encoding="utf-8"))

    class MyCorpus(object):
        def __iter__(self):
            for line in open('mycorpus.txt'):
                # assume there's one document per line, tokens
                # separated by whitespace
                yield dictionary.doc2bow(line.lower().split())

    # corpus = buildCorpus(mastercorpus, dictionary)

    corpus = MyCorpus()

    # corpus = glob.glob("swcorpus/*")

    if not os.path.exists("out"):
        os.makedirs("out")
    # if not os.path.exists(os.path.join(os.path.join(os.getcwd(),
    # 'out'), foldername)): os.makedirs(os.path.join
    # (os.path.join(os.getcwd(), 'out'), foldername))

    MmCorpus.serialize(
        os.path.join(os.path.join(os.getcwd(), "out"), '.'.join(
            ['corpus.mm'])), corpus)
    mm = MmCorpus('out/corpus.mm')

    print(mm)

    # doc_labels = glob.glob("corpus/*")

    print("fitting the model ...\n")

    model = LdaModel(
        corpus=mm, id2word=dictionary, num_topics=no_of_topics,
        passes=no_of_passes, eval_every=eval, chunksize=chunk,
        alpha=alpha, eta=eta)

    # model = LdaMulticore(corpus=corpus, id2word=dictionary,
    # num_topics=no_of_topics, passes=no_of_passes,
    # eval_every=eval, chunksize=chunk, alpha=alpha, eta=eta)

    print(model, "\n")

    topics = model.show_topics(num_topics=no_of_topics)

    for item, i in zip(topics, enumerate(topics)):
        print("topic #"+str(i[0])+": "+str(item)+"\n")

    print("saving ...\n")

    if not os.path.exists("out"):
        os.makedirs("out")
    # if not os.path.exists(os.path.join(os.path.join(os.getcwd(),
    # 'out'), foldername)):
    # os.makedirs(os.path.join(os.path.join(os.getcwd(), 'out'),
    # foldername))

    with open(
        os.path.join(os.path.join(os.getcwd(), "out"), ''.join(
            ["corpus_doclabels.txt"])), "w", encoding="utf-8") as f:
            for item in doc_labels:
                f.write(item + "\n")

    with open(
        os.path.join(os.path.join(os.getcwd(), "out"), ''.join(
            ["corpus_topics.txt"])), "w", encoding="utf-8") as f:
        for item, i in zip(topics, enumerate(topics)):
            f.write(
                "".join(["topic #", str(i[0]), ": ", str(item), "\n"]))

    dictionary.save(
        os.path.join(os.path.join(os.getcwd(), "out"), '.'.join(
            ['corpus', 'dict'])))
    # MmCorpus.serialize(
    # os.path.join(os.path.join(os.getcwd(), "out"), '.'.join(
    # [foldername, 'mm'])), corpus)
    model.save(
        os.path.join(os.path.join(os.getcwd(), "out"), '.'.join(
            ['corpus', 'lda'])))

    print("\n ta-daaaa ...\n")

    # VISUALIZATION
    no_of_topics = model.num_topics
    no_of_docs = len(doc_labels)
    doc_topic = np.zeros((no_of_docs, no_of_topics))

    for doc, i in zip(corpus, range(no_of_docs)):
        # topic_dist is a list of tuples (topic_id, topic_prob)
        topic_dist = model.__getitem__(doc)
        for topic in topic_dist:
            doc_topic[i][topic[0]] = topic[1]

    # get plot labels
    topic_labels = []
    for i in range(no_of_topics):
        # show_topic() returns tuples (word_prob, word)
        topic_terms = [x[0] for x in model.show_topic(i, topn=3)]
        topic_labels.append(" ".join(topic_terms))

    # cf. https://de.dariah.eu/tatom/topic_model_visualization.html

    if no_of_docs > 20 or no_of_topics > 20:
        plt.figure(figsize=(20, 20)) # if many items, enlarge figure
    plt.pcolor(doc_topic, norm=None, cmap='Reds')
    plt.yticks(np.arange(doc_topic.shape[0])+1.0, doc_labels)
    plt.xticks(
        np.arange(doc_topic.shape[1])+0.5, topic_labels, rotation='90')
    plt.gca().invert_yaxis()
    plt.colorbar(cmap='Reds')
    plt.tight_layout()
    plt.savefig("./static/corpus_heatmap.svg")
    return render_template('success.html')

if __name__ == '__main__':
    threading.Timer(
        1.25, lambda: webbrowser.open('http://127.0.0.1:5000')).start()
    app.run(debug=True)
