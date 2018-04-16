import application
import sys
import pathlib
import PyQt5.QtGui
import PyQt5.QtWidgets
import PyQt5.QtWebEngineWidgets
import PyQt5.QtCore


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


def provide_gui(application):
    """
    Opens a QtWebEngine window, runs the Flask application, and renders the
    index.html page.
    """
    title = 'Topics Explorer'
    icon = str(pathlib.Path('application', 'static', 'img', 'page_icon.png'))
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


def run():
    sys.exit(provide_gui(application.web.app))
