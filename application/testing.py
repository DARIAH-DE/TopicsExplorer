#!/usr/bin/env python3

import flask
import json
import config
import utils
import logging

app = config.create_app("topicsexplorer")
logfile = utils.setup_logging()

@app.route("/")
def index():
    return flask.render_template("index.html")

@app.route("/help")
def help():
    return flask.render_template("help.html")

@app.route("/modeling")
def modeling():
    return flask.render_template("modeling.html")

@app.route("/visualization")
def visualization():
    return flask.render_template("visualization.html")

@app.route("/status")
def status():
    """Stream log messages.
    """
    logging.info("Nice")
    return utils.get_status(logfile)


if __name__ == "__main__":
    app.run(debug=True)