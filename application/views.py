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


# Initialize logging with logfile in tempdir:
utils.init_logging(logging.INFO)

# Initialize Flask application:
web = utils.init_app("topicsexplorer")


@web.route("/")
def index():
    """Home page.
    """
    logging.debug("Calling home page endpoint...")
    if "process" in globals() and process.is_alive():
        logging.info("Terminating topic modeling process...")
        process.terminate()
    # Initialize SQLite database:
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


@web.route("/error")
def error():
    """Error page.
    """
    with utils.LOGFILE.open("r", encoding="utf-8") as logfile:
        log = logfile.read().split("\n")[-20:]
        return flask.render_template("error.html",
                                     reset=True,
                                     log="\n".join(log),
                                     tempdir=utils.TEMPDIR)


@web.route("/modeling", methods=["POST"])
def modeling():
    """Modeling page.
    """
    logging.debug("Calling modeling page endpoint...")
    # Must be global to use anywhere:
    global start
    global process
    start = time.time()
    process = multiprocessing.Process(target=workflow.wrapper)
    logging.info("Initializing topic modeling process...")
    process.start()
    logging.info("Started topic modeling process.")
    logging.debug("Rendering modeling page template...")
    return flask.render_template("modeling.html",
                                 abort=True)


@web.route("/overview-topics")
def overview_topics():
    """Topics overview page.
    """
    logging.debug("Calling topics overview page endpoint...")
    logging.info("Get document-topic distributions...")
    response = get_document_topic_distributions()
    document_topic = pd.read_json(response, orient="index")

    logging.info("Get token frequencies...")
    response = get_token_frequencies()
    token_freqs = json.loads(response)

    logging.info("Add frequencies to weights...")
    document_topic = document_topic.multiply(token_freqs, axis=0)

    logging.info("Sum the weights...")
    dominance = document_topic.sum(axis=0)

    logging.info("Scale weights...")
    proportions = utils.scale(dominance)
    proportions = pd.Series(proportions, index=dominance.index)
    proportions = proportions.sort_values(ascending=False)

    # Convert pandas.Series to a 2-D array:
    proportions = list(utils.series2array(proportions))

    corpus_size = get_corpus_size()
    number_topics = get_number_of_topics()
    logging.debug("Rendering topics overview template...")
    return flask.render_template("overview-topics.html",
                                 current="topics",
                                 help=True,
                                 reset=True,
                                 topics=True,
                                 documents=True,
                                 document_topic_distributions=True,
                                 parameters=True,
                                 export_data=True,
                                 proportions=proportions,
                                 corpus_size=corpus_size,
                                 number_topics=number_topics)


@web.route("/overview-documents")
def overview_documents():
    """Documents overview page.
    """
    logging.debug("Calling documents overview page endpoint...")
    sizes = pd.DataFrame(get_textfile_sizes(), columns=["title", "size"])

    proportions = utils.scale(sizes["size"])
    proportions = pd.Series(proportions, index=sizes["title"])
    proportions = proportions.sort_values(ascending=False)

    # Convert pandas.Series to a 2-D array:
    proportions = list(utils.series2array(proportions))

    corpus_size = get_corpus_size()
    return flask.render_template("overview-documents.html",
                                 current="documents",
                                 help=True,
                                 reset=True,
                                 topics=True,
                                 documents=True,
                                 document_topic_distributions=True,
                                 parameters=True,
                                 export_data=True,
                                 proportions=proportions,
                                 corpus_size=corpus_size)


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
                                 parameters=True,
                                 export_data=True)


