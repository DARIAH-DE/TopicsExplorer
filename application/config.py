import pathlib
import sys
import flask
import tempfile

def create_app(**kwargs):
    """
    Creates a Flask app and temporary folders. If the scripts were frozen with
    PyInstaller, the paths to the template and static folder are adjusted
    accordingly.
    """
    tempdir = tempfile.gettempdir()
    dumpdir = pathlib.Path(tempdir, 'topicsexplorerdump')
    archivedir = pathlib.Path(tempdir, 'topicsexplorerdata')
    dumpdir.mkdir(exist_ok=True)
    archivedir.mkdir(exist_ok=True)
    
    if getattr(sys, 'frozen', False):
        root = pathlib.Path(sys._MEIPASS)
        app = flask.Flask(import_name=__name__,
                          template_folder=str(pathlib.Path(root, 'templates')),
                          static_folder=str(pathlib.Path(root, 'static')),
                          **kwargs)
    else:
        app = flask.Flask(import_name=__name__, **kwargs)
    return app, str(dumpdir), str(archivedir)
