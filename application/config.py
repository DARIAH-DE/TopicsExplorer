import sys

import flask

def create_app(name, **kwargs):
    """Create Flask app.
    """
    if getattr(sys, "frozen", False):
        # True, if script was frozen with PyInstaller
        template_folder = pathlib.Path(sys._MEIPASS, "templates")
        static_folder = pathlib.Path(sys._MEIPASS, "static")
        app = flask.Flask(name,
                          template_folder,
                          static_folder,
                          **kwargs)
    else:
        app = flask.Flask(name,
                          **kwargs)
    return app
