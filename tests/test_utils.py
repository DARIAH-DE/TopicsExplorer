import logging
from pathlib import Path
import sys
import xml
sys.path.insert(0, str(Path(".").absolute()))

import cophi
import numpy as np
import pytest

from application import utils


TEST_STRING = "very-nice-great-success"


def test_dead_process():
    process = utils.DeadProcess()
    assert process.is_alive() is False


def test_init_app():
    app, process = utils.init_app(TEST_STRING)
    assert app.name == TEST_STRING
    assert isinstance(process, utils.DeadProcess)
    assert process.is_alive() == False


def test_init_logging():
    # TODO
    pass


def test_init_db():
    # TODO
    pass


def test_format_logging():
    a = "n_documents: 1"
    b = "vocab_size: 1"
    c = "n_words: 1"
    d = "n_topics: 1"
    e = "n_iter: 1"
    f = "<1> log likelihood: 1"
    assert utils.format_logging(a) == "Number of documents: 1"
    assert utils.format_logging(b) == "Number of types: 1"
    assert utils.format_logging(c) == "Number of tokens: 1"
    assert utils.format_logging(d) == "Number of topics: 1"
    assert utils.format_logging(e) == "Initializing topic model..."
    assert utils.format_logging(f) == "Iteration 1"
    assert utils.format_logging(TEST_STRING) == TEST_STRING


def test_textfile():
    # TODO
    pass


def test_remove_markup():
    text = "<tag>{}</tag>".format(TEST_STRING)
    assert utils.remove_markup(text) == TEST_STRING
    with pytest.raises(xml.etree.ElementTree.ParseError):
        text = "<tag>{}</anothertag>".format(TEST_STRING)
        utils.remove_markup(text)

def test_get_documents():
    textfiles = [("A", "This is a document.")]
    documents = list(utils.get_documents(textfiles))
    for document in documents:
        assert document.title == "A"
        assert document.text == "This is a document."

def test_get_stopwords():
    # TODO
    pass

def test_get_data():
    # TODO
    pass

def test_get_topics():
    # TODO
    pass

def test_get_document_topic():
    # TODO
    pass

def test_get_cosine():
    matrix = np.array([[1, 2], [1, 3]])
    descriptors = ["A", "B"]
    similarites = utils.get_cosine(matrix, descriptors)
    assert similarites.sum().sum() == 3.9611613513818402

