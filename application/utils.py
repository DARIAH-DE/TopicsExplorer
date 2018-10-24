from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree
import logging
import sqlite3
import numpy as np
import pandas as pd
import cophi

import flask
from werkzeug.utils import secure_filename

import constants
import database


class DeadProcess:
    """Provide dead process.
    """
    def is_alive(self):
        return False


def init_app(name):
    """Initialize Flask application.
    """
    app = flask.Flask(name)
    global process
    process  = DeadProcess()
    return app, process


def init_logging(level):
    """Initialize logging.
    """
    logging.basicConfig(level=level,
                        format="%(message)s",
                        filename=constants.LOGFILE,
                        filemode="w")
    # Disable logging for Flask and Werkzeug:
    logging.getLogger("flask").setLevel(logging.ERROR)
    logging.getLogger("werkzeug").setLevel(logging.ERROR)


def init_db(app):
    """Initialize SQLite database.
    """
    db = database.get_db()
    with app.open_resource("schema.sql") as schemafile:
        schema = schemafile.read().decode("utf-8")
        db.executescript(schema)
    db.commit()
    database.close_db()


def get_status():
    """Read logfile and get most recent status.
    """
    logfile = Path(constants.LOGFILE)
    now = datetime.now().strftime("%H:%M:%S")
    with logfile.open("r", encoding="utf-8") as logfile:
        messages = logfile.readlines()
        message = messages[-1].strip()
        message = format_logging(message)
        return "{}<br>{}".format(now, message)


def format_logging(message):
    """Format log messages.
    """
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


def load_textfile(textfile):
    """Load text file, return title and content.
    """
    filename = Path(secure_filename(textfile.filename))
    title = filename.stem
    suffix = filename.suffix
    content = textfile.read().decode("utf-8")
    if suffix in {".xml", ".html"}:
        content = remove_markup(content)
    return title, content


def remove_markup(text):
    """Parse XML and drop tags.
    """
    tree = ElementTree.fromstring(text)
    plaintext = ElementTree.tostring(tree,
                                     encoding="utf8",
                                     method="text")
    return plaintext.decode("utf-8")


def get_documents(textfiles):
    """Get Document objects.
    """
    for textfile in textfiles:
        title, content = textfile
        yield cophi.model.Document(content, title)


def get_stopwords(data, corpus):
    """Get stopwords from file or corpus.
    """
    if "stopwords" in data:
        _, stopwords = load_textfile(data["stopwords"])
        stopwords = stopwords.split("\n")
    else:
        stopwords = corpus.mfw(data["mfw"])
    return stopwords


def get_data(corpus, topics, iterations, stopwords, mfw):
    """Get data from HTML forms.
    """
    data = {"corpus": flask.request.files.getlist("corpus"),
            "topics": int(flask.request.form["topics"]),
            "iterations": int(flask.request.form["iterations"])}
    if flask.request.files.get("stopwords", None):
        data["stopwords"] = flask.request.files["stopwords"]
    else:
        data["mfw"] = int(flask.request.form["mfw"])
    return data


def get_topics(model, vocabulary, maximum=100):
    """Get topics from topic model.
    """
    for i, distribution in enumerate(model.topic_word_):
        yield list(np.array(vocabulary)[np.argsort(distribution)][:-maximum-1:-1])


def get_topic_descriptors(topics):
    """Get first three tokens of a topic as string.
    """
    for topic in topics:
        yield ", ".join(topic[:3])


def get_doc_topic(model, titles, descriptors):
    """Get document-topic distribution from topic model.
    """
    doc_topic = pd.DataFrame(model.doc_topic_)
    doc_topic.index = titles
    doc_topic.columns = descriptors
    return doc_topic


def get_cosine(matrix, descriptors):
    """Calculate cosine similarity between columns.
    """
    d = matrix.T @ matrix
    norm = (matrix * matrix).sum(0, keepdims=True) ** .5
    similarities = d / norm / norm.T
    return pd.DataFrame(similarities, index=descriptors, columns=descriptors)


def get_topic_presence():
    """Get topic presence in the corpus.
    """
    doc_topic = database.select("doc_topic")
    topic_presence = doc_topic.sum(axis=0).sort_values(ascending=False)
    proportions = scale(topic_presence)
    for topic, proportion in zip(topic_presence.index, proportions):
        yield topic, proportion


def scale(vector, minimum=40, maximum=100):
    """Min-max scaler for a vector.
    """
    return np.interp(vector, (vector.min(), vector.max()), (minimum, maximum))
