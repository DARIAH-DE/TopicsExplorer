import logging
import json
import sqlite3

import flask
import pandas as pd

from application import utils


def get_db():
    """Create connection to SQLite database.
    """
    logging.info("Connecting to database...")
    if "db" not in flask.g:
        flask.g.db = sqlite3.connect(str(utils.DATABASE))
    return flask.g.db


def close_db(e=None):
    """Close connection to SQLite database.
    """
    logging.info("Closing connection to database...")
    db = flask.g.pop("db", None)
    if db is not None:
        db.close()


def _insert_into_textfiles(db, data):
    """Insert data into textfiles table.
    """
    for textfile in data:
        title, content = utils.load_textfile(textfile)
        logging.info("Insert '{}' into database...".format(title))
        db.execute("""
                   INSERT INTO textfiles (title, content) 
                   VALUES(?, ?);
                   """, [title, content])

def _insert_into_token_freqs(db, data):
    logging.info("Insert token frequencies into database...")
    db.execute("""
               INSERT INTO token_freqs (content) 
               VALUES(?);
               """, [data])

def insert_into(table, data):
    """Insert data into database.
    """
    db = get_db()
    if table in {"textfiles"}:
        _insert_into_textfiles(db, data)
    elif table in {"token_freqs"}:
        _insert_into_token_freqs(db, data)
    elif table in {"stopwords"}:
        _insert_into_stopwords(db, data)
    elif table in {"model"}:
        _insert_into_model(db, data)
    db.commit()
    close_db()


def _insert_into_model(db, data):
    """Insert data into model table.
    """
    logging.info("Insert topic model output into database...")
    db.execute("""
               INSERT INTO model (document_topic, topics, document_similarities, topic_similarities)
               VALUES(?, ?, ?, ?);
               """,
               [data["document_topic"], data["topics"],
                data["document_similarities"], data["topic_similarities"]])


def _insert_into_stopwords(db, data):
    """Insert data into stopwords table.
    """
    logging.info("Insert stopwords into database...")
    db.execute("""
               INSERT INTO stopwords (content)
               VALUES(?);
               """,
               [data])


def select(value, **kwargs):
    """Select values from database.
    """
    db = get_db()
    cursor = db.cursor()
    if value in {"textfiles"}:
        return _select_textfiles(cursor)
    elif value in {"textfile_titles"}:
        return _select_textfile_titles(cursor)
    elif value in {"token_freqs"}:
        return _select_token_freqs(cursor)
    elif value in {"document_topic_distributions"}:
        return _select_document_topic_distributions(cursor)
    elif value in {"topics"}:
        return _select_topics(cursor)
    elif value in {"textfile"}:
        return _select_textfile(cursor, **kwargs)
    elif value in {"document_similarities"}:
        return _select_document_similarities(cursor)
    elif value in {"topic_similarities"}:
        return _select_topic_similarities(cursor)
    elif value in {"stopwords"}:
        return _select_stopwords(cursor)
    elif value in {"data_export"}:
        return _select_data_export(cursor)

def _select_stopwords(cursor):
    logging.info("Selecting stopwords from database...")
    return cursor.execute("""
                          SELECT content 
                          FROM stopwords;
                          """).fetchone()[0]

def _select_document_similarities(cursor):
    logging.info("Selecting document similarity matrix from database...")
    return cursor.execute("""
                          SELECT document_similarities 
                          FROM model;
                          """).fetchone()[0]


def _select_topic_similarities(cursor):
    logging.info("Selecting topic similarity matrix from database...")
    return cursor.execute("""
                          SELECT topic_similarities 
                          FROM model;
                          """).fetchone()[0]


def _select_token_freqs(cursor):
    logging.info("Selecting token frequencies from database...")
    return cursor.execute("""
                          SELECT content 
                          FROM token_freqs;
                          """).fetchone()[0]

def _select_textfile_titles(cursor):
    """Select textfile titles from database.
    """
    logging.info("Selecting textfile titles from database...")
    cursor.execute("""
                   SELECT title 
                   FROM textfiles;
                   """)
    return json.dumps([title[0] for title in cursor.fetchall()])


def _select_textfiles(cursor):
    """Select textfiles from database.
    """
    logging.info("Selecting textfiles from database...")
    cursor.execute("""
                   SELECT title, content 
                   FROM textfiles;
                   """)
    return cursor.fetchall()


def _select_document_topic_distributions(cursor):
    """Select document-topic matrix form database.
    """
    logging.info("Selecting document-topic distributions from database...")
    return cursor.execute("""
                          SELECT document_topic 
                          FROM model;
                          """).fetchone()[0]


def _select_topics(cursor):
    logging.info("Selecting topics from database...")
    return cursor.execute("""
                              SELECT topics 
                              FROM model;
                              """).fetchone()[0]


def _select_textfile(cursor, title):
    logging.info("Selecting '{}' from database...".format(title))
    return cursor.execute("""
                          SELECT content 
                          FROM textfiles
                          WHERE title is ?;
                          """, [title]).fetchone()[0]

def _select_data_export(cursor):
    """Select model output from database.
    """
    logging.info("Selectin stopwords from database...")
    stopwords = cursor.execute("""
                              SELECT content 
                              FROM stopwords;
                              """).fetchone()[0]

    logging.info("Selecting model output from database...")
    model = cursor.execute("""
                           SELECT document_topic, topics, document_similarities, topic_similarities 
                           FROM model;
                           """).fetchone()
    document_topic, topics, document_similarities, topic_similarities = model

    logging.info("Preparing document-topic distributions...")
    document_topic = pd.read_json(document_topic, orient="index")

    logging.info("Preparing topics...")
    topics = pd.read_json(topics)
    topics.index = ["Topic {}".format(n) for n in topics.index]
    topics.columns = ["Word {}".format(n) for n in topics.columns]

    logging.info("Preparing topic similarity matrix...")
    topic_similarities = pd.read_json(topic_similarities)

    logging.info("Preparing document similarity matrix...")
    document_similarities = pd.read_json(document_similarities)
    return {"document-topic-distribution": document_topic,
            "topics": topics,
            "topic-similarities": topic_similarities,
            "document-similarities": document_similarities,
            "stopwords": json.loads(stopwords)}