#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Demonstrator: Topic Modeling.

This module demonstrates the joy of Topic Modeling, wrapped in an user-friendly
web application provided by `DARIAH-DE`_.

.. _DARIAH-DE:
    https://de.dariah.eu
    https://github.com/DARIAH-DE
"""

from dariah_topics import preprocessing
from dariah_topics import evaluation
from dariah_topics import visualization
import threading
import webbrowser
import matplotlib.pyplot as plt
from flask import Flask, request, render_template, send_file
from werkzeug.utils import secure_filename
from gensim.models import LdaModel
from gensim.corpora import MmCorpus


__author__ = "Severin Simmler"
__email__ = "severin.simmler@stud-mail.uni-wuerzburg.de"
__date__ = "2017-02-03"

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    files = request.files.getlist('files')
    corpus = []
    labels = []
    for file in files:
        text = file.read().decode('utf-8')
        tokens = list(preprocessing.tokenize(text))
        label = secure_filename(file.filename).split('.')[0]
        corpus.append(tokens)
        labels.append(label)

    id_types, doc_ids = preprocessing.create_dictionaries(labels, corpus)
    sparse_bow = preprocessing.create_mm(labels, corpus, id_types, doc_ids)

    stopwords = request.files['stoplist']
    if len(str(stopwords)) > 46:    # todo: improve this condition
        stopwords = stopwords.read().decode('utf-8')
        stopwords = set(preprocessing.tokenize(stopwords))
        clean_term_frequency = preprocessing.remove_features(sparse_bow, id_types, stopwords)
    else:
        threshold = int(request.form['mfws'])
        stopwords = preprocessing.find_stopwords(sparse_bow, id_types, threshold)
        hapax = preprocessing.find_hapax(sparse_bow, id_types)
        feature_list = set(stopwords).union(hapax)
        clean_term_frequency = preprocessing.remove_features(sparse_bow, id_types, feature_list)
    """
    num_docs = max(clean_term_frequency.index.get_level_values("doc_id"))+1 # todo: '+1' correct?
    num_types = max(clean_term_frequency.index.get_level_values("token_id"))+1  # todo: dito
    sum_counts = sum(clean_term_frequency[0])
    header_string = str(num_docs) + " " + str(num_types) + " " + str(sum_counts) + "\n"

    with open("gb_plain.mm", 'w', encoding = "utf-8") as f:
        pass

    with open("gb_plain.mm", 'a', encoding = "utf-8") as f:
        f.write("%%MatrixMarket matrix coordinate real general\n")
        f.write(header_string)
        sparse_bow.to_csv( f, sep = ' ', header = None)

    mm = MmCorpus("gb_plain.mm")
    doc2id = {value : key for key, value in doc_ids.items()}
    type2id = {value : key for key, value in id_types.items()}

    models = []
    for x in range(1, int(request.form['evaluation'])):
        model = LdaModel(corpus=mm, id2word=type2id, iterations=200, num_topics=x, random_state=x)
        topics = model.show_topics(num_topics = x)
        segmented_topics = evaluation.topic_segmenter(model, type2id, x, permutation=True)
        score = evaluation.token_probability(corpus, segmented_topics)
        umass = evaluation.calculate_umass(segmented_topics, score, corpus, x)
        models.append((umass, model))

    best_score, best_model = max(models)
    worst_score, worst_model = min(models)

    with open("./templates/result.html", 'r', encoding='utf-8') as f:
        html = f.readlines()

    #html.insert(89, ) = str(best_model.show_topics())

    with open("./templates/result.html", 'w', encoding='utf-8') as f:
        f.writelines(html)"""
    """
    heat = bool('heatmap' in request.form)
    inter = bool('interactive' in request.form)

    if heat:
        vis = visualization.Visualization(best_model, mm, type2id, labels, interactive=False)   # todo: consider user input
        heatmap = vis.make_heatmap()
    if inter:
        print("interactive")
    vis.save_heatmap("./visualizations/heatmap")
    """
    print(bool('mallet' in request.form))
    #return render_template('result.html')
    return "ok"

if __name__ == '__main__':
    threading.Timer(
        1.25, lambda: webbrowser.open('http://127.0.0.1:5000')).start()
    app.run()
