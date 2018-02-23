#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, render_template, Response, stream_with_context
from pathlib import Path
import utils
import pandas as pd
import time
from bokeh.plotting import output_file, save
from bokeh.embed import components
from bokeh.resources import INLINE
from dariah_topics import preprocessing
from dariah_topics import postprocessing
from dariah_topics import visualization
import logging
import tempfile
import sys
import shutil
import numpy as np
from werkzeug.utils import secure_filename


__author__ = "Severin Simmler"
__email__ = "severin.simmler@stud-mail.uni-wuerzburg.de"


tempdir = tempfile.mkdtemp()
NUM_KEYS = 10


if getattr(sys, 'frozen', False):
    app = Flask(__name__,
                template_folder=str(Path(sys._MEIPASS, 'templates')),
                static_folder=str(Path(sys._MEIPASS, 'static')))
else:
    app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/help')
def help():
    return render_template('help.html')


@app.route('/modeling', methods=['POST'])
def modeling():
    return Response(stream_with_context(stream_template('modeling.html', logging=create_model())))


@app.route('/model')
def model():
    data = utils.decompress(str(Path(tempdir, 'data.bin.xz')))
    parameter = pd.read_csv(str(Path(tempdir, 'parameter.csv')), index_col=0, encoding='utf-8')
    parameter.columns = ['']
    data['parameter'] = [parameter.to_html(classes=['parameter'], border=0)]
    data['topics'] = [pd.read_csv(str(Path(tempdir, 'topics.csv')), index_col=0, encoding='utf-8').to_html(classes='topics')]
    return render_template('model.html', **data)


@app.after_request
def add_header(r):
    r.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    r.headers['Pragma'] = 'no-cache'
    r.headers['Expires'] = '0'
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

