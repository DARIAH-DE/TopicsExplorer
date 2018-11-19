from datetime import datetime
import logging
from pathlib import Path
import shutil
import tempfile
from xml.etree import ElementTree

import cophi
import flask
import numpy as np
import pandas as pd
from werkzeug.utils import secure_filename

from application import database


TEMPDIR = tempfile.gettempdir()
DATABASE = Path(TEMPDIR, "topicsexplorer.db")
LOGFILE = Path(TEMPDIR, "topicsexplorer.log")
DATA_EXPORT = Path(TEMPDIR, "topicsexplorer-data")


class DeadProcess:
    """Provide a dead process.
    """
    def is_alive(self):
        return False


def init_app(name):
    """Initialize Flask application.
    """
    logging.debug("Initializing flask app...")
    app = flask.Flask(name,
                      template_folder=Path("application", "templates"),
                      static_folder=Path("application", "static"))
    process  = DeadProcess()
    return app, process


def init_logging(level):
    """Initialize logging.
    """
    logging.basicConfig(level=level,
                        format="%(message)s",
                        filename=str(LOGFILE),
                        filemode="w")
    # Disable logging for Flask and Werkzeug:
    logging.getLogger("flask").setLevel(logging.ERROR)
    logging.getLogger("werkzeug").setLevel(logging.ERROR)


def init_db(app):
    """Initialize SQLite database.
    """
    logging.debug("Initializing database...")
    db = database.get_db()
    with app.open_resource("schema.sql") as schemafile:
        schema = schemafile.read().decode("utf-8")
        db.executescript(schema)
    db.commit()
    database.close_db()


def format_logging(message):
    """Format log messages.
    """
    if "n_documents" in message:
        n = message.split("n_documents: ")[1]
        return "Number of documents: {}".format(n)
    elif "vocab_size" in message:
        n = message.split("vocab_size: ")[1]
        return "Number of types: {}".format(n)
    elif "n_words" in message:
        n = message.split("n_words: ")[1]
        return "Number of tokens: {}".format(n)
    elif "n_topics" in message:
        n = message.split("n_topics: ")[1]
        return "Number of topics: {}".format(n)
    elif "n_iter" in message:
        return "Initializing topic model..."
    elif "log likelihood" in message:
        iteration, _ = message.split("> log likelihood: ")
        return "Iteration {}".format(iteration[1:])
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
    logging.info("Removing markup...")
    tree = ElementTree.fromstring(text)
    plaintext = ElementTree.tostring(tree,
                                     encoding="utf8",
                                     method="text")
    return plaintext.decode("utf-8")


def get_documents(textfiles):
    """Get Document objects.
    """
    logging.info("Fetching documents...")
    for textfile in textfiles:
        title, content = textfile
        yield cophi.model.Document(content, title)


def get_stopwords(data, corpus):
    """Get stopwords from file or corpus.
    """
    logging.info("Fetching stopwords...")
    if "stopwords" in data:
        _, stopwords = load_textfile(data["stopwords"])
        stopwords = cophi.model.Document(stopwords).tokens
    else:
        stopwords = corpus.mfw(data["mfw"])
    return stopwords


def get_data(corpus, topics, iterations, stopwords, mfw):
    """Get data from HTML forms.
    """
    logging.info("Fetching user data...")
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
    for distribution in model.topic_word_:
        words = list(np.array(vocabulary)[np.argsort(distribution)][:-maximum-1:-1])
        yield "{}, ...".format(", ".join(words[:3])), words


def get_document_topic(model, titles, descriptors):
    """Get document-topic distribution from topic model.
    """
    document_topic = pd.DataFrame(model.doc_topic_)
    document_topic.index = titles
    document_topic.columns = descriptors
    return document_topic


def get_cosine(matrix, descriptors):
    """Calculate cosine similarity between columns.
    """
    d = matrix.T @ matrix
    norm = (matrix * matrix).sum(0, keepdims=True) ** .5
    similarities = d / norm / norm.T
    return pd.DataFrame(similarities, index=descriptors, columns=descriptors)


def scale(vector, minimum=50, maximum=100):
    """Min-max scaler for a vector.
    """
    return np.interp(vector, (vector.min(), vector.max()), (minimum, maximum))


def export_data():
    logging.info("Creating data archive...")
    if DATA_EXPORT.exists():
        unlink_content(DATA_EXPORT)
    else:
        DATA_EXPORT.mkdir()
    data_export = database.select("data_export")
    for name, data in data_export.items():
        if name in {"stopwords"}:
            with Path(DATA_EXPORT, "{}.txt".format(name)).open("w", encoding="utf-8") as file:
                for word in data:
                    file.write("{}\n".format(word))
        else:
            path = Path(DATA_EXPORT, "{}.csv".format(name))
            data.to_csv(path, sep=";", encoding="utf-8")
    shutil.make_archive(DATA_EXPORT, "zip", DATA_EXPORT)


def unlink_content(directory, pattern="*"):
    """Deletes the content of a directory.
    """
    logging.info("Cleaning up in data directory...")
    for p in directory.rglob(pattern):
        if p.is_file():
            p.unlink()


def series2array(s):
    for i, v in zip(s.index, s):
        yield [i, v]