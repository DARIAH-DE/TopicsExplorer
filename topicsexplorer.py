#!/usr/bin/env python3

import sys
import pathlib
import PyQt5.QtGui
import PyQt5.QtWidgets
import PyQt5.QtWebEngineWidgets
import PyQt5.QtCore

# If you want to freeze the application using PyInstaller, all of the
# dependencies have to be imported here, although needed in other modules.

# utils.py dependencies:
# import lzma
# import pickle
# import time
# import regex as re
# import logging
# import bokeh.plotting
# import bokeh.models
# import bokeh.layouts
# import lda
# import threading
# import queue

# webapp.py dependencies:
# import time
# import shutil
# import tempfile
# import dariah_topics
# import flask
# import pandas as pd
# import numpy as np
# import bokeh.embed
# import werkzeug.utils


PORT = 5000
ROOT_URL = 'http://localhost:{port}'.format(port=PORT)


class FlaskThread(PyQt5.QtCore.QThread):
    def __init__(self, application):
        PyQt5.QtCore.QThread.__init__(self)
        self.application = application

    def __del__(self):
        self.wait()

    def run(self):
        self.application.run(port=PORT)


def ProvideGui(application):
    """
    Opens a QtWebEngine window, runs the Flask application, and renders the
    index.html page.
    """
    title = 'Topics Explorer'
    icon = str(pathlib.Path('static', 'img', 'page_icon.png'))
    width = 1200
    height = 660

    qtapp = PyQt5.QtWidgets.QApplication(sys.argv)

    webapp = FlaskThread(application)
    webapp.start()

    qtapp.aboutToQuit.connect(webapp.terminate)

    webview = PyQt5.QtWebEngineWidgets.QWebEngineView()
    webview.resize(width, height)
    webview.setWindowTitle(title)
    webview.setWindowIcon(PyQt5.QtGui.QIcon(icon))

    webview.load(PyQt5.QtCore.QUrl(ROOT_URL))
    webview.show()

    return qtapp.exec_()


if __name__ == '__main__':
    from webapp import app
    sys.exit(ProvideGui(app))
