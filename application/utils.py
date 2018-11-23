from datetime import datetime
import json
import logging
from pathlib import Path
import shutil
import sys
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


def init_app(name):
    """Initialize Flask application.
    """
    logging.debug("Initializing Flask app...")
    if getattr(sys, "frozen", False):
        logging.debug("Application is frozen.")
        root = Path(sys._MEIPASS)
    else:
        logging.debug("Application is not frozen.")
        root = Path("application")
    app = flask.Flask(name,
                      template_folder=str(Path(root, "templates")),
                      static_folder=str(Path(root, "static")))
    return app


def init_logging(level):
    """Initialize logging.
    """
    logging.basicConfig(level=level,
                        format="%(message)s",
                        filename=str(LOGFILE),
                        filemode="w")
    # Disable logging for Flask and Werkzeug
    # (this would be a lot of spam, even level INFO):
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
    if suffix in {".txt", ".xml", ".html"}:
        content = textfile.read().decode("utf-8")
        if suffix in {".xml", ".html"}:
            content = remove_markup(content)
        return title, content
    else:
        return None, None


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
    logging.info("Processing user data...")
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
    logging.info("Fetching topics from topic model...")
    for distribution in model.topic_word_:
        words = list(np.array(vocabulary)[np.argsort(distribution)][:-maximum-1:-1])
        yield "{}, ...".format(", ".join(words[:3])), words


def get_document_topic(model, titles, descriptors):
    """Get document-topic distribution from topic model.
    """
    logging.info("Fetching document-topic distributions from topic model...")
    document_topic = pd.DataFrame(model.doc_topic_)
    document_topic.index = titles
    document_topic.columns = descriptors
    return document_topic


def get_cosine(matrix, descriptors):
    """Calculate cosine similarity between columns.
    """
    logging.info("Calculcating cosine similarity...")
    d = matrix.T @ matrix
    norm = (matrix * matrix).sum(0, keepdims=True) ** .5
    similarities = d / norm / norm.T
    return pd.DataFrame(similarities, index=descriptors, columns=descriptors)


def scale(vector, minimum=50, maximum=100):
    """Min-max scaler for a vector.
    """
    logging.debug("Scaling data from {} to {}...".format(minimum, maximum))
    return np.interp(vector, (vector.min(), vector.max()), (minimum, maximum))


def export_data():
    """Export model output to ZIP archive.
    """
    logging.info("Creating data archive...")
    if DATA_EXPORT.exists():
        unlink_content(DATA_EXPORT)
    else:
        DATA_EXPORT.mkdir()
    model, stopwords = database.select("data_export")
    document_topic, topics, document_similarities, topic_similarities = model

    logging.info("Preparing document-topic distributions...")
    document_topic = pd.read_json(document_topic, orient="index")
    document_topic.columns = [col.replace(",", "").replace(" ...", "") for col in document_topic.columns]

    logging.info("Preparing topics...")
    topics = pd.read_json(topics, orient="index")
    topics.index = ["Topic {}".format(n) for n in range(topics.shape[0])]
    topics.columns = ["Word {}".format(n) for n in  range(topics.shape[1])]

    logging.info("Preparing topic similarity matrix...")
    topic_similarities = pd.read_json(topic_similarities)
    topic_similarities.columns = [col.replace(",", "").replace(" ...", "") for col in topic_similarities.columns]
    topic_similarities.index = [ix.replace(",", "").replace(" ...", "") for ix in topic_similarities.index]

    logging.info("Preparing document similarity matrix...")
    document_similarities = pd.read_json(document_similarities)
    data_export = {"document-topic-distribution": document_topic,
                   "topics": topics,
                   "topic-similarities": topic_similarities,
                   "document-similarities": document_similarities,
                   "stopwords": json.loads(stopwords)}

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
    """Convert pandas Series to a 2-D array.
    """
    for i, v in zip(s.index, s):
        yield [i, v]