@web.route("/topics/<topic>")
def topics(topic):
    """Topic page.
    """
    logging.debug("Calling topic page endpoint...")
    logging.info("Get topics...")
    topics = json.loads(get_topics())
    logging.info("Get document-topic distributions...")
    document_topic = pd.read_json(get_document_topic_distributions(), orient="index")
    logging.info("Get topic similarity matrix...")
    topic_similarites = pd.read_json(get_topic_similarities())

    logging.info("Get related documents...")
    related_docs = document_topic[topic].sort_values(ascending=False)[:10]
    related_docs_proportions = utils.scale(related_docs, minimum=70)
    related_docs_proportions = pd.Series(related_docs_proportions, index=related_docs.index)
    related_docs_proportions = related_docs_proportions.sort_values(ascending=False)

    # Convert pandas.Series to a 2-D array:
    related_docs_proportions = list(utils.series2array(related_docs_proportions))

    logging.info("Get related words...")
    related_words = topics[topic][:15]

    logging.info("Get similar topics...")
    similar_topics = topic_similarites[topic].sort_values(ascending=False)[1:4]
    logging.debug("Rendering topic page template...")
    return flask.render_template("detail-topic.html",
                                 help=True,
                                 reset=True,
                                 topics=True,
                                 documents=True,
                                 document_topic_distributions=True,
                                 parameters=True,
                                 export_data=True,
                                 topic=topic,
                                 similar_topics=similar_topics.index,
                                 related_words=related_words,
                                 related_documents=related_docs_proportions)


@web.route("/documents/<title>")
def documents(title):
    """Document page.
    """
    logging.debug("Calling document page endpoint...")
    logging.info("Get textfiles...")
    text = get_textfile(title)
    logging.info("Get document-topics distributions...")
    document_topic = pd.read_json(get_document_topic_distributions(), orient="index")
    logging.info("Get document similarity matrix...")
    document_similarites = pd.read_json(get_document_similarities())

    logging.info("Get related topics...")
    related_topics = document_topic.loc[title].sort_values(ascending=False) * 100
    distribution = list(related_topics.to_dict().items())

    logging.info("Get similar documents...")
    similar_docs = document_similarites[title].sort_values(ascending=False)[1:4]

    logging.debug("Use only the first 10000 characters (or less) from document...")
    text = text if len(text) < 10000 else "{}... This was an excerpt of the original text.".format(text[:10000])

    logging.debug("Split paragraphs...")
    text = text.split("\n\n")

    n = get_number_of_topics()
    top_topics = ["{} most relevant".format(n) if int(n) >= 10 else n,
                  "Top {}".format(n)]
    logging.debug("Rendering document page template...")
    return flask.render_template("detail-document.html",
                                 help=True,
                                 reset=True,
                                 topics=True,
                                 documents=True,
                                 document_topic_distributions=True,
                                 parameters=True,
                                 export_data=True,
                                 title=title,
                                 text=text,
                                 distribution=distribution,
                                 similar_documents=similar_docs.index,
                                 related_topics=related_topics.index,
                                 top_topics=top_topics)


@web.route("/parameters")
def parameters():
    """Paramter page.
    """
    logging.debug("Calling parameters page endpoint...")
    logging.info("Get parameters...")
    data = json.loads(get_parameters())[0]
    info = json.loads(data)
    logging.debug("Rendering parameters page template...")
    return flask.render_template("overview-parameters.html",
                                 current="parameters",
                                 parameters=True,
                                 help=True,
                                 reset=True,
                                 topics=True,
                                 documents=True,
                                 document_topic_distributions=True,
                                 export_data=True,
                                 **info)


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


@web.route("/api/parameters")
def get_parameters():
    """Model parameters.
    """
    return json.dumps(database.select("parameters"))


@web.route("/api/textfile-sizes")
def get_textfile_sizes():
    """Textfile sizes.
    """
    return database.select("textfile_sizes")


@web.route("/api/corpus-size")
def get_corpus_size():
    """Corpus size.
    """
    return str(len(get_textfile_sizes()))


@web.route("/api/number-topics")
def get_number_of_topics():
    """Number of topics.
    """
    return str(len(json.loads(get_topics())))


@web.route("/export/<filename>")
def export(filename):
    """Data archive.
    """
    if "topicsexplorer-data.zip" in {filename}:
        utils.export_data()
    path = Path(utils.TEMPDIR, filename)
    return flask.send_file(filename_or_fp=str(path))


@web.errorhandler(werkzeug.exceptions.HTTPException)
def handle_http_exception(e):
    """Handle errors..
    """
    return error()

for code in werkzeug.exceptions.default_exceptions:
    web.errorhandler(code)(handle_http_exception)


@web.after_request
def add_header(r):
    """Clear cache after request.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers["Cache-Control"] = "public, max-age=0"
    return r


@web.teardown_appcontext
def close_connection(exception):
    """Close connection to SQLite database.
    """
    db = getattr(flask.g, "_database", None)
    if db is not None:
        db.close()
