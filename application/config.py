#!/usr/bin/env python3

import pathlib
import sys
import flask

def create_app(**kwargs):
    """
    Creates a Flask app and determines the path for bokeh resources. If the
    scripts were frozen with PyInstaller, the paths are adjusted accordingly.
    """
    if getattr(sys, 'frozen', False):
        root = pathlib.Path(sys._MEIPASS)
        app = flask.Flask(import_name=__name__,
                          template_folder=str(pathlib.Path(root, 'templates')),
                          static_folder=str(pathlib.Path(root, 'static')),
                          **kwargs)
        bokeh_resources = str(pathlib.Path(root, 'static', 'bokeh_templates'))
    else:
        app = flask.Flask(import_name=__name__, **kwargs)
        bokeh_resources = str(pathlib.Path('static', 'bokeh_templates'))
    return app, bokeh_resources