def create_model():
    INFO_2A = "FYI: This might take a while..."
    INFO_3A = "In the meanwhile, have a look at"
    INFO_4A = "our Jupyter notebook introducing"
    INFO_5A = "topic modeling with MALLET."
    INFO_1B = "Iteration {0} of {1} ..."
    INFO_2B = "You have selected {0} text files,"
    INFO_3B = "containing {0} tokens"
    INFO_4B = "or {0} unique types"
    INFO_5B = "to generate {0} topics."
    start = time.time()
    yield "Collecting user input ...", INFO_2A, INFO_3A, INFO_4A, INFO_5A
    user_input = {'files': request.files.getlist('files'),
                  'num_topics': int(request.form['num_topics']),
                  'num_iterations': int(request.form['num_iterations'])}
    if request.files.get('stopword_list', None):
        user_input['stopwords'] = request.files['stopword_list']
    else:
        user_input['mft'] = int(request.form['mft_threshold'])

    parameter = pd.Series()
    parameter['Corpus size, in documents'] = len(user_input['files'])
    parameter['Corpus size (raw), in tokens'] = 0

    yield "Reading and tokenizing corpus ...", INFO_2A, INFO_3A, INFO_4A, INFO_5A
    tokenized_corpus = pd.Series()
    for file in user_input['files']:
        filename = Path(secure_filename(file.filename))
        if filename.suffix == '.txt':
            text = file.read().decode('utf-8')
        elif filename.suffix == '.xml':
            text = utils.process_xml(file)
        tokens = list(preprocessing.tokenize(text))
        tokenized_corpus[filename.stem] = tokens
        parameter['Corpus size (raw), in tokens'] += len(tokens)
        file.flush()
    
    yield "Creating document-term matrix ...", INFO_2A, INFO_3A, INFO_4A, INFO_5A
    document_labels = tokenized_corpus.index
    document_term_matrix = preprocessing.create_document_term_matrix(tokenized_corpus, document_labels)

    group = ['Document size (raw)' for n in range(parameter['Corpus size, in documents'])]
    corpus_stats = pd.DataFrame({'score': np.array(document_term_matrix.sum(axis=1)),
                                 'group': group})

    yield "Removing stopwords and hapax legomena from corpus ...", INFO_2A, INFO_3A, INFO_4A, INFO_5A
    try:
        stopwords = preprocessing.find_stopwords(document_term_matrix, user_input['mft'])
    except KeyError:
        stopwords = user_input['stopwords'].read().decode('utf-8')
        stopwords = preprocessing.tokenize(stopwords)
    hapax_legomena = preprocessing.find_hapax_legomena(document_term_matrix)
    features = set(stopwords).union(hapax_legomena)
    features = [token for token in features if token in document_term_matrix.columns]
    document_term_matrix = document_term_matrix.drop(features, axis=1)

    group = ['Document size (clean)' for n in range(parameter['Corpus size, in documents'])]
    corpus_stats = corpus_stats.append(pd.DataFrame({'score': np.array(document_term_matrix.sum(axis=1)),
                                                     'group': group}))

    parameter['Corpus size (clean), in tokens'] = int(document_term_matrix.values.sum())

    document_term_arr = document_term_matrix.as_matrix().astype(int)
    vocabulary = document_term_matrix.columns

    parameter['Size of vocabulary, in tokens'] = len(vocabulary)
    parameter['Number of topics'] = user_input['num_topics']
    parameter['Number of iterations'] = user_input['num_iterations']

    INFO_2B = INFO_2B.format(parameter['Corpus size, in documents'])
    INFO_3B = INFO_3B.format(parameter['Corpus size (raw), in tokens'])
    INFO_4B = INFO_4B.format(parameter['Size of vocabulary, in tokens'])
    INFO_5B = INFO_5B.format(parameter['Number of topics'])

    yield "Initializing LDA topic model ...", INFO_2B, INFO_3B, INFO_4B, INFO_5B
    
    model = utils.enthread(target=utils.lda_modeling,
                           args=(document_term_arr, user_input['num_topics'], user_input['num_iterations'], tempdir))
    while True:
        msg = utils.read_logfile(str(Path(tempdir, 'topicmodeling.log')))

        if msg == None:
            model = model.get()
            break
        else:
            yield 'Iteration {0} of {1} ...'.format(msg, user_input['num_iterations']), INFO_2B, INFO_3B, INFO_4B, INFO_5B

    parameter['The model log-likelihood'] = round(model.loglikelihood())

    yield "Accessing topics ...", INFO_2B, INFO_3B, INFO_4B, INFO_5B
    topics = postprocessing.show_topics(model=model, vocabulary=vocabulary, num_keys=NUM_KEYS)
    topics.columns = ['Key {0}'.format(i) for i in range(1, NUM_KEYS + 1)]
    topics.index = ['Topic {0}'.format(i) for i in range(1, user_input['num_topics'] + 1)]

    yield "Accessing document topics distributions ...", INFO_2B, INFO_3B, INFO_4B, INFO_5B

    document_topics = postprocessing.show_document_topics(model=model, topics=topics, document_labels=document_labels)
    if document_topics.shape[0] < document_topics.shape[1]:
        if document_topics.shape[1] < 20:
            height = 20 * 28
        else:
            height = document_topics.shape[1] * 28
        document_topics_heatmap = document_topics.T
    else:
        if document_topics.shape[0] < 20:
            height = 20 * 28
        else:
            height = document_topics.shape[0] * 28
        document_topics_heatmap = document_topics
    yield "Creating visualizations ...", INFO_2B, INFO_3B, INFO_4B, INFO_5B
    fig = visualization.PlotDocumentTopics(document_topics_heatmap,
                                           enable_notebook=False)
    heatmap = fig.interactive_heatmap(height=height,
                                      sizing_mode='scale_width',
                                      tools='hover, pan, reset, wheel_zoom, zoom_in, zoom_out')

    output_file(str(Path(tempdir, 'heatmap.html')))
    save(heatmap)

    heatmap_script, heatmap_div = components(heatmap)

    corpus_boxplot = utils.boxplot(corpus_stats)
    corpus_boxplot_script, corpus_boxplot_div = components(corpus_boxplot)
    output_file(str(Path(tempdir, 'corpus_statistics.html')))
    save(corpus_boxplot)

    if document_topics.shape[1] < 10:
        height = 10 * 18
    else:
        height = document_topics.shape[1] * 18
    topics_barchart = utils.barchart(document_topics, height=height)
    topics_script, topics_div = components(topics_barchart)
    output_file(str(Path(tempdir, 'topics_barchart.html')))
    save(topics_barchart)

    if document_topics.shape[0] < 10:
        height = 10 * 18
    else:
        height = document_topics.shape[0] * 18
    documents_barchart = utils.barchart(document_topics.T, height=height, topics=topics)
    documents_script, documents_div = components(documents_barchart)
    output_file(str(Path(tempdir, 'document_topics_barchart.html')))
    save(documents_barchart)

    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
    end = time.time()
    passed_time = round((end - start) / 60)

    if passed_time == 0:
        parameter['Passed time, in seconds'] = round(end - start)
    else:
        parameter['Passed time, in minutes'] = passed_time

    parameter = pd.DataFrame(pd.Series(parameter))
    topics.to_csv(str(Path(tempdir, 'topics.csv')), encoding='utf-8')
    document_topics.to_csv(str(Path(tempdir, 'document_topics.csv')), encoding='utf-8')
    parameter.to_csv(str(Path(tempdir, 'parameter.csv')), encoding='utf-8')
    
    cwd = str(Path(*Path.cwd().parts[:-1]))
    shutil.make_archive(str(Path(cwd, 'topicmodeling')), 'zip', tempdir)

    data = {'heatmap_script': heatmap_script,
            'heatmap_div': heatmap_div,
            'topics_script': topics_script,
            'topics_div': topics_div,
            'documents_script': documents_script,
            'documents_div': documents_div,
            'js_resources': js_resources,
            'css_resources': css_resources,
            'corpus_boxplot_script': corpus_boxplot_script,
            'corpus_boxplot_div': corpus_boxplot_div,
            'cwd': cwd}
    utils.compress(data, str(Path(tempdir, 'data.bin.xz')))
    yield 'render_result', '', '', '', ''


def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    return rv

if __name__ == '__main__':
    app.run()
