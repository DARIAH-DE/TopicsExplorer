import pathlib
import sqlite3
import logging
import json
import datetime
import tempfile
from xml.etree import ElementTree

import flask
import cophi
import numpy as np
import pandas as pd
from werkzeug.utils import secure_filename

TEMPDIR = tempfile.gettempdir()
DATABASE_URI = str(pathlib.Path(TEMPDIR, "topicsexplorer.db"))
LOGFILE = str(pathlib.Path(TEMPDIR, "topicsexplorer.log"))

def init_logging(level=logging.DEBUG):
    # Set up basic configuration:
    logging.basicConfig(level=level,
                        format="%(message)s",
                        filename=LOGFILE,
                        filemode="w")
    # Ignore messages from flask and werkzeug:
    logging.getLogger("flask").setLevel(logging.ERROR)
    logging.getLogger("werkzeug").setLevel(logging.ERROR)


def get_status():
    # Open logfile:
    with pathlib.Path(LOGFILE).open("r", encoding="utf-8") as logfile:
        # Read lines:
        messages = logfile.readlines()
        # Select and strip the last one:
        message = messages[-1].strip()
        # Format the log message:
        message = format_logging(message)
        # Get current time:
        now = datetime.datetime.now().strftime("%H:%M:%S")
        return f"{now}<br>{message}"

def format_logging(message):
    if "n_documents" in message:
        n = message.split("n_documents: ")[1]
        return f"Number of documents: {n}."
    elif "vocab_size" in message:
        n = message.split("vocab_size: ")[1]
        return f"Number of types: {n}."
    elif "n_words" in message:
        n = message.split("n_words: ")[1]
        return f"Number of tokens: {n}."
    elif "n_topics" in message:
        n = message.split("n_topics: ")[1]
        return f"Number of topics: {n}."
    elif "n_iter" in message:
        # Logging might freeze at this point,
        # so better log something like this:
        return "Initializing topic model."
    elif "log likelihood" in message:
        iteration, log_likelihood = message.split("> log likelihood: ")
        return f"Iteration {iteration[1:]}, log-likelihood: {log_likelihood}."
    else:
        return message


def get_db():
    """Establish connection to database.
    """
    if "db" not in flask.g:
        # Establish connection to pointed URI:
        flask.g.db = sqlite3.connect(DATABASE_URI)
    return flask.g.db


def close_db(e=None):
    """Close connection to database.
    """
    # Check if a connection was created:
    db = flask.g.pop("db", None)
    if db is not None:
        # Close connection if exists:
        db.close()


def init_db(app):
    """Initialize database and create tables.
    """
    db = get_db()
    with app.open_resource("schema.sql") as schemafile:
        schema = schemafile.read().decode("utf-8")
        db.executescript(schema)
    db.commit()
    close_db()


def get_data(corpus, topics, iterations, stopwords, mfw):
    """Get input data.
    """
    logging.info("Fetching corpus and parameters...")
    # Get text files, number of topics and number of iterations:
    data = {"corpus": flask.request.files.getlist("corpus"),
            "topics": int(flask.request.form["topics"]),
            "iterations": int(flask.request.form["iterations"])}
    # Get stopword list, if user selected one:
    if flask.request.files.get("stopwords", None):
        logging.info("Fetching external stopwords list...")
        data["stopwords"] = flask.request.files["stopwords"]
    # Use most frequent words threshold otherwise:
    else:
        logging.info("Fetching threshold value for most frequent words...")
        data["mfw"] = int(flask.request.form["mfw"])
    return data


def insert_into_textfiles(values):
    """Insert text files into table.
    """
    logging.info("Connecting to database...")
    # Connect to database:
    db = get_db()
    # Insert values into table:
    for textfile in values:
        # Get title and text:
        title, text = load_textfile(textfile)
        logging.info(f"Loading '{title}'...")
        # Execute SQL:
        db.execute("""
                   INSERT INTO textfiles (title, text) 
                   VALUES(?, ?);
                   """,
                   [title, text])
    logging.info("Committing to database...")
    db.commit()
    logging.info("Closing connection to database...")
    close_db()


def insert_into_model(doc_topic, topics):
    logging.info("Connecting to database...")
    # Connect to database:
    db = get_db()
    # Insert values into table:
    db.execute("""
               INSERT INTO model (doc_topic, topics)
               VALUES(?, ?);
               """,
               [doc_topic, topics])
    logging.info("Committing to database...")
    db.commit()
    logging.info("Closing connection to database...")
    close_db()

def select_textfiles():
    """
    TODO: fetchone? fetchall? nothing?
    """
    cursor = get_db().cursor()
    return cursor.execute("""
                          SELECT title, text 
                          FROM textfiles;
                          """)

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
                          SELECT text 
                          FROM textfiles
                          WHERE title is ?;
                          """, [title])
    return response.fetchone()[0]

def get_documents(textfiles):
    for textfile in textfiles:
        title, text = textfile
        yield cophi.model.Document(text, title)

def load_textfile(textfile):
    """Load textfile and get title.
    """
    # Get filename:
    filename = pathlib.Path(secure_filename(textfile.filename))
    # Get title:
    title = filename.stem
    # Get file extension:
    suffix = filename.suffix
    # Read file:
    text = textfile.read().decode("utf-8")
    # If suffix implies any markup, remove it:
    if suffix in {".xml", ".html"}:
        logging.info("Removing markup...")
        text = remove_markup(text)
    return title, text


def remove_markup(text):
    """Parse string and remove markup.
    """
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
    # Query text files:
    textfiles = select_textfiles()
    logging.info("Constructing document objetcs...")
    # Get cophi.model.Document object:
    documents = get_documents(textfiles)
    logging.info("Constructing corpus object...")
    # Create cophi.model.Corpus object:
    corpus = cophi.model.Corpus(documents)
    logging.info("Fetching stopwords...")
    # Get stopwords:
    stopwords = get_stopwords(data, corpus)
    logging.info("Fetching hapax legomena...")
    # Get hapax legomena:
    hapax = corpus.hapax
    # Join both lists:
    features = set(stopwords).union(set(hapax))
    logging.info("Cleaning corpus...")
    # Clean document-term matrix:
    dtm = corpus.drop(corpus.dtm, features)
    # Get sizes:
    sizes = corpus.num_tokens
    # Convert to a NumPy array and return:
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
