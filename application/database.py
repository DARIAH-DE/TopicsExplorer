import json
import sqlite3

import flask
import pandas as pd

import utils


def get_db():
    """Create connection to SQLite database.
    """
    if "db" not in flask.g:
        flask.g.db = sqlite3.connect(str(utils.DATABASE))
    return flask.g.db


def close_db(e=None):
    """Close connection to SQLite database.
    """
    db = flask.g.pop("db", None)
    if db is not None:
        db.close()


def _insert_into_textfiles(db, data):
    """Insert data into textfiles table.
    """
    for textfile in data:
        title, content = utils.load_textfile(textfile)
        db.execute("""
                   INSERT INTO textfiles (title, content) 
                   VALUES(?, ?);
                   """, [title, content])


def insert_into(table, data):
    """Insert data into database.
    """
    db = get_db()
    if table in {"textfiles"}:
        _insert_into_textfiles(db, data)
    elif table in {"stopwords"}:
        _insert_into_stopwords(db, data)
    elif table in {"model"}:
        _insert_into_model(db, data)
    db.commit()
    close_db()


def _insert_into_model(db, data):
    """Insert data into model table.
    """
    db.execute("""
               INSERT INTO model (document_topic, topics, document_similarities, topic_similarities)
               VALUES(?, ?, ?, ?);
               """,
               [data["document_topic"], data["topics"],
                data["document_similarities"], data["topic_similarities"]])


def _insert_into_stopwords(db, data):
    """Insert data into stopwords table.
    """
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
    elif value in {"titles"}:
        return _select_titles(cursor)
    elif value in {"document-topic"}:
        return _select_document_topic(cursor)
    elif value in {"topic-overview"}:
        return _select_topic_overview(cursor)
    elif value in {"document-overview"}:
        return _select_document_overview(cursor, **kwargs)
    elif value in {"model-output"}:
        return _select_model_output(cursor)


def _select_titles(cursor):
    """Select textfile titles from database.
    """
    cursor.execute("""
                   SELECT title 
                   FROM textfiles;
                   """)
    return [title[0] for title in cursor.fetchall()]


def _select_model_output(cursor):
    """Select model output from database.
    """
    stopwords = cursor.execute("""
                              SELECT content 
                              FROM stopwords;
                              """).fetchone()

    response = cursor.execute("""
                              SELECT document_topic, topics, document_similarities, topic_similarities 
                              FROM model;
                              """).fetchone()
    document_topic, topics, document_similarities, topic_similarities = response
    document_topic = pd.read_json(document_topic)
    document_topic.columns = [col.replace(",", "") for col in document_topic.columns]
    document_topic.index = [ix.replace(",", "") for ix in document_topic.index]

    topics = pd.read_json(topics)
    topics.index = ["Topic {}".format(n) for n in topics.index]
    topics.columns = ["Word {}".format(n) for n in topics.columns]

    topic_similarities = pd.read_json(topic_similarities)
    topic_similarities.columns = [col.replace(",", "") for col in topic_similarities.columns]
    topic_similarities.index = [ix.replace(",", "") for ix in topic_similarities.index]

    document_similarities = pd.read_json(document_similarities)
    document_similarities.columns = [col.replace(",", "") for col in document_similarities.columns]
    document_similarities.index = [ix.replace(",", "") for ix in document_similarities.index]
    return {"document-topic-distribution": document_topic,
            "topics": topics,
            "topic-similarites": topic_similarities,
            "document-similarites": document_similarities,
            "stopwords": json.loads(stopwords[0])}


def _select_textfiles(cursor):
    """Select textfiles from database.
    """
    cursor.execute("""
                   SELECT title, content 
                   FROM textfiles;
                   """)
    return cursor.fetchall()


def _select_document_topic(cursor):
    """Select document-topic matrix form database.
    """
    response = cursor.execute("""
                              SELECT document_topic 
                              FROM model;
                              """).fetchone()[0]
    return pd.read_json(response)


def _select_topic_overview(cursor):
    """Select values for the topic overview page.
    """
    response = cursor.execute("""
                              SELECT document_topic, topics, topic_similarities 
                              FROM model;
                              """).fetchone()
    document_topic, topics, topic_similarities = response
    return pd.read_json(document_topic), json.loads(topics), pd.read_json(topic_similarities)


def _select_document_overview(cursor, title):
    """Select values for the document overview page.
    """
    response = cursor.execute("""
                              SELECT document_topic, topics, document_similarities 
                              FROM model;
                              """).fetchone()
    document_topic, topics, document_similarities = response
    text = cursor.execute("""
                          SELECT content 
                          FROM textfiles
                          WHERE title is ?;
                          """, [title]).fetchone()[0]
    return text, pd.read_json(document_topic).T, json.loads(topics), pd.read_json(document_similarities)
