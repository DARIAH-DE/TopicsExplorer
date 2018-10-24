import pathlib
import sqlite3
import logging
import json
import multiprocessing
import lda
import datetime
import tempfile
from xml.etree import ElementTree

import flask
import cophi
import numpy as np
import pandas as pd
from werkzeug.utils import secure_filename

import constants


def init_logging(level=logging.DEBUG):
    logging.basicConfig(level=level,
                        format="%(message)s",
                        filename=constants.LOGFILE,
                        filemode="w")
    logging.getLogger("flask").setLevel(logging.ERROR)
    logging.getLogger("werkzeug").setLevel(logging.ERROR)


def get_status():
    logfile = pathlib.Path(constants.LOGFILE)
    with logfile.open("r", encoding="utf-8") as logfile:
        messages = logfile.readlines()
        message = messages[-1].strip()
        message = format_logging(message)
        now = datetime.datetime.now().strftime("%H:%M:%S")
        return "{}<br>{}".format(now, message)


def format_logging(message):
    if "n_documents" in message:
        n = message.split("n_documents: ")[1]
        return "Number of documents: {}.".format(n)
    elif "vocab_size" in message:
        n = message.split("vocab_size: ")[1]
        return "Number of types: {}.".format(n)
    elif "n_words" in message:
        n = message.split("n_words: ")[1]
        return "Number of tokens: {}.".format(n)
    elif "n_topics" in message:
        n = message.split("n_topics: ")[1]
        return "Number of topics: {}.".format(n)
    elif "n_iter" in message:
        return "Initializing topic model."
    elif "log likelihood" in message:
        iteration, likelihood = message.split("> log likelihood: ")
        return "Iteration {}, log-likelihood: {}.".format(iteration[1:], likelihood)
    else:
        return message


def get_db():
    if "db" not in flask.g:
        flask.g.db = sqlite3.connect(constants.DATABASE_URI)
    return flask.g.db


def close_db(e=None):
    db = flask.g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    db = get_db()
    with app.open_resource("schema.sql") as schemafile:
        schema = schemafile.read().decode("utf-8")
        db.executescript(schema)
    db.commit()
    close_db()


def get_data(corpus, topics, iterations, stopwords, mfw):
    data = {"corpus": flask.request.files.getlist("corpus"),
            "topics": int(flask.request.form["topics"]),
            "iterations": int(flask.request.form["iterations"])}
    if flask.request.files.get("stopwords", None):
        data["stopwords"] = flask.request.files["stopwords"]
    else:
        data["mfw"] = int(flask.request.form["mfw"])
    return data


def insert_into_textfiles(values):
    db = get_db()
    for textfile in values:
        title, content = load_textfile(textfile)
        db.execute("""
                   INSERT INTO textfiles (title, content) 
                   VALUES(?, ?);
                   """,
                   [title, content])
    db.commit()
    close_db()


def insert_into_model(doc_topic, topics):
    db = get_db()
    db.execute("""
               INSERT INTO model (doc_topic, topics)
               VALUES(?, ?);
               """,
               [doc_topic, topics])
    db.commit()
    close_db()


def select_textfiles():
    cursor = get_db().cursor()
    cursor.execute("""
                   SELECT title, content 
                   FROM textfiles;
                   """)
    return cursor.fetchall()


def select_doc_topic():
    cursor = get_db().cursor()
    response = cursor.execute("""
                              SELECT doc_topic 
                              FROM model;
                              """)
    return pd.read_json(response.fetchone()[0])


def select_topics():
    cursor = get_db().cursor()
    response = cursor.execute("""
                              SELECT topics 
                              FROM model;
                              """)
    return json.loads(response.fetchone()[0])


def select_document(title):
    cursor = get_db().cursor()
    response = cursor.execute("""
                              SELECT content 
                              FROM textfiles
                              WHERE title is ?;
                              """, [title])
    return response.fetchone()[0]


def get_documents(textfiles):
    for textfile in textfiles:
        title, content = textfile
        yield cophi.model.Document(content, title)


def load_textfile(textfile):
    filename = pathlib.Path(secure_filename(textfile.filename))
    title = filename.stem
    suffix = filename.suffix
    content = textfile.read().decode("utf-8")
    if suffix in {".xml", ".html"}:
        text = remove_markup(text)
    return title, content


def remove_markup(text):
    tree = ElementTree.fromstring(text)
    plaintext = ElementTree.tostring(tree,
                                     encoding="utf8",
                                     method="text")
    return plaintext.decode("utf-8")


def get_stopwords(data, corpus):
    if "stopwords" in data:
        _, stopwords = load_textfile(data["stopwords"])
        stopwords = stopwords.split("\n")
    else:
        stopwords = corpus.mfw(data["mfw"])
    return stopwords


def preprocess(data):
    logging.info("Querying corpus from database...")
    textfiles = select_textfiles()

    logging.info("Constructing document objetcs...")
    documents = get_documents(textfiles)

    logging.info("Constructing corpus object...")
    corpus = cophi.model.Corpus(documents)

    logging.info("Fetching stopwords...")
    stopwords = get_stopwords(data, corpus)

    logging.info("Fetching hapax legomena...")
    hapax = corpus.hapax
    features = set(stopwords).union(set(hapax))

    logging.info("Cleaning corpus...")
    dtm = corpus.drop(corpus.dtm, features)
    sizes = corpus.num_tokens
    return dtm.values, dtm.columns, dtm.index, sizes.values


def get_topics(model, vocabulary, maximum=100):
    for i, distribution in enumerate(model.topic_word_):
        yield list(np.array(vocabulary)[np.argsort(distribution)][:-maximum-1:-1])


def get_similarities(matrix):
    d = matrix.T @ matrix
    norm = (matrix * matrix).sum(0, keepdims=True) ** .5
    return d / norm / norm.T


def normalize(matrix, sizes):
    return matrix * sizes


def scale(vector):
    return np.interp(vector, (vector.min(), vector.max()), (40, 100))


def get_topic_descriptors(topics):
    for topic in topics:
        yield ", ".join(topic[:3])


def init_app():
    app = flask.Flask("topicsexplorer")
    global process
    process  = multiprocessing.Process()
    return app, process


def workflow():
    data = get_data("corpus",
                    "topics",
                    "iterations",
                    "stopwords",
                    "mfw")
    insert_into_textfiles(data["corpus"])
    dtm, vocabulary, titles, sizes = preprocess(data)
    model = lda.LDA(n_topics=data["topics"], n_iter=data["iterations"])
    model.fit(dtm)
    topics = list(get_topics(model, vocabulary))
    descriptors = list(get_topic_descriptors(topics))
    doc_topic = get_doc_topic(model, titles, descriptors)
    insert_into_model(doc_topic.to_json(), json.dumps(topics))


def get_doc_topic(model, titles, descriptors):
    doc_topic = pd.DataFrame(model.doc_topic_)
    doc_topic.index = titles
    doc_topic.columns = descriptors
    return doc_topic


def get_topic_presence():
    doc_topic = select_doc_topic()
    topic_presence = doc_topic.sum(axis=0)
    topic_presence = topic_presence.sort_values(ascending=False)
    proportions = scale(topic_presence)
    for topic, proportion in zip(topic_presence.index, proportions):
        yield topic, proportion