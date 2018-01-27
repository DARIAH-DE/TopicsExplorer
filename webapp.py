#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import sys
import time
from bokeh.layouts import column
from bokeh.plotting import figure
from bokeh.models import CustomJS, ColumnDataSource, HoverTool
from bokeh.models.widgets import Dropdown
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
import re
from werkzeug.utils import secure_filename


__author__ = "Severin Simmler"
__email__ = "severin.simmler@stud-mail.uni-wuerzburg.de"


log = logging.getLogger('webapp')


NUM_KEYS = 5
TOOLS = 'hover, pan, reset, save, wheel_zoom, zoom_in, zoom_out'
JAVASCRIPT = '''
             var f = cb_obj.value;
             var options = %s;
             
             for (var i in options) {
                 if (f == options[i]) {
                     console.log("Visible: " + options[i])
                     eval(options[i]).visible = true;
                 }
                 else {
                     console.log("Unvisible: " + options[i])
                     eval(options[i]).visible = false;
                 }
             }
             console.log(' ')
             '''


if getattr(sys, 'frozen', False):
    app = Flask(__name__,
                template_folder=os.path.join(sys._MEIPASS, 'templates'),
                static_folder=os.path.join(sys._MEIPASS, 'static'))
else:
    app = Flask(__name__)


def process_xml(file):
    ns = dict(tei='http://www.tei-c.org/ns/1.0')
    text = etree.parse(file)
    try:
        text = text.xpath('//tei:text', namespaces=ns)[0]
    except IndexError:
        pass
    return ''.join(text.xpath('.//text()'))


def boxplot(document_topics, height, topics=True):
    y_range = document_topics.columns.tolist()
    fig = figure(y_range=y_range, plot_height=height, tools=TOOLS,
                 toolbar_location='right', sizing_mode='scale_width',
                 logo=None)

    plots = {}
    options = document_topics.index.tolist()
    for i, option in enumerate(options):
        x_axis = document_topics.iloc[i]
        source = ColumnDataSource(dict(Describer=y_range, Proportion=x_axis))
        option = re.sub(' ', '_', option)
        bar = fig.hbar(y='Describer', right='Proportion', source=source,
                       height=0.5, color='#053967')
        bar.visible = False
        plots[option] = bar

    fig.xgrid.grid_line_color = None
    fig.x_range.start = 0
    fig.select_one(HoverTool).tooltips = [('Proportion', '@Proportion')]
    fig.xaxis.axis_label = 'Proportion'
    
    callback = CustomJS(args=plots, code=JAVASCRIPT % list(plots.keys()))
    
    menu = [(select, re.sub(' ', '_', option)) for select, option in zip(document_topics.index, options)]
    if topics:
        dropdown = Dropdown(label="Select Topic", menu=menu, callback=callback)
    else:
        dropdown = Dropdown(label="Select Document", menu=menu, callback=callback)
    return column(dropdown, fig, sizing_mode='scale_width')


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server.")
    func()


@app.route('/')
def index():
    log.info("Rendering main page ...")
    return render_template('index.html')


