import json
import logging
import xml

import cophi
import lda
import numpy as np
import pandas as pd

from application import database
from application import utils


def wrapper(data, app):
    """Wrapper for the topic modeling workflow.
    """
    with app.app_context():
        try:
            logging.info("Just started topic modeling workflow.")
            if len(data["corpus"]) < 10:
                raise ValueError("Your corpus is too small. "
                                    "Please select at least 10 text files.")
            logging.info("Fetched user data...")
    
            # 1. Preprocess:
            dtm, token_freqs, parameters = preprocess(data)
            logging.info("Successfully preprocessed data.")
            database.insert_into("token_freqs",
                                    json.dumps(token_freqs))
            # 2. Create model:
            model = create_model(dtm, data["topics"], data["iterations"])
            parameters["log_likelihood"] = int(model.loglikelihood())
            database.insert_into("parameters", json.dumps(parameters))
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
            logging.error("Redirect to error page...")
        except UnicodeDecodeError as error:
            logging.error("ERROR: There is something wrong with your text files. "
                            "Are they UTF-8 encoded?")
            logging.error("ERROR: {}".format(error))
            logging.error("Redirect to error page...")
        except Exception as error:
            logging.error("ERROR: {}".format(error))
            logging.error("Redirect to error page...")


def preprocess(data):
    """Preprocess text data.
    """
    # Constructing corpus:
    textfiles = database.select("textfiles")
    documents = utils.get_documents(textfiles)
    corpus = cophi.model.Corpus(documents)
    num_tokens = corpus.num_tokens
    database.update("textfiles", num_tokens.to_dict())
    # Get paramter:
    D, W = corpus.dtm.shape
    N = num_tokens.sum()
    # Cleaning corpus:
    stopwords = utils.get_stopwords(data, corpus)
    hapax = corpus.hapax
    features = set(stopwords).union(set(hapax))
    logging.info("Cleaning corpus...")
    dtm = corpus.drop(corpus.dtm, features)
    # Save stopwords:
    database.insert_into("stopwords", json.dumps(stopwords))
    # Save parameters:
    parameters = {"n_topics": int(data["topics"]),
                  "n_iterations": int(data["iterations"]),
                  "n_documents": int(D),
                  "n_stopwords": int(len(stopwords)),
                  "n_hapax": int(len(hapax)),
                  "n_tokens": int(N),
                  "n_types": int(W)}
    return dtm, num_tokens.tolist(), parameters


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
    topics = dict(utils.get_topics(model, dtm.columns))
    descriptors = list(topics.keys())
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
