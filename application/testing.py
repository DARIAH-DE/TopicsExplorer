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


app, process = utils.init_app()


@app.route("/")
def index():
    if process.is_alive():
        process.terminate()
    utils.init_logging()
    utils.init_db(app)
    return flask.render_template("index.html")

@app.route("/modeling", methods=["POST"])
def modeling():
    process = multiprocessing.Process(target=utils.workflow)
    process.start()
    return flask.render_template("modeling.html")

@app.route("/help")
def help():
    return flask.render_template("help.html")

@app.route("/topic-presence")
def topic_presence():
    presence = list(utils.get_topic_presence())
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


    return flask.render_template("document.html", title=title, text=text[:4], distribution=distribution, similar_documents=similar_topics, related_topics=related_topics)

@app.route("/api/status")
def status():
    return utils.get_status()

@app.route("/api/textfiles/<id>", methods=["GET"])
def get_textfile():
    cursor = get_db("database.db").cursor()
    res = cur.execute("SELECT * FROM textfiles;")

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers["Cache-Control"] = "public, max-age=0"
    return r

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(flask.g, '_database', None)
    if db is not None:
        db.close()


if __name__ == "__main__":
    app.run(debug=True)