import logging
import multiprocessing
import utils
import workflow
import database

import flask


app, process = utils.init_app("topicsexplorer")

@app.route("/")
def index():
    """Home page.
    """
    if process.is_alive():
        process.terminate()
    utils.init_logging(logging.DEBUG)
    utils.init_db(app)
    return flask.render_template("index.html")

@app.route("/help")
def help():
    """Help page.
    """
    return flask.render_template("help.html")

@app.route("/api/status")
def status():
    """API: Current modeling status.
    """
    return utils.get_status()

@app.route("/modeling", methods=["POST"])
def modeling():
    process = multiprocessing.Process(target=workflow.wrapper)
    process.start()
    return flask.render_template("modeling.html")

@app.route("/topic-presence")
def topic_presence():
    presence = list(utils.get_topic_presence())
    return flask.render_template("topic-presence.html", presence=presence)

@app.route("/topics/<topic>")
def topics(topic):
    doc_topic, topics, topic_sim = database.select("topic-overview")
    # Get related documents:
    related_docs = doc_topic[topic].sort_values(ascending=False)[:30]
    related_docs = list(related_docs.index)

    # Get related words:
    loc = doc_topic.columns.get_loc(topic)
    related_words = topics[loc][:20]

    # Get similar topics:
    similar_topics = topic_sim[topic].sort_values(ascending=False)[1:4]
    similar_topics = list(similar_topics.index)
    return flask.render_template("topic.html",
                                 topic=topic,
                                 similar_topics=similar_topics,
                                 related_words=related_words,
                                 related_documents=related_docs)

@app.route("/documents/<title>")
def documents(title):
    text, doc_topic, topics, doc_sim = database.select("document-overview", title=title)
    # TODO: how to deal with this?
    text = text.split("\n\n")

    # Get related topics:
    related_topics = doc_topic[title].sort_values(ascending=False) * 100
    distribution = list(related_topics.to_dict().items())
    related_topics = related_topics[:20].index

    # Get similar documents:
    similar_docs = doc_sim[title].sort_values(ascending=False)[1:4]
    similar_docs = list(similar_docs.index)
    return flask.render_template("document.html",
                                 title=title,
                                 text=text,
                                 distribution=distribution,
                                 similar_documents=similar_docs,
                                 related_topics=related_topics)

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