#!/usr/bin/env python3

import operator
import pathlib
import logging
import json
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

def get_topic_descriptors(topics):
    for topic in topics:
        yield ", ".join(topic[:3])


def workflow():
    """Topic modeling workflow
    """
    # Get input data:
    data = utils.get_data("corpus",
                          "topics",
                          "iterations",
                          "stopwords",
                          "mfw")
    # Insert documents into textfiles table:
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

    descriptors = list(get_topic_descriptors(topics))
    doc_topic = get_doc_topic(model, titles, descriptors)
    utils.insert_into_model(doc_topic, json.dumps(topics))


def get_doc_topic(model, titles, descriptors):
    doc_topic = pd.DataFrame(model.doc_topic_)
    doc_topic.index = titles
    doc_topic.columns = [descriptor.replace(", ", "-") for descriptor in descriptors]
    return doc_topic.to_json()

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



@app.route("/topic-presence")
def topic_presence():
    doc_topic = utils.select_doc_topic()
    doc_topic_n = doc_topic#utils.normalize(doc_topic, sizes)
    topic_weights = doc_topic_n.sum(axis=0)
    topic_weights_s = utils.scale(topic_weights)
    descriptors = list(get_topic_descriptors(topics))
    relevance = pd.Series(topic_weights_s, index=descriptors).to_dict().items()
    presence = sorted(relevance, key=operator.itemgetter(1), reverse=True)
    return flask.render_template("topic-presence.html", presence=presence)


@app.route("/topics/<topic>")
def topics(topic):
    doc_topic = utils.select_doc_topic()
    topicss = utils.select_topics()
    topic1 = doc_topic[topic].sort_values(ascending=False)[:30]
    related_docs = list(topic1.index)
    loc = doc_topic.columns.get_loc(topic)
    related_words = topicss[loc][:20]
    s = utils.scale(topic1)
    sim = pd.DataFrame(utils.get_similarities(doc_topic.values))[loc]
    sim.index = doc_topic.columns
    sim = sim.sort_values(ascending=False)[1:4]
    similar_topics = [", ".join(topicss[doc_topic.columns.get_loc(topic)][:3]) for topic in sim.index]

    return flask.render_template("topic.html", topic=", ".join(related_words[:3]), similar_topics=similar_topics, related_words=related_words, related_documents=related_docs)


@app.route("/documents/<title>")
def documents(title):
    doc_topic = utils.select_doc_topic().T
    text = utils.select_document(title).split("\n\n")
    topic1 = doc_topic[title].sort_values(ascending=False) * 100
    distribution = list(topic1.to_dict().items())
    loc = doc_topic.columns.get_loc(title)
    sim = pd.DataFrame(utils.get_similarities(doc_topic.values))[loc]
    sim.index = doc_topic.columns
    sim = sim.sort_values(ascending=False)[1:4]
    similar_topics = list(sim.index)
    related_topics = topic1[:20].index


    return flask.render_template("document.html", title=title, text=text, distribution=distribution, similar_documents=similar_topics, related_topics=related_topics)


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
