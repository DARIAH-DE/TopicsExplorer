import json
import logging
import multiprocessing
from pathlib import Path

import flask

import database
import utils
import workflow


web, process = utils.init_app("topicsexplorer")

@web.route("/")
def index():
    """Home page.
    """
    if process.is_alive():
        process.terminate()
    utils.init_logging(logging.DEBUG)
    utils.init_db(web)
    return flask.render_template("index.html",
                                 help=True)

@web.route("/help")
def help():
    """Help page.
    """
    return flask.render_template("help.html",
                                 go_back=True)

@web.route("/modeling", methods=["POST"])
def modeling():
    """Modeling page.
    """
    process = multiprocessing.Process(target=workflow.wrapper)
    process.start()
    return flask.render_template("modeling.html",
                                 help=True,
                                 abort=True)

@web.route("/overview-topics")
def overview_topics():
    presence = list(utils.get_topic_presence())
    return flask.render_template("overview-topics.html",
                                 current="topics",
                                 help=True,
                                 reset=True,
                                 topics=True,
                                 documents=True,
                                 document_topic_distributions=True,
                                 export_data=True,
                                 presence=presence)

@web.route("/overview-documents")
def overview_documents():
    titles = sorted(database.select("titles"))
    return flask.render_template("overview-documents.html",
                                 current="documents",
                                 help=True,
                                 reset=True,
                                 topics=True,
                                 documents=True,
                                 document_topic_distributions=True,
                                 export_data=True,
                                 titles=titles)

@web.route("/document-topic-distribution")
def document_topic_distributions():
    return flask.render_template("document-topic-distribution.html",
                                 current="document-topic-distributions",
                                 help=True,
                                 reset=True,
                                 topics=True,
                                 documents=True,
                                 document_topic_distributions=True,
                                 export_data=True)

@web.route("/topics/<topic>")
def topics(topic):
    document_topic, topics, topic_similarites = database.select("topic-overview")
    # Get related documents:
    related_docs = document_topic[topic].sort_values(ascending=False)[:30]
    related_docs = list(related_docs.index)

    # Get related words:
    loc = document_topic.columns.get_loc(topic)
    related_words = topics[loc][:20]

    # Get similar topics:
    similar_topics = topic_similarites[topic].sort_values(ascending=False)[1:4]
    similar_topics = list(similar_topics.index)
    return flask.render_template("detail-topic.html",
                                 current="topics",
                                 help=True,
                                 reset=True,
                                 topics=True,
                                 documents=True,
                                 document_topic_distributions=True,
                                 export_data=True,
                                 topic=topic,
                                 similar_topics=similar_topics,
                                 related_words=related_words,
                                 related_documents=related_docs)

@web.route("/documents/<title>")
def documents(title):
    text, document_topic, topics, document_similarites = database.select("document-overview", title=title)

    # Get related topics:
    related_topics = document_topic[title].sort_values(ascending=False) * 100
    distribution = list(related_topics.to_dict().items())
    related_topics = related_topics[:20].index

    # Get similar documents:
    similar_docs = document_similarites[title].sort_values(ascending=False)[1:4]
    similar_docs = list(similar_docs.index)
    return flask.render_template("detail-document.html",
                                 current="documents",
                                 help=True,
                                 reset=True,
                                 topics=True,
                                 documents=True,
                                 document_topic_distributions=True,
                                 export_data=True,
                                 title=title,
                                 text=text[:5000] + "...",
                                 distribution=distribution,
                                 similar_documents=similar_docs,
                                 related_topics=related_topics)

# API STUFF

@web.route("/api/status")
def status():
    """API: Current modeling status.
    """
    return utils.get_status()

@web.route("/api/document-topic")
def document_topic_overview():
    document_topic = database.select("document-topic")
    x = list()
    for key, value in document_topic.to_dict().items():
        x.append({"name": key, "data": [{"x": title, "y": wert} for title, wert in value.items()]})
    return json.dumps(x)



@web.route("/export/<filename>")
def export(filename):
    utils.export_data()
    path = Path(utils.TEMPDIR, filename)
    return flask.send_file(filename_or_fp=str(path))

@web.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers["Cache-Control"] = "public, max-age=0"
    return r

@web.teardown_appcontext
def close_connection(exception):
    db = getattr(flask.g, "_database", None)
    if db is not None:
        db.close()


if __name__ == "__main__":
    web.run(debug=True)