#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Topics – Easy Topic Modeling Demonstrator.

This is a web-application introducing the text mining technique Topic Modeling.
Open a command-line and type `python demonstrator.py` to run the application,
your browser will be launched by default. If not, go to http://127.0.0.1:5000/
by yourself.

There are also standalone executables for Windows and macOS available. Please
go to the release section on GitHub.
"""


from dariah_topics import preprocessing
from dariah_topics import visualization
from flask import Flask, request, render_template
import lda
from lxml import etree
import numpy as np
import os
import pandas as pd
import sys
import threading
import webbrowser
from werkzeug.utils import secure_filename

__author__ = "Severin Simmler"
__email__ = "severin.simmler@stud-mail.uni-wuerzburg.de"

if getattr(sys, 'frozen', False):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import mpld3
    from mpld3 import plugins

    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    app = Flask(__name__, template_folder=template_folder,
                static_folder=static_folder)
    
    def plot_mpld3_heatmap(doc_topics, figsize=(1200/96, 800/96), fontsize=12, cmap='Reds'):
        css = """
        .meta {
            background-color: #FFFFFF;
            padding: 10px 10px 10px 10px;
            border: solid;
            border-width: thin;
            font-size: 12;
            font-family: Arial, Helvetica;}
        """
        html = """
        <div class='meta'>
            <b>Topic {}</b>: {}<br>
            <b>Document</b>: {}<br>
            <b>Score</b>: {}
        </div>
        """
        doc_topics = doc_topics.T
        docs = doc_topics.shape[0]
        topics = doc_topics.shape[1]
        labels = []
        for row in doc_topics.iterrows():
            tmp = []
            n = 0
            for topic, score in row[1].iteritems():
                tmp.append(html.format(n, topic, row[0], score))
                n += 1
            labels.extend(tmp)
        fig, ax = plt.subplots(figsize=figsize)
        ax.set_xlabel('Topics', fontsize=fontsize+1)
        heatmap = ax.pcolor(doc_topics, cmap=cmap)
        plt.yticks(np.arange(docs) + 0.5, doc_topics.index, fontsize=fontsize)
        plt.xticks(np.arange(topics) + 0.5, np.arange(topics), fontsize=fontsize)
        fig.subplots_adjust(left=0.27, right=0.95, bottom=0.1, top=0.95, hspace=0.1, wspace=0.1)
        tooltip = plugins.PointHTMLTooltip(heatmap, labels=labels, voffset=10, hoffset=10, css=css)
        plugins.connect(fig, tooltip)
        return fig

else:
    from bokeh.embed import components
    from bokeh.resources import INLINE
    app = Flask(__name__)


def process_xml(file):
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
            text = process_xml(file)
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
    doc_term_matrix = preprocessing.remove_features_from_df(doc_term_matrix, features)
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
    if getattr(sys, 'frozen', False):
        heatmap = plot_mpld3_heatmap(doc_topics)
        return render_template('result.html', topics=[topics.to_html(classes='df')],
                               div=mpld3.fig_to_html(heatmap))
        
    else:
        heatmap = visualization.doc_topic_heatmap_interactive(doc_topics, title=" ")
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


if __name__ == '__main__':
    threading.Timer(
        1.25, lambda: webbrowser.open('http://127.0.0.1:5000')).start()
    app.run()
