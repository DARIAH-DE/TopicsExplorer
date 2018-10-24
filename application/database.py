import flask
import sqlite3
import utils
import pandas as pd
import constants
import json



def get_db():
    """Create connection to SQLite database.
    """
    if "db" not in flask.g:
        flask.g.db = sqlite3.connect(constants.DATABASE)
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
    elif table in {"model"}:
        _insert_into_model(db, data)
    db.commit()
    close_db()


def _insert_into_model(db, data):
    """Insert data into model table.
    """
    db.execute("""
               INSERT INTO model (doc_topic, topics, doc_sim, topic_sim)
               VALUES(?, ?, ?, ?);
               """,
               [data["doc_topic"], data["topics"],
                data["doc_sim"], data["topic_sim"]])


def select(value, **kwargs):
    """Select values from database.
    """
    db = get_db()
    cursor = db.cursor()
    if value in {"textfiles"}:
        return _select_textfiles(cursor)
    elif value in {"doc_topic"}:
        return _select_doc_topic(cursor)
    elif value in {"topic-overview"}:
        return _select_topic_overview(cursor)
    elif value in {"document-overview"}:
        return _select_document_overview(cursor, **kwargs)


def _select_textfiles(cursor):
    """Select textfiles from database.
    """
    cursor.execute("""
                   SELECT title, content 
                   FROM textfiles;
                   """)
    return cursor.fetchall()


def _select_doc_topic(cursor):
    """Select document-topic matrix form database.
    """
    response = cursor.execute("""
                              SELECT doc_topic 
                              FROM model;
                              """).fetchone()[0]
    return pd.read_json(response)


def _select_topic_overview(cursor):
    """Select values for the topic overview page.
    """
    doc_topic, topics, topic_sim = cursor.execute("""
                                                  SELECT doc_topic, topics, topic_sim 
                                                  FROM model;
                                                  """).fetchone()
    return pd.read_json(doc_topic), json.loads(topics), pd.read_json(topic_sim)


def _select_document_overview(cursor, title):
    """Select values for the document overview page.
    """
    text = cursor.execute("""
                          SELECT content 
                          FROM textfiles
                          WHERE title is ?;
                          """, [title]).fetchone()[0]
    doc_topic, topics, doc_sim = cursor.execute("""
                                                SELECT doc_topic, topics, doc_sim 
                                                FROM model;
                                                """).fetchone()
    return text, pd.read_json(doc_topic).T, json.loads(topics), pd.read_json(doc_sim)