@app.route('/modeling', methods=['POST'])
def modeling():
    start = time.time()
    parameter = []
    log.info("Accessing user input ...")
    files = request.files.getlist('files')
    log.info("Got {0} text files.".format(str(len(files))))
    num_topics = int(request.form['num_topics'])
    log.info("Got {0} topics.".format(str(num_topics)))
    num_iterations = int(request.form['num_iterations'])
    log.info("Got {0} iterations.".format(str(num_iterations)))
    if request.files.get('stopword_list', None):
        log.info("Using external stopwords list.")
    else:
        mft_threshold = int(request.form['mft_threshold'])
        log.info("Using '{0}' as threshold for most frequent tokens.".format(str(mft_threshold)))

    log.info("Processing text files ...")
    tokenized_corpus = pd.Series()
    corpus_tokens = 0
    for file in files:
        filename, extension = os.path.splitext(secure_filename(file.filename))
        log.debug("Tokenizing {0} ...".format(file))
        if extension == '.txt':
            text = file.read().decode('utf-8')
        elif extension == '.xml':
            text = process_xml(file)
        else:
            return render_template('error.html')
        tokens = list(preprocessing.tokenize(text))
        tokenized_corpus[filename] = tokens
        corpus_tokens += len(tokens)
        file.flush()
    parameter.append(len(tokenized_corpus))
    parameter.append(corpus_tokens)

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
        log.info("Determining {0} most frequent tokens ...".format(mft_threshold))
        stopwords = preprocessing.find_stopwords(document_term_matrix, mft_threshold)
    log.info("Determining hapax legomena ...")
    hapax_legomena = preprocessing.find_hapax_legomena(document_term_matrix)
    features = set(stopwords).union(hapax_legomena)
    log.info("Removing stopwords and hapax legomena from corpus ...")
    features = [token for token in features if token in document_term_matrix.columns]
    document_term_matrix = document_term_matrix.drop(features, axis=1)
    parameter.append(int(document_term_matrix.values.sum()))
    document_term_arr = document_term_matrix.as_matrix().astype(int)
    log.info("Accessing corpus vocabulary ...")
    vocabulary = document_term_matrix.columns
    parameter.append(len(vocabulary))
    
    parameter.append(num_topics)
    parameter.append(num_iterations)

    log.info("LDA training ...")
    model = lda.LDA(n_topics=num_topics, n_iter=num_iterations)
    model.fit(document_term_arr)
    parameter.append(round(model.loglikelihood()))

    log.info("Accessing topics ...")
    topics = postprocessing.show_topics(model=model, vocabulary=vocabulary, num_keys=NUM_KEYS)
    topics.columns = ['Key {0}'.format(i) for i in range(1, NUM_KEYS + 1)]
    topics.index = ['Topic {0}'.format(i) for i in range(1, num_topics + 1)]
    log.info("Accessing document-topic matrix ...")
    document_topics = postprocessing.show_document_topics(model=model, topics=topics, document_labels=document_labels)

    log.info("Creating interactive heatmap ...")
    if document_topics.shape[0] < document_topics.shape[1]:
        if document_topics.shape[1] < 20:
            height = 20 * 25
        else:
            height = document_topics.shape[1] * 25
        document_topics_heatmap = document_topics.T
    else:
        if document_topics.shape[0] < 20:
            height = 20 * 25
        else:
            height = document_topics.shape[0] * 25
        document_topics_heatmap = document_topics
    fig = visualization.PlotDocumentTopics(document_topics_heatmap,
                                           enable_notebook=False)
    heatmap = fig.interactive_heatmap(height=height,
                                      sizing_mode='scale_width')
    heatmap_script, heatmap_div = components(heatmap)
    
    log.info("Creating interactive boxplots ...")
    if document_topics.shape[1] < 10:
        height = 10 * 20
    else:
        height = document_topics.shape[1] * 15
    topics_boxplot = boxplot(document_topics, height=height)
    topics_script, topics_div = components(topics_boxplot)

    if document_topics.shape[0] < 10:
        height = 10 * 20
    else:
        height = document_topics.shape[1] * 15
    documents_boxplot = boxplot(document_topics.T, height=height, topics=False)
    documents_script, documents_div = components(documents_boxplot)
    
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
    end = time.time()
    passed_time = round((end - start) / 60)
    index = ['Corpus Size in Documents', 'Corpus Size in Tokens', 'Corpus Size in Tokens (cleaned)',
             'Size of Vocabulary', 'Number of Topics', 'Number of Iterations', 'The Model\'s Log Likelihood']
    if passed_time == 0:
        index.append('Passed Time in Seconds')
        parameter.append(round(end - start))
    else:
        index.append('Passed Time in Minutes')
        parameter.append(passed_time)
    parameter = pd.Series(parameter, index=index)
    return render_template('result.html', topics=[topics.to_html(classes='topics')],
                           heatmap_script=heatmap_script, heatmap_div=heatmap_div,
                           topics_script=topics_script, topics_div=topics_div,
                           documents_script=documents_script, documents_div=documents_div,
                           js_resources=js_resources, css_resources=css_resources,
                           parameter=[pd.DataFrame(parameter, columns=['']).to_html(classes=['parameter'], border=0)])


@app.route('/help')
def help():
    return render_template('help.html')


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
