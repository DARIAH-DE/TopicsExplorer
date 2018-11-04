import json
import logging

import cophi
import lda
import numpy as np
import pandas as pd

import database
import utils


def wrapper():
    """Wrapper for the topic modeling workflow.
    """
    data = utils.get_data("corpus",
                          "topics",
                          "iterations",
                          "stopwords",
                          "mfw")
    database.insert_into("textfiles", data["corpus"])

    # 1. Preprocess:
    dtm = preprocess(data)
    # 2. Create model:
    model = create_model(dtm, data["topics"], data["iterations"])
    # 3. Get model output:
    topics, descriptors, document_topic = get_model_output(model, dtm)
    # 4. Calculate similarities:
    topic_similarities, document_similarities = get_similarities(document_topic)

    data = {"document_topic": document_topic.to_json(force_ascii=False),
            "topics": json.dumps(topics, ensure_ascii=False),
            "document_similarities": document_similarities.to_json(force_ascii=False),
            "topic_similarities": topic_similarities.to_json(force_ascii=False)}
    database.insert_into("model", data)
    logging.info("Done!")


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
    dtm = corpus.drop(corpus.dtm, features)
    # Save stopwords:
    database.insert_into("stopwords", json.dumps(stopwords))
    return dtm


def create_model(dtm, topics, iterations):
    """Create a topic model.
    """
    model = lda.LDA(n_topics=topics,
                    n_iter=iterations)
    model.fit(dtm.values)
    return model


def get_model_output(model, dtm):
    """Get topics and distributions from topic model.
    """
    # Topics and their descriptors:
    topics = list(utils.get_topics(model, dtm.columns))
    descriptors = list(utils.get_topic_descriptors(topics))
    # Document-topic distribution:
    document_topic = utils.get_document_topic(model, dtm.index, descriptors)
    return topics, descriptors, document_topic


def get_similarities(document_topic):
    """Calculate similarities between vectors.
    """
    topics = utils.get_cosine(document_topic.values, document_topic.columns)
    documents = utils.get_cosine(document_topic.T.values, document_topic.index)
    return topics, documents
