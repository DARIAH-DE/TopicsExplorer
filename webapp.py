#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import sys
from bokeh.embed import components
from bokeh.resources import INLINE
from dariah_topics import preprocessing
from dariah_topics import postprocessing
from dariah_topics import visualization
from flask import Flask, request, render_template
import lda
from lxml import etree
import numpy as np
import pandas as pd
from werkzeug.utils import secure_filename


__author__ = "Severin Simmler"
__email__ = "severin.simmler@stud-mail.uni-wuerzburg.de"
__copyright__ = "Copyright 2018, DARIAH-DE"
__status__ = "Development"

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())
logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s: %(message)s')


NUM_KEYS = 7 # number of topic keys


if getattr(sys, 'frozen', False):
    app = Flask(__name__,
                template_folder=os.path.join(sys._MEIPASS, 'templates'),
                static_folder=os.path.join(sys._MEIPASS, 'static'))
else:
    app = Flask(__name__)


def process_xml(file):
    ns = dict(tei='http://www.tei-c.org/ns/1.0')
    text = etree.parse(file)
    text = text.xpath('//tei:text', namespaces=ns)[0]
    return ''.join(text.xpath('.//text()'))


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server.')
    func()


@app.route('/')
def index():
    log.info("Rendering index.html ...")
    return render_template('index.html')


@app.route('/modeling', methods=['POST'])
def modeling():
    log.info("Accessing user input ...")
    files = request.files.getlist('files')
    if not request.files.get('files', None):
        return render_template('error.html')
    elif len(files) < 5:
        return "Too less files"
    log.info("{} text files.".format(str(len(files))))
    num_topics = int(request.form['num_topics'])
    log.info("{} topics.".format(str(num_topics)))
    num_iterations = int(request.form['num_iterations'])
    log.info("{} iterations.".format(str(num_iterations)))
    if request.files.get('stopword_list', None):
        log.info("Using external stopwords list.")
    else:
        mft_threshold = int(request.form['mft_threshold'])
        log.info("{} as threshold for most frequent tokens.".format(str(mft_threshold)))

    tokenized_corpus = pd.Series()
    for file in files:
        filename, extension = os.path.splitext(secure_filename(file.filename))
        log.debug("Tokenizing {} ...".format(file))
        if extension == '.txt':
            text = file.read().decode('utf-8')
        elif extension == '.xml':
            text = process_xml(file)
        else:
            return render_template('error.html')
        tokens = list(preprocessing.tokenize(text))
        tokenized_corpus[filename] = tokens
        file.flush()

    log.info("Creating document-term matrix ...")
    document_labels = tokenized_corpus.index
    document_term_matrix = preprocessing.create_document_term_matrix(tokenized_corpus, document_labels)

    if request.files.get('stopword_list', None):
        log.info("Accessing external stopwords list ...")
        stopword_list = request.files['stopword_list']
        stopwords = stopword_list.read().decode('utf-8')
        stopwords = preprocessing.tokenize(stopwords)
        stopword_list.flush()
    else:
        log.info("Getting {} most frequent tokens ...".format(mft_threshold))
        stopwords = preprocessing.find_stopwords(document_term_matrix, mft_threshold)
    log.info("Getting hapax legomena ...")
    hapax_legomena = preprocessing.find_hapax_legomena(document_term_matrix)
    features = set(stopwords).union(hapax_legomena)
    log.info("Removing stopwords and hapax legomena from corpus ...")
    features = [token for token in features if token in document_term_matrix.columns]
    document_term_matrix = document_term_matrix.drop(features, axis=1)
    document_term_arr = document_term_matrix.as_matrix().astype(int)
    log.info("Accessing corpus vocabulary ...")
    vocabulary = document_term_matrix.columns

    log.info("LDA training ...")
    model = lda.LDA(n_topics=num_topics, n_iter=num_iterations)
    model.fit(document_term_arr)

    log.info("Accessing topics ...")
    topics = postprocessing.show_topics(model=model, vocabulary=vocabulary, num_keys=NUM_KEYS)
    log.info("Accessing document-topic matrix ...")
    document_topics = postprocessing.show_document_topics(model=model, topics=topics, document_labels=document_labels)

    log.info("Creating interactive heatmap ...")
    if document_topics.shape[0] < document_topics.shape[1]:
        document_topics = document_topics.T
    fig = visualization.PlotDocumentTopics(document_topics,
                                           enable_notebook=False)
    heatmap = fig.interactive_heatmap(sizing_mode='scale_width')
    script, div = components(heatmap)
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
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


@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return "Shutdown"


if __name__ == '__main__':
    log.info("Starting application ...")
    app.run()
