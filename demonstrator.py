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

import matplotlib
matplotlib.use('Agg')
from dariahs_topics import preprocessing
from dariahs_topics import visualization
from dariahs_topics import mallet
from flask import Flask, request, render_template, send_file
from gensim.models import LdaModel
from gensim.corpora import MmCorpus
from lxml import etree
import matplotlib.pyplot as plt
import os
import pandas as pd
import shutil
import threading
import webbrowser
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from werkzeug.utils import secure_filename

__author__ = "Severin Simmler"
__email__ = "severin.simmler@stud-mail.uni-wuerzburg.de"
__date__ = "2017-02-22"

app = Flask(__name__)

@app.route('/')
def index():
    print("Rendering index.html ...")
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # access input
    files = request.files.getlist('files')
    lda = request.form['lda']
    num_topics = int(request.form['number_topics'])
    num_iterations = int(request.form['number_iterations'])
    threshold = int(request.form['mfws'])
    
    if 'gensim' in lda:
        corpus = pd.Series()

    print("Accessing and tokenizing files ...")
    for file in files:
        filename, extension = os.path.splitext(secure_filename(file.filename))
        
        if 'mallet' in lda:
            os.makedirs('./tmp_files', exist_ok=True)
            if extension == '.txt':
                file.save('./tmp_files/' + secure_filename(file.filename))
            elif extension == '.xml':
                ns = dict(tei="http://www.tei-c.org/ns/1.0")
                text = etree.parse(file)
                text = text.xpath('//tei:text', namespaces=ns)[0]
                text = "".join(text.xpath('.//text()'))
                with open('./tmp_files/' + secure_filename(file.filename), 'w+', encoding='utf-8') as f:
                    f.writelines(text)
            
        
        elif 'gensim' in lda:
            if extension == '.txt':
                text = file.read().decode('utf-8')
            elif extension == '.xml':
                ns = dict(tei="http://www.tei-c.org/ns/1.0")
                text = etree.parse(file)
                text = text.xpath('//tei:text', namespaces=ns)[0]
                text = "".join(text.xpath('.//text()'))
            else:
                print("Error: File format is not supported.")
            tokens = list(preprocessing.tokenize(text))
            label = filename
            corpus[label] = tokens
        file.flush()

    if 'mallet' in lda:
        print("Creating MALLET binary ...")
        if request.files.get('stoplist', None):
            os.makedirs('./stopwordlist', exist_ok=True)
            stopwords = request.files['stoplist']
            stopwords.save('./stopwordlist/' + secure_filename(stopwords.filename))
            try:
                mallet.create_mallet_model("./mallet_output", "./tmp_files", 'mallet', stoplist='./stopwordlist/' + secure_filename(stopwords.filename))
            except:
                mallet.create_mallet_model("./mallet_output", "./tmp_files", './mallet/bin/mallet', stoplist='./stopwordlist/' + secure_filename(stopwords.filename))
            shutil.rmtree('./stopwordlist')
        else:
            try:
                mallet.create_mallet_model("./mallet_output", "./tmp_files", 'mallet')
            except:
                mallet.create_mallet_model("./mallet_output", "./tmp_files", './mallet/bin/mallet')
            
        print("Training MALLET LDA model ...")
        try:
            mallet.create_mallet_output('./mallet_output/malletModel.mallet', './mallet_output', 'mallet', num_topics=str(num_topics), num_iterations=str(num_iterations))
        except:
            mallet.create_mallet_output('./mallet_output/malletModel.mallet', './mallet_output', './mallet/bin/mallet', num_topics=str(num_topics), num_iterations=str(num_iterations))
        df = mallet.show_topics_keys('./mallet_output', num_topics=num_topics)
        doc_topic = mallet.show_docTopicMatrix('./mallet_output')
        heatmap = visualization.doc_topic_heatmap(doc_topic)
        heatmap.savefig('./static/heatmap.png')
        heatmap.close()
       

        with open ('./mallet_output/topic_keys.txt', 'r', encoding='utf-8') as f:
            text = f.read()
            wordcloud = WordCloud(width=800, height=600, background_color='white').generate(text)
            plt.imshow(wordcloud)
            plt.axis("off")
            plt.savefig('./static/cloud.png')
            plt.close()
        shutil.rmtree('./tmp_files')
        shutil.rmtree('./mallet_output')
        print("Rendering result.hml ...")
        return render_template('result.html', tables=[df.to_html(classes='df')])
    
    elif 'gensim' in lda:
        labels = corpus.index.tolist()
        tokens = corpus.tolist()
        print("Creating bag-of-words model ...")
        id_types, doc_ids = preprocessing.create_dictionaries(labels, tokens)
        sparse_bow = preprocessing.create_mm(labels, tokens, id_types, doc_ids)

        if request.files.get('stoplist', None):
            print("Accessing external stopword list and cleaning corpus ...")
            stopwords = request.files['stoplist']
            words = stopwords.read().decode('utf-8')
            words = set(preprocessing.tokenize(words))
            hapax = preprocessing.find_hapax(sparse_bow, id_types)
            feature_list = words.union(hapax)
            sparse_bow = preprocessing.remove_features(sparse_bow, id_types, feature_list)
            stopwords.flush()
        else:
            print("Accessing", threshold, "most frequent words and cleaning corpus ...")
            stopwords = preprocessing.find_stopwords(sparse_bow, id_types, threshold)
            hapax = preprocessing.find_hapax(sparse_bow, id_types)
            feature_list = set(stopwords).union(hapax)
            sparse_bow = preprocessing.remove_features(sparse_bow, id_types, feature_list)
    
        print("Creating matrix market model ...")
        preprocessing.save_bow_mm(sparse_bow, 'matrixmarket')

        mm = MmCorpus('matrixmarket.mm')
        doc2id = {value : key for key, value in doc_ids.items()}
        type2id = {value : key for key, value in id_types.items()}

        
        print("Training Gensim LDA with", num_topics, "topics ...")
        model = LdaModel(corpus=mm, id2word=type2id, num_topics=num_topics, iterations=num_iterations, passes=10)

        print("Visualizing document-topic matrix and saving as heatmap.png ...")
        doc_topic = visualization.create_doc_topic(mm, model, corpus.index.tolist())
        heatmap = visualization.doc_topic_heatmap(doc_topic)
        heatmap.savefig('./static/heatmap.png')
        heatmap.close()

        wordcloud = WordCloud(width=800, height=600, background_color='white').fit_words(model.show_topic(1,100))
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.savefig('./static/cloud.png')
        plt.close()

        # Todo: replace by DataFrame.to_html():
        print("Accessing topics for HTML table ...")
        df = preprocessing.gensim2dataframe(model)
        print("Rendering result.html ...")
        return render_template('result.html', tables=[df.to_html(classes='df')])
    
    
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
