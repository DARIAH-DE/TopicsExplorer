import datetime
import json
import logging
import multiprocessing
from pathlib import Path
import time

import flask
import pandas as pd
import werkzeug

from application import database
from application import utils
from application import workflow


utils.init_logging(logging.INFO)
web, process = utils.init_app("topicsexplorer")


@web.route("/")
def index():
    """Home page.
    """
    logging.debug("Calling home page endpoint...")
    if process.is_alive():
        logging.info("Terminating topic modeling process...")
        process.terminate()
    logging.debug("Initializing database...")
    # And drop tables, if any exist:
    utils.init_db(web)
    logging.debug("Rendering home page template...")
    return flask.render_template("index.html",
                                 help=True)


@web.route("/help")
def help():
    """Help page.
    """
    logging.debug("Rendering help page template...")
    return flask.render_template("help.html",
                                 go_back=True)


@web.route("/modeling", methods=["POST"])
def modeling():
    """Modeling page.
    """
    logging.debug("Calling modeling page endpoint...")
    # Must be global to use it in the other function:
    global start
    start = time.time()
    global process
    process = multiprocessing.Process(target=workflow.wrapper)
    logging.info("Initializing topic modeling process...")
    process.start()
    logging.debug("Rendering modeling page template...")
    return flask.render_template("modeling.html",
                                 reset=True,
                                 abort=True)


@web.route("/overview-topics")
def overview_topics():
    """Topics overview page.
    """
    logging.debug("Calling topics overview page endpoint...")
    # Get document-topic distributions:
    response = get_document_topic_distributions()
    document_topic = pd.read_json(response, orient="index").iloc[:, :50]

    # Get token frequencies:
    response = get_token_frequencies()
    token_freqs = json.loads(response)

    # Add frequencies to weights:
    document_topic = document_topic.multiply(token_freqs, axis=0)

    # Sum the weights:
    dominance = document_topic.sum(axis=0)

    # Scale them:
    proportions = utils.scale(dominance)
    proportions = pd.Series(proportions, index=dominance.index)
    proportions = proportions.sort_values(ascending=False)

    def series2array(s):
        for i, v in zip(s.index, s):
            yield [i, v]

    # Convert pandas.Series to a 2-D array:
    proportions = list(series2array(proportions))
    logging.debug("Rendering topics overview template...")
    return flask.render_template("overview-topics.html",
                                 current="topics",
                                 help=True,
                                 reset=True,
                                 topics=True,
                                 documents=True,
                                 document_topic_distributions=True,
                                 parameter=True,
                                 export_data=True,
                                 proportions=proportions)


@web.route("/overview-documents")
def overview_documents():
    """Documents overview page.
    """
    logging.debug("Calling documents overview page endpoint...")
    titles = get_textfile_titles()
    # Parse and sort them:
    titles = sorted(json.loads(titles))
    logging.debug("Rendering documents overview page template...")
    return flask.render_template("overview-documents.html",
                                 current="documents",
                                 help=True,
                                 reset=True,
                                 topics=True,
                                 documents=True,
                                 document_topic_distributions=True,
                                 parameter=True,
                                 export_data=True,
                                 titles=titles)


@web.route("/document-topic-distributions")
def document_topic_distributions():
    """Document-topic distributions page.
    """
    logging.debug("Calling document-topic distributions endpoint...")
    logging.debug("Rendering document-topic distributions page template...")
    return flask.render_template("document-topic-distributions.html",
                                 current="document-topic-distributions",
                                 help=True,
                                 reset=True,
                                 topics=True,
                                 documents=True,
                                 document_topic_distributions=True,
                                 parameter=True,
                                 export_data=True)


@web.route("/topics/<topic>")
def topics(topic):
    """Topic page.
    """
    logging.debug("Calling topic page endpoint...")
    # Get data:
    topics = json.loads(get_topics())
    document_topic = pd.read_json(get_document_topic_distributions(), orient="index")
    topic_similarites = pd.read_json(get_topic_similarities())

    # Get related documents:
    related_docs = document_topic[topic].sort_values(ascending=False)[:10]
    related_docs = list(related_docs.index)

    # Get related words:
    loc = document_topic.columns.get_loc(topic)
    related_words = topics[loc][:25]

    # Get similar topics:
    similar_topics = topic_similarites[topic].sort_values(ascending=False)[1:4]
    similar_topics = list(similar_topics.index)
    logging.debug("Rendering topic page template...")
    return flask.render_template("detail-topic.html",
                                 current="topics",
                                 help=True,
                                 reset=True,
                                 topics=True,
                                 documents=True,
                                 document_topic_distributions=True,
                                 parameter=True,
                                 export_data=True,
                                 topic=topic,
                                 similar_topics=similar_topics,
                                 related_words=related_words,
                                 related_documents=related_docs)


