#!/usr/bin/env python3

import application.utils
import application.config
import pathlib
import time
import sys
import shutil
import logging
import tempfile
import dariah_topics
import flask
import pandas as pd
import numpy as np
import bokeh.plotting
import bokeh.embed
import werkzeug.utils


TEMPDIR = tempfile.mkdtemp()  # Storing logfile, dumping temporary data, etc.
app, bokeh_resources = application.config.create_app()  # Creating the app


@app.route('/')
def index():
    """
    Renders the main page. A warning pops up, if the machine is not
    connected to the internet.
    """
    if application.utils.is_connected():
        return flask.render_template('index.html')
    else:
        return flask.render_template('index.html', internet='warning')


@app.route('/help')
def help():
    """
    Renders the help page.
    """
    return flask.render_template('help.html')


@app.route('/modeling', methods=['POST'])
def modeling():
    """
    Streams the modeling page, printing useful information to screen.
    The generated data will be dumped into the tempdir (specified above).
    """
    def stream_template(template_name, **context):
        app.update_template_context(context)
        t = app.jinja_env.get_template(template_name)
        return t.stream(context)

    stream = flask.stream_with_context(modeling.create_model())
    return flask.Response(stream_template('modeling.html', info=stream))


@app.route('/model')
def model():
    """
    Loads the dumped data, deletes the tempdir, and renders the model page.
    """
    data = utils.load_data(TEMPDIR)
    shutil.rmtree(TEMPDIR)
    return flask.render_template('model.html', **data)


@app.after_request
def add_header(r):
    """
    Clears the cache after the request.
    """
    r.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    r.headers['Pragma'] = 'no-cache'
    r.headers['Expires'] = '0'
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r
