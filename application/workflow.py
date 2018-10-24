import utils
import lda
import database
import json
import cophi
import numpy as np
import pandas as pd

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
    topics, descriptors, doc_topic = get_model_output(model, dtm)
    # 4. Calculate similarities:
    topic_sim, doc_sim = get_similarities(doc_topic)

    data = {"doc_topic": doc_topic.to_json(force_ascii=False),
            "topics": json.dumps(topics, ensure_ascii=False),
            "doc_sim": doc_sim.to_json(force_ascii=False),
            "topic_sim": topic_sim.to_json(force_ascii=False)}
    database.insert_into("model", data)


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
    doc_topic = utils.get_doc_topic(model, dtm.index, descriptors)
    return topics, descriptors, doc_topic


def get_similarities(doc_topic):
    """Calculate similarities between vectors.
    """
    topics = utils.get_cosine(doc_topic.values, doc_topic.columns)
    documents = utils.get_cosine(doc_topic.T.values, doc_topic.index)
    return topics, documents
