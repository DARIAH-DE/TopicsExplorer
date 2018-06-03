#!/usr/bin/env python3

import application
import pathlib
import tempfile
import pytest


@pytest.fixture
def app():
    app, _, _ = application.config.create_app()
    return app

@pytest.fixture
def dumpdir():
    _, dumpdir, _ = application.config.create_app()
    return dumpdir

@pytest.fixture
def archivedir():
    _, _, archivedir = application.config.create_app()
    return archivedir


def test_temporary_folders(dumpdir, archivedir):
    tempdir = tempfile.gettempdir()
    correct_dumpdir = str(pathlib.Path(tempdir, "topicsexplorerdump"))
    correct_archivedir = str(pathlib.Path(tempdir, "topicsexplorerdata"))

    assert dumpdir == correct_dumpdir
    assert archivedir == correct_archivedir

def test_flask_configuration(app):
    cwd = pathlib.Path.cwd()
    assert app.config["DEBUG"] == False
    assert app.import_name == "application.config"
    assert app.template_folder == "templates"
    assert app.static_folder == str(pathlib.Path(cwd, "application", "static"))
    
def test_pyinstaller(app):
    """
    todo: test `if getattr(sys, "frozen", False)` part
    """
    pass
