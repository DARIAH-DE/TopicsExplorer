import json
import logging
import xml

import cophi
import lda
import numpy as np
import pandas as pd

from application import database
from application import utils


def wrapper():
    """Wrapper for the topic modeling workflow.
    """
    try:
        logging.info("Just started topic modeling.")
        data = utils.get_data("corpus",
                            "topics",
                            "iterations",
                            "stopwords",
                            "mfw")
        logging.info("Fetched user data...")
        database.insert_into("textfiles",
                            data["corpus"])
        logging.info("Inserted data into database.")

        # 1. Preprocess:
        dtm, token_freqs = preprocess(data)
        logging.info("Successfully preprocessed data.")
        database.insert_into("token_freqs",
                            json.dumps(token_freqs))
        # 2. Create model:
        model = create_model(dtm, data["topics"], data["iterations"])
        logging.info("Successfully created topic model.")
        # 3. Get model output:
        topics, descriptors, document_topic = get_model_output(model, dtm)
        logging.info("Got model output.")
        # 4. Calculate similarities:
        topic_similarities, document_similarities = get_similarities(document_topic)
        logging.info("Successfully calculated topic and document similarities.")

        data = {"document_topic": document_topic.to_json(orient="index", force_ascii=False),
                "topics": json.dumps(topics, ensure_ascii=False),
                "document_similarities": document_similarities.to_json(force_ascii=False),
                "topic_similarities": topic_similarities.to_json(force_ascii=False)}
        database.insert_into("model", data)
        logging.info("Successfully inserted data into database.")
        logging.info("Very nice, great success!")
    except xml.etree.ElementTree.ParseError as error:
        logging.error("ERROR: There is something wrong with your XML files.")
        logging.error("ERROR: {}".format(error))
        logging.error("Redirect to error page.")
    except UnicodeDecodeError:
        logging.error("ERROR: There is something wrong with your text files. "
                      "Are they UTF-8 encoded?")
        logging.error("Redirect to error page.")
    except Exception as error:
        logging.error("ERROR: {}".format(error))
        logging.error("Redirect to error page.")


def preprocess(data):
    """Preprocess text data.
    """
    # Constructing corpus:
    textfiles = database.select("textfiles")
    documents = utils.get_documents(textfiles)
    corpus = cophi.model.Corpus(documents)
    # Cleaning corpus:
    stopwords = utils.get_stopwords(data, corpus)
    hapax = corpus.hapax
    features = set(stopwords).union(set(hapax))
    logging.info("Cleaning corpus...")
    dtm = corpus.drop(corpus.dtm, features)
    # Save stopwords:
    database.insert_into("stopwords", json.dumps(stopwords))
    return dtm, corpus.num_tokens.tolist()


def create_model(dtm, topics, iterations):
    """Create a topic model.
    """
    logging.info("Creating topic model...")
    model = lda.LDA(n_topics=topics,
                    n_iter=iterations)
    model.fit(dtm.values)
    return model


def get_model_output(model, dtm):
    """Get topics and distributions from topic model.
    """
    logging.info("Fetching model output...")
    # Topics and their descriptors:
    topics = list(utils.get_topics(model, dtm.columns))
    descriptors = list(utils.get_topic_descriptors(topics))
    # Document-topic distribution:
    document_topic = utils.get_document_topic(model, dtm.index, descriptors)
    return topics, descriptors, document_topic


def get_similarities(document_topic):
    """Calculate similarities between vectors.
    """
    logging.info("Calculating topic similarities...")
    topics = utils.get_cosine(document_topic.values, document_topic.columns)
    logging.info("Calculating document similarites...")
    documents = utils.get_cosine(document_topic.T.values, document_topic.index)
    return topics, documents
