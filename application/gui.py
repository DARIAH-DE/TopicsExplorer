import application
import pathlib
import sys
import PyQt5.QtGui
import PyQt5.QtWidgets
import PyQt5.QtWebEngineWidgets
import PyQt5.QtCore


if hasattr(PyQt5.QtCore.Qt, 'AA_EnableHighDpiScaling'):
    PyQt5.QtWidgets.QApplication.setAttribute(PyQt5.QtCore.Qt.AA_EnableHighDpiScaling, True)
 
if hasattr(PyQt5.QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    PyQt5.QtWidgets.QApplication.setAttribute(PyQt5.QtCore.Qt.AA_UseHighDpiPixmaps, True)

class ApplicationThread(PyQt5.QtCore.QThread):
    def __init__(self, application, port=5000):
        super(ApplicationThread, self).__init__()
        self.application = application
        self.port = port

    def __del__(self):
        self.wait()

    def run(self):
        self.application.run(port=self.port, threaded=True)

"""
# This part allows you to open external links in the standard browser,
# but has been discarded because dead links should be avoided in the 
# application.

class WebPage(PyQt5.QtWebEngineWidgets.QWebEnginePage):
    def __init__(self, root_url):
        super(WebPage, self).__init__()
        self.root_url = root_url

    def home(self):
        self.load(PyQt5.QtCore.QUrl(self.root_url))

    def acceptNavigationRequest(self, url, kind, is_main_frame):
        ready_url = url.toEncoded().data().decode()
        is_clicked = kind == self.NavigationTypeLinkClicked

        if is_clicked and (self.root_url not in ready_url):
            PyQt5.QtGui.QDesktopServices.openUrl(url)
            return False
        return super(WebPage, self).acceptNavigationRequest(url, kind, is_main_frame)
"""

def init_gui(application, port=5000, argv=None):
    """
    Initializes the Qt web engine, starts the web application, and loads the
    main page.
    """
    if argv is None:
        argv = sys.argv

    title = "Topics Explorer"
    icon = str(pathlib.Path("application", "static", "img", "app_icon.png"))

    qtapp = PyQt5.QtWidgets.QApplication(argv)
    webapp = ApplicationThread(application, port)
    webapp.start()
    qtapp.aboutToQuit.connect(webapp.terminate)

    screen = qtapp.primaryScreen()
    size = screen.size()
    width = size.width() - (size.width() / 100 * 7)
    height = size.height() - (size.height() / 100 * 20)

    webview = PyQt5.QtWebEngineWidgets.QWebEngineView()
    webview.resize(width, height)
    webview.setWindowTitle(title)
    webview.setWindowIcon(PyQt5.QtGui.QIcon(icon))
    webview.load(PyQt5.QtCore.QUrl("http://localhost:{}".format(port)))
    
    def download_requested(item):
        """
        Opens a file dialog to save the ZIP archive.
        """
        path = PyQt5.QtWidgets.QFileDialog.getSaveFileName(None,
                                                           "Select destination folder and file name",
                                                           "",
                                                           "Zip files (*.zip)")[0]
        item.setPath("{path}.{ext}".format(path=path, ext="zip"))
        item.accept()

    webview.page().profile().downloadRequested.connect(download_requested)
    webview.show()
    return qtapp.exec_()


def run():
    """
    Calls the main function.
    """
    sys.exit(init_gui(application.web.app))
