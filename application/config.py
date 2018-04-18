import pathlib
import sys
import flask

def create_app(**kwargs):
    """
    Creates a Flask app. If the scripts were frozen with PyInstaller,
    the paths to the template and static folder are adjusted accordingly.
    """
    if getattr(sys, 'frozen', False):
        root = pathlib.Path(sys._MEIPASS)
        app = flask.Flask(import_name=__name__,
                          template_folder=str(pathlib.Path(root, 'templates')),
                          static_folder=str(pathlib.Path(root, 'static')),
                          **kwargs)
    else:
        app = flask.Flask(import_name=__name__, **kwargs)
    return app
