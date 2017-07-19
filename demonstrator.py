#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Demonstrator: Topics – Easy Topic Modeling.

This script demonstrates the joy of Topic Modeling, wrapped in an user-friendly
web application provided by `DARIAH-DE`_.

.. _DARIAH-DE:
    https://de.dariah.eu
"""


from bokeh.embed import components
from bokeh.resources import INLINE
from dariah_topics import preprocessing
from dariah_topics import visualization
from flask import Flask, request, render_template
import lda
from lxml import etree
import os
import pandas as pd
import shutil
import sys
import threading
import webbrowser
from werkzeug.utils import secure_filename

__author__ = "Severin Simmler"
__email__ = "severin.simmler@stud-mail.uni-wuerzburg.de"

if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    app = Flask(__name__, template_folder=template_folder,
                static_folder=static_folder)
else:
    app = Flask(__name__)


def tei(file):
    ns = dict(tei='http://www.tei-c.org/ns/1.0')
    text = etree.parse(file)
    text = text.xpath('//tei:text', namespaces=ns)[0]
    return ''.join(text.xpath('.//text()'))


@app.route('/')
def index():
    print("Rendering index.html ...")
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    print("Accessing user input ...")
    files = request.files.getlist('files')
    print("%s text files." % len(files))
    num_topics = int(request.form['num_topics'])
    print("%s topics." % num_topics)
    num_iterations = int(request.form['num_iterations'])
    print("%s iterations." % num_iterations)
    if request.files.get('stopword_list', None):
        print("Using external stopwords list.")
    else:
        mfw_threshold = int(request.form['mfw_threshold'])
        print("%s most frequent words." % mfw_threshold)

    corpus = pd.Series()
    for file in files:
        filename, extension = os.path.splitext(secure_filename(file.filename))
        print("Tokenizing %s ..." % file)
        if extension == '.txt':
            text = file.read().decode('utf-8')
        elif extension == '.xml':
            text = tei(file)
        else:
            print("File format is not supported.")
        tokens = list(preprocessing.tokenize(text))
        corpus[filename] = tokens
        file.flush()

    app.logger.info("Creating doc-term-matrix ...")
    doc_term_matrix = preprocessing.create_doc_term_matrix(
        corpus, corpus.index)

    if request.files.get('stopword_list', None):
        print("Accessing external stopwords list ...")
        stopword_list = request.files['stopword_list']
        stopwords = stopword_list.read().decode('utf-8')
        stopwords = preprocessing.tokenize(stopwords)
        stopword_list.flush()
    else:
        print("Determining %s most frequent words" % mfw_threshold)
        stopwords = preprocessing.find_stopwords(
            doc_term_matrix, mfw_threshold)
    print("Determining hapax legomena ...")
    hapax = preprocessing.find_hapax(doc_term_matrix)
    features = set(stopwords).union(hapax)
    print("Removing stopwords and hapax legomena from corpus ...")
    doc_term_matrix = preprocessing.remove_features(doc_term_matrix, features)
    doc_term_arr = doc_term_matrix.as_matrix().astype(int)
    print("Accessing corpus vocabulary ...")
    corpus_vocabulary = doc_term_matrix.columns

    print("LDA training ...")
    model = lda.LDA(n_topics=num_topics, n_iter=num_iterations)
    model.fit(doc_term_arr)

    print("Accessing topics ...")
    topics = preprocessing.lda2dataframe(model, corpus_vocabulary)
    print("Accessing doc-topic-matrix ...")
    doc_topics = preprocessing.lda_doc_topic(model, topics, corpus.index)
    print("Creating interactive heatmap ...")
    heatmap = visualization.doc_topic_heatmap_interactive(doc_topics)
    script, div = components(heatmap)
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
    '''
    print("Creating heatmap ...")
    heatmap = visualization.doc_topic_heatmap(doc_topics)
    if getattr(sys, 'frozen', False):
        heatmap.savefig(os.path.join(sys._MEIPASS, 'static', 'heatmap.png'))
    else:
        heatmap.savefig(os.path.join('static', 'heatmap.png'))
    heatmap.close()

    doc_topic_plot = visualization.plot_doc_topics(doc_topics, 0)
    if getattr(sys, 'frozen', False):
        doc_topic_plot.savefig(os.path.join(
            sys._MEIPASS, 'static', 'topics.png'))
    else:
        doc_topic_plot.savefig(os.path.join('static', 'topics.png'))
    doc_topic_plot.close()
    '''
    print("Rendering result.html ...")
    return render_template('result.html', topics=[topics.to_html(classes='df')],
                           script=script, div=div, js_resources=js_resources,
                           css_resources=css_resources)


@app.after_request
def add_header(r):
    r.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    r.headers['Pragma'] = 'no-cache'
    r.headers['Expires'] = '0'
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


if __name__ == '__main__':
    threading.Timer(
        1.25, lambda: webbrowser.open('http://127.0.0.1:5000')).start()
    app.run()