@web.route("/documents/<title>")
def documents(title):
    """Document page.
    """
    logging.debug("Calling document page endpoint...")
    # Get data:
    text = get_textfile(title)
    document_topic = pd.read_json(get_document_topic_distributions(), orient="index")
    document_similarites = pd.read_json(get_document_similarities())

    # Get related topics:
    related_topics = document_topic.loc[title].sort_values(ascending=False) * 100
    distribution = list(related_topics.to_dict().items())
    related_topics = list(related_topics[:20].index)

    # Get similar documents:
    similar_docs = document_similarites[title].sort_values(ascending=False)[1:4]
    similar_docs = list(similar_docs.index)

    # Use only the first 5000 characters, or less:
    text = text if len(text) < 5000 else "{}... To be continued.".format(text[:5000])

    # Split paragraphs:
    text = text.split("\n\n")
    logging.debug("Rendering document page template...")
    return flask.render_template("detail-document.html",
                                 current="documents",
                                 help=True,
                                 reset=True,
                                 topics=True,
                                 documents=True,
                                 document_topic_distributions=True,
                                 parameter=True,
                                 export_data=True,
                                 title=title,
                                 text=text,
                                 distribution=distribution,
                                 similar_documents=similar_docs,
                                 related_topics=related_topics)


@web.route("/parameter")
def parameter():
    return flask.render_template("overview-parameter.html",
                                 current="parameter",
                                 parameter=True,
                                 help=True,
                                 reset=True,
                                 topics=True,
                                 documents=True,
                                 document_topic_distributions=True,
                                 export_data=True)

# API endpoints:

@web.route("/api/status")
def get_status():
    """Current modeling status.
    """
    seconds = int(time.time() - start)
    elapsed_time = datetime.timedelta(seconds=seconds)
    with utils.LOGFILE.open("r", encoding="utf-8") as logfile:
        messages = logfile.readlines()
        message = messages[-1].strip()
        message = utils.format_logging(message)
        return "Elapsed time: {}<br>{}".format(elapsed_time, message)


@web.route("/api/document-topic-distributions")
def get_document_topic_distributions():
    """Document-topics distributions.
    """
    return database.select("document_topic_distributions")


@web.route("/api/topics")
def get_topics():
    """Topics.
    """
    return database.select("topics")


@web.route("/api/document-similarities")
def get_document_similarities():
    """Document similarity matrix.
    """
    return database.select("document_similarities")


@web.route("/api/topic-similarities")
def get_topic_similarities():
    """Topic similarity matrix.
    """
    return database.select("topic_similarities")


@web.route("/api/textfiles/<title>")
def get_textfile(title):
    """Textfiles.
    """
    return database.select("textfile", title=title)


@web.route("/api/textfiles/titles")
def get_textfile_titles():
    """Textfile titles.
    """
    return database.select("textfile_titles")


@web.route("/api/stopwords")
def get_stopwords():
    """Stopwords.
    """
    return database.select("stopwords")


@web.route("/api/token-frequencies")
def get_token_frequencies():
    """Token frequencies per document.
    """
    return database.select("token_freqs")


@web.route("/export/<filename>")
def export(filename):
    """Data archive.
    """
    utils.export_data()
    path = Path(utils.TEMPDIR, filename)
    return flask.send_file(filename_or_fp=str(path))


@web.route("/error")
def error():
    with utils.LOGFILE.open("r", encoding="utf-8") as logfile:
        log = logfile.read().split("\n")[-20:]
        return flask.render_template("error.html",
                                     reset=True,
                                     go_back=True,
                                     log="\n".join(log))


@web.errorhandler(werkzeug.exceptions.HTTPException)
def handle_http_exception(e):
    """Error page.
    """
    return error()

for code in werkzeug.exceptions.default_exceptions:
    web.errorhandler(code)(handle_http_exception)


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
