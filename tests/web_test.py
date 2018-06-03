#!/usr/bin/env python3

import pytest
import tempfile
import application
import pathlib
import io

@pytest.fixture
def app():
    return application.web.app

@pytest.fixture
def client(app):
    return app.test_client()


def test_index(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Easy Topic Modeling" in resp.data

def test_help(client):
    resp = client.get("/help")
    assert resp.status_code == 200
    assert b"Help on Topics Explorer" in resp.data

def test_modeling(client):
    resp = client.post("/modeling")
    assert resp.status_code == 200
    assert b"This may take a while..." in resp.data

def test_model(client):
    tempdir = pathlib.Path(tempfile.gettempdir(), "topicsexplorerdump")
    filepath = pathlib.Path(tempdir, "data.pickle")
    parameter = pathlib.Path(tempdir, "parameter.csv")
    topics = pathlib.Path(tempdir, "topics.csv")
    data = {"foo": "bar"}
    application.utils.compress(data, str(filepath))
    with parameter.open("w", encoding="utf-8") as file:
        file.write("foo;bar\nfoo;bar")
    with topics.open("w", encoding="utf-8") as file:
        file.write("foo;bar\nfoo;bar")
    resp = client.get("/model")
    assert resp.status_code == 200
    assert b"Inspecting the topic model" in resp.data
    application.utils.unlink_content(tempdir)
