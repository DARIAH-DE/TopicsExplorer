import logging
import sqlite3

import flask

from topicsexplorer import utils


def get_db():
    """Create connection to SQLite database."""
    logging.info("Connecting to database...")
    if "db" not in flask.g:
        flask.g.db = sqlite3.connect(str(utils.DATABASE))
    return flask.g.db


def close_db(e=None):
    """Close connection to SQLite database."""
    logging.info("Closing connection to database...")
    db = flask.g.pop("db", None)
    if db is not None:
        db.close()


def _insert_into_textfiles(db, data):
    for textfile in data:
        title, content = utils.load_textfile(textfile)
        if content:
            logging.info("Insert '{}' into database...".format(title))
            db.execute(
                "INSERT INTO textfiles (title, content) VALUES(?, ?);",
                [title, content],
            )


def _insert_into_token_freqs(db, data):
    logging.info("Insert token frequencies into database...")
    db.execute(
        "INSERT INTO token_freqs (content) VALUES(?);",
        [data],
    )


def insert_into(table, data):
    """Insert data into database."""
    db = get_db()
    if table in {"textfiles"}:
        _insert_into_textfiles(db, data)
    elif table in {"token_freqs"}:
        _insert_into_token_freqs(db, data)
    elif table in {"stopwords"}:
        _insert_into_stopwords(db, data)
    elif table in {"model"}:
        _insert_into_model(db, data)
    elif table in {"parameters"}:
        _insert_into_parameters(db, data)
    db.commit()
    close_db()


def update(table, data):
    """Update table in database."""
    db = get_db()
    if table in {"textfiles"}:
        _update_textfile_sizes(db, data)
    db.commit()
    close_db()


def _update_textfile_sizes(db, data):
    logging.info("Update textfile sizes in database...")
    for title, size in data.items():
        db.execute(
            "UPDATE textfiles SET size = ? WHERE title = ?;",
            [size, title],
        )


def _insert_into_parameters(db, data):
    logging.info("Insert parameters into database...")
    db.execute(
        "INSERT INTO parameters (content) VALUES(?);",
        [data],
    )


def _insert_into_model(db, data):
    logging.info("Insert topic model output into database...")
    db.execute(
        "INSERT INTO model (document_topic, topics, document_similarities, topic_similarities) VALUES(?, ?, ?, ?);",
        [
            data["document_topic"],
            data["topics"],
            data["document_similarities"],
            data["topic_similarities"],
        ],
    )


def _insert_into_stopwords(db, data):
    logging.info("Insert stopwords into database...")
    db.execute(
        "INSERT INTO stopwords (content) VALUES(?);",
        [data],
    )


def select(value, **kwargs):
    """Select values from database."""
    db = get_db()
    cursor = db.cursor()
    if value in {"textfiles"}:
        return _select_textfiles(cursor)
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
    elif value in {"parameters"}:
        return _select_parameters(cursor)
    elif value in {"textfile_sizes"}:
        return _select_textfile_sizes(cursor)


def _select_textfile_sizes(cursor):
    logging.info("Select textfile sizes from database...")
    return cursor.execute("SELECT title, size FROM textfiles;").fetchall()


def _select_parameters(cursor):
    logging.info("Select parameters from database...")
    return cursor.execute("SELECT content FROM parameters;").fetchone()


def _select_stopwords(cursor):
    logging.info("Select stopwords from database...")
    return cursor.execute("SELECT content FROM stopwords;").fetchone()[0]


def _select_document_similarities(cursor):
    logging.info("Select document similarity matrix from database...")
    return cursor.execute("SELECT document_similarities FROM model;").fetchone()[0]


def _select_topic_similarities(cursor):
    logging.info("Select topic similarity matrix from database...")
    return cursor.execute("SELECT topic_similarities FROM model;").fetchone()[0]


def _select_token_freqs(cursor):
    logging.info("Select token frequencies from database...")
    return cursor.execute("SELECT content FROM token_freqs;").fetchone()[0]


def _select_textfiles(cursor):
    logging.info("Select textfiles from database...")
    return cursor.execute("SELECT title, content FROM textfiles;").fetchall()


def _select_document_topic_distributions(cursor):
    logging.info("Select document-topic distributions from database...")
    return cursor.execute("SELECT document_topic FROM model;").fetchone()[0]


def _select_topics(cursor):
    logging.info("Select topics from database...")
    return cursor.execute("SELECT topics FROM model;").fetchone()[0]


def _select_textfile(cursor, title):
    logging.info("Select '{}' from database...".format(title))
    return cursor.execute(
        "SELECT content FROM textfiles WHERE title = ?;",
        [title],
    ).fetchone()[0]


def _select_data_export(cursor):
    stopwords = _select_stopwords(cursor)

    logging.info("Select model output from database...")
    model = cursor.execute(
        "SELECT document_topic, topics, document_similarities, topic_similarities FROM model;"
    ).fetchone()
    return model, stopwords
