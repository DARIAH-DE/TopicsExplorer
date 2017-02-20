#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Demonstrator: Topic Modeling.

This module demonstrates the joy of Topic Modeling, wrapped in an user-friendly
web application provided by `DARIAH-DE`_.

Todo: Replace print statements with logging (which is currently not working).

.. _DARIAH-DE:
    https://de.dariah.eu
    https://github.com/DARIAH-DE
"""

from dariah_topics import preprocessing
from dariah_topics import visualization
from flask import Flask, request, render_template, send_file
from gensim.models import LdaModel
from gensim.corpora import MmCorpus
from lxml import etree
import matplotlib.pyplot as plt
import os
import pandas as pd
import threading
import webbrowser
from werkzeug.utils import secure_filename

__author__ = "Severin Simmler"
__email__ = "severin.simmler@stud-mail.uni-wuerzburg.de"
__date__ = "2017-02-20"

app = Flask(__name__)

@app.route('/')
def index():
    print("Rendering index.html ...")
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    files = request.files.getlist('files')
    corpus = pd.Series()
    print("Accessing and tokenizing files ...")
    for file in files:
        filename, extension = os.path.splitext(secure_filename(file.filename))
        if extension == '.txt':
            text = file.read().decode('utf-8')
            file.flush()
        elif extension == '.xml':
            ns = dict(tei="http://www.tei-c.org/ns/1.0")
            text = etree.parse(file)
            text = text.xpath('//tei:text', namespaces=ns)[0]
            text = "".join(text.xpath('.//text()'))
            file.flush()
        else:
            print("File format is not supported.")
        tokens = list(preprocessing.tokenize(text))
        label = filename
        corpus[label] = tokens

    print("Creating bag-of-words model ...")
    id_types, doc_ids = preprocessing.create_dictionaries(corpus.index.tolist(), corpus.tolist())
    sparse_bow = preprocessing.create_mm(corpus.index.tolist(), corpus.tolist(), id_types, doc_ids)

    stopwords = request.files['stoplist']
    if request.files.get('stoplist', None):
        print("Accessing external stopword list and cleaning corpus ...")
        words = stopwords.read().decode('utf-8')
        words = set(preprocessing.tokenize(words))
        clean_term_frequency = preprocessing.remove_features(sparse_bow, id_types, words)
        stopwords.flush()
    else:
        threshold = int(request.form['mfws'])
        print("Accessing", threshold, "most frequent words and cleaning corpus ...")
        stopwords = preprocessing.find_stopwords(sparse_bow, id_types, threshold)
        hapax = preprocessing.find_hapax(sparse_bow, id_types)
        feature_list = set(stopwords).union(hapax)
        clean_term_frequency = preprocessing.remove_features(sparse_bow, id_types, feature_list)
    
    print("Creating matrix market model ...")
    num_docs = max(clean_term_frequency.index.get_level_values("doc_id"))
    num_types = max(clean_term_frequency.index.get_level_values("token_id"))
    sum_counts = sum(clean_term_frequency[0])
    header_string = str(num_docs) + " " + str(num_types) + " " + str(sum_counts) + "\n"

    print("Saving matrix market model to matrixmarket.mm ...")
    with open("matrixmarket.mm", 'w+', encoding = "utf-8") as f:
        f.write("%%MatrixMarket matrix coordinate real general\n")
        f.write(header_string)
        sparse_bow.to_csv(f, sep = ' ', header = None)
        f.flush()

    mm = MmCorpus("matrixmarket.mm")
    doc2id = {value : key for key, value in doc_ids.items()}
    type2id = {value : key for key, value in id_types.items()}

    num_topics = int(request.form['number_topics'])
    passes = int(request.form['passes'])
    print("Training LDA with", num_topics, "topics and", passes, "passes ...")
    model = LdaModel(corpus=mm, id2word=type2id, num_topics=num_topics, passes=passes)

    print("Visualizing document-topic matrix and saving as heatmap.png ...")
    doc_topic = visualization.create_doc_topic(mm, model, corpus.index.tolist())
    heatmap = visualization.doc_topic_heatmap(doc_topic)
    heatmap.savefig('./static/heatmap.png')

    # Todo: replace by DataFrame.to_html():
    print("Accessing topics for HTML table ...")
    import regex
    pattern = regex.compile(r'\p{L}+\p{P}?\p{L}+')
    topics = []
    for n, topic in enumerate(model.show_topics()):
        topics.append((n+1, pattern.findall(topic[1])))
    print("Rendering result.html ...")
    return render_template('result.html', topics=topics, documents=corpus.index.tolist())
    
@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

if __name__ == '__main__':
    threading.Timer(
        1.25, lambda: webbrowser.open('http://127.0.0.1:5000')).start()
    app.run()
