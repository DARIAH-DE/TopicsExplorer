#!/usr/bin/env python3
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
from dariah_topics import mallet
from flask import Flask, request, render_template
from gensim.models import LdaModel
from gensim.corpora import MmCorpus
import logging
from lxml import etree
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import pandas as pd
import shutil
import threading
import webbrowser
from wordcloud import WordCloud
from werkzeug.utils import secure_filename

__author__ = "Severin Simmler"
__email__ = "severin.simmler@stud-mail.uni-wuerzburg.de"


log = logging.getLogger('demonstrator')
log.addHandler(logging.NullHandler())
logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s %(name)s: %(message)s')

app = Flask(__name__)

def tei(file):
    log.info("Processing TEI XML ...")
    ns = dict(tei='http://www.tei-c.org/ns/1.0')
    text = etree.parse(file)
    text = text.xpath('//tei:text', namespaces=ns)[0]
    return ''.join(text.xpath('.//text()'))

@app.route('/')
def index():
    log.info("Rendering main page ...")
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    log.info("Accessing user input ...")
    files = request.files.getlist('files')
    lda = request.form['lda']
    num_topics = int(request.form['number_topics'])
    num_iterations = int(request.form['number_iterations'])
    threshold = int(request.form['mfws'])
    if request.files.get('stoplist', None):
        stopwords = request.files['stoplist']
    if 'gensim' in lda:
        corpus = pd.Series()

    log.info("Processing text files ...")
    for file in files:
        filename, extension = os.path.splitext(secure_filename(file.filename))

        if 'mallet' in lda:
            os.makedirs('tmp_files', exist_ok=True)
            if extension == '.txt':
                file.save(os.path.join('tmp_files', secure_filename(file.filename)))
            elif extension == '.xml':
                text = tei(file)
                with open(os.path.join('tmp_files', secure_filename(file.filename)), 'w+', encoding='utf-8') as f:
                    f.writelines(text)
            else:
                log.error("File format is not supported.")

        elif 'gensim' in lda:
            if extension == '.txt':
                text = file.read().decode('utf-8')
            elif extension == '.xml':
                text = tei(file)
            else:
                log.error("File format is not supported.")
            tokens = list(preprocessing.tokenize(text))
            label = filename
            corpus[label] = tokens
        file.flush()

    if 'mallet' in lda:
        log.info("Creating MALLET binary ...")
        if request.files.get('stoplist', None):
            os.makedirs('stopwordlist', exist_ok=True)
            stopwords.save(os.path.join('stopwordlist', secure_filename(stopwords.filename)))
            try:
                mallet.create_mallet_binary(path_to_corpus='tmp_files',
                                            path_to_mallet='mallet',
                                            output_file=os.path.join('mallet_output', 'binary.mallet'),
                                            stoplist=os.path.join('stopwordlist', secure_filename(stopwords.filename)))
            except:
                log.error("Retry ...")
                mallet.create_mallet_binary(path_to_corpus='tmp_files',
                                            path_to_mallet=os.path.join('mallet', 'bin', 'mallet'),
                                            output_file=os.path.join('mallet_output', 'binary.mallet'),
                                            stoplist=os.path.join('stopwordlist', secure_filename(stopwords.filename)))
            shutil.rmtree('stopwordlist')
        else:
            try:
                mallet.create_mallet_binary(path_to_corpus='tmp_files', path_to_mallet='mallet')
            except:
                log.error("Retry ...")
                mallet.create_mallet_binary(path_to_corpus='tmp_files', path_to_mallet=os.path.join('mallet', 'bin', 'mallet'))

        log.info("Training MALLET LDA model ...")
        try:
            mallet.create_mallet_model(path_to_binary=os.path.join('mallet_output', 'binary.mallet'),
                                       folder_for_output='mallet_output',
                                       path_to_mallet='mallet',
                                       num_topics=str(num_topics),
                                       num_iterations=str(num_iterations),
                                       num_top_words=10,
                                       output_model=False,
                                       output_state=False,
                                       inferencer_file=False,
                                       evaluator_file=False,
                                       topic_word_weights_file=False,
                                       word_topic_counts_file=False,
                                       diagnostics_file=False,
                                       xml_topic_report=False,
                                       xml_topic_phrase_report=False,
                                       output_topic_docs=False,
                                       output_doc_topics=True)
        except:
            log.error("Retry ...")
            mallet.create_mallet_model(path_to_binary=os.path.join('mallet_output', 'binary.mallet'),
                                       folder_for_output='mallet_output',
                                       path_to_mallet=os.path.join('mallet', 'bin', 'mallet'),
                                       num_topics=str(num_topics),
                                       num_iterations=str(num_iterations),
                                       num_top_words=10,
                                       output_model=False,
                                       output_state=False,
                                       inferencer_file=False,
                                       evaluator_file=False,
                                       topic_word_weights_file=False,
                                       word_topic_counts_file=False,
                                       diagnostics_file=False,
                                       xml_topic_report=False,
                                       xml_topic_phrase_report=False,
                                       output_topic_docs=False,
                                       output_doc_topics=True)

        log.info("Accessing and visualizing MALLET output as heatmap ...")
        df = mallet.show_topics_keys('mallet_output', num_topics=num_topics)
        doc_topic = mallet.show_doc_topic_matrix('mallet_output')
        heatmap = visualization.doc_topic_heatmap(doc_topic)
        heatmap.savefig(os.path.join('static', 'heatmap.png'))
        heatmap.close()

        log.info("Accessing and visualizing MALLET output as wordcloud ...")
        with open (os.path.join('mallet_output', 'topic_keys.txt'), 'r', encoding='utf-8') as f:
            text = f.read()
            wordcloud = WordCloud(width=800, height=600, background_color='white').generate(text)
            plt.imshow(wordcloud)
            plt.axis('off')
            plt.savefig('static/cloud.png')
            plt.close()

        shutil.rmtree('tmp_files')
        shutil.rmtree('mallet_output')
        print("Rendering result page ...")
        return render_template('result.html', tables=[df.to_html(classes='df')])

    elif 'gensim' in lda:
        labels = corpus.index.tolist()
        tokens = corpus.tolist()
        log.info("Creating bag-of-words model ...")
        id_types = preprocessing.create_dictionary(tokens)
        doc_ids = preprocessing.create_dictionary(labels)
        sparse_bow = preprocessing.create_sparse_bow(labels, tokens, id_types, doc_ids)

        if request.files.get('stoplist', None):
            log.info("Accessing external stopword list and cleaning corpus ...")
            words = stopwords.read().decode('utf-8')
            words = set(preprocessing.tokenize(words))
            hapax = preprocessing.find_hapax(sparse_bow, id_types)
            feature_list = words.union(hapax)
            sparse_bow = preprocessing.remove_features(sparse_bow, id_types, feature_list)
            stopwords.flush()
        else:
            log.info("Accessing", threshold, "most frequent words and cleaning corpus ...")
            stopwords = preprocessing.find_stopwords(sparse_bow, id_types, threshold)
            hapax = preprocessing.find_hapax(sparse_bow, id_types)
            feature_list = set(stopwords).union(hapax)
            sparse_bow = preprocessing.remove_features(sparse_bow, id_types, feature_list)

        log.info("Creating matrix market model ...")
        preprocessing.save_sparse_bow(sparse_bow, 'matrixmarket')

        mm = MmCorpus('matrixmarket.mm')
        type2id = {value : key for key, value in id_types.items()}

        log.info("Training Gensim LDA model ...")
        model = LdaModel(corpus=mm, id2word=type2id, num_topics=num_topics, iterations=num_iterations, passes=10)

        log.info("Visualizing Gensim output ...")
        doc_topic = visualization.create_doc_topic(mm, model, corpus.index.tolist())
        heatmap = visualization.doc_topic_heatmap(doc_topic)
        heatmap.savefig(os.path.join('static', 'heatmap.png'))
        heatmap.close()
        wordcloud = WordCloud(width=800, height=600, background_color='white').fit_words(dict(model.show_topic(1,100)))
        plt.imshow(wordcloud)
        plt.axis('off')
        plt.savefig('static/cloud.png')
        plt.close()

        df = preprocessing.gensim2dataframe(model)
        log.info("Rendering result page ...")
        return render_template('result.html', tables=[df.to_html(classes='df')])


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
