#!/usr/bin/env python3

import operator
import pathlib
import logging
import sqlite3
import multiprocessing

import flask
import pandas as pd
import numpy as np
import lda

import utils


app = flask.Flask("topicsexplorer")
global process
process  = multiprocessing.Process()


@app.route("/")
def index():
    """Render home page.

    Note:
        Calling this function will drop all tables
            in the database – if any.
    """
    # Kill modeling process, if any:
    if process.is_alive():
        logging.info("Restarting topic modeling...")
        process.terminate()
    # Initialize logging:
    utils.init_logging()
    # Initialize database and create tables:
    utils.init_db(app)
    # Render home page:
    return flask.render_template("index.html")


@app.route("/modeling", methods=["POST"])
def modeling():
    """Create topic model and render status page.
    """
    process = multiprocessing.Process(target=workflow)
    process.start()
    return flask.render_template("modeling.html")
    return flask.render_template("topic-presence.html", presence=relevance)

def get_topic_descriptors(topics):
    for topic in topics:
        yield ", ".join(topic[:3])


def workflow():
    # Get input data:
    data = utils.get_data("corpus",
                          "topics",
                          "iterations",
                          "stopwords",
                          "mfw")
    # Insert data into textfiles table:
    utils.insert_into_textfiles(data["corpus"])
    # Preprocess data:
    dtm, vocabulary, titles, sizes = utils.preprocess(data)
    # Initialize topic model:
    model = lda.LDA(n_topics=data["topics"], n_iter=data["iterations"])
    model.fit(dtm)
    # Get topics generator:
    topics = utils.get_topics(model, vocabulary)
    # Call it:
    topics = list(topics)
    # Get document-topic distribution:
    # (Rows -> documents, columns -> topics)
    doc_topic = model.doc_topic_
    # Get normalized document-topic distribution:
    doc_topic_n = utils.normalize(doc_topic, sizes)

    topic_weights = doc_topic_n.sum(axis=0)
    topic_weights_s = utils.scale(topic_weights)
    descriptors = list(get_topic_descriptors(topics))
    relevance = pd.Series(topic_weights_s, index=descriptors).to_dict().items()
    relevance = sorted(relevance, key=operator.itemgetter(1), reverse=True)


@app.after_request
def add_header(r):
    """Clear cache after a request.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers["Cache-Control"] = "public, max-age=0"
    return r


@app.route("/help")
def help():
    cur = get_db(utils.DATABASE_URI).cursor()
    res = cur.execute("SELECT title FROM textfiles;")
    print(res.fetchall())
    return " ".join(res.fetchall())
    #return flask.render_template("help.html")






@app.route("/topic-presence/<topic>")
def topic_presence(topic):
    print(topic)
    return flask.render_template("topic-presence.html")


@app.route("/topics")
def topics():
    return flask.render_template("topics.html")


@app.route("/documents")
def documents():
    return flask.render_template("documents.html")


@app.route("/api/status")
def status():
    return utils.get_status()


@app.route("/api/textfiles/<id>", methods=["GET"])
def get_textfile():
    cursor = get_db("database.db").cursor()
    res = cur.execute("SELECT * FROM textfiles;")


def get_db(uri):
    db = getattr(flask.g, "_database", None)
    if db is None:
        db = flask.g._database = sqlite3.connect(uri)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(flask.g, '_database', None)
    if db is not None:
        db.close()


if __name__ == "__main__":
    app.run(debug=True)
    


"""
@app.route('/', methods=['GET', 'POST'])
def index():
    search = MusicSearchForm(request.form)
    if request.method == 'POST':
        return search_results(search)
 
    return render_template('index.html', form=search)
 
 
@app.route('/results')
def search_results(search):
    results = []
    search_string = search.data['search']
 
    if search.data['search'] == '':
        qry = db_session.query(Album)
        results = qry.all()
 
    if not results:
        flash('No results found!')
        return redirect('/')
    else:
        # display results
        return render_template('results.html', results=results)
"""
