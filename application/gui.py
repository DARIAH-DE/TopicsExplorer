import application
import pathlib
import sys
import PyQt5.QtGui
import PyQt5.QtWidgets
import PyQt5.QtWebEngineWidgets
import PyQt5.QtCore


parent_dir = pathlib.Path(__file__).parent
TITLE = "Topics Explorer"
ICON = str(pathlib.Path(parent_dir, "static", "img", "app_icon.png"))
PORT = 5000

if hasattr(PyQt5.QtCore.Qt, "AA_EnableHighDpiScaling"):
    PyQt5.QtWidgets.QApplication.setAttribute(PyQt5.QtCore.Qt.AA_EnableHighDpiScaling, True)
 
if hasattr(PyQt5.QtCore.Qt, "AA_UseHighDpiPixmaps"):
    PyQt5.QtWidgets.QApplication.setAttribute(PyQt5.QtCore.Qt.AA_UseHighDpiPixmaps, True)

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

class ApplicationThread(PyQt5.QtCore.QThread):
    def __init__(self, application, port=PORT):
        super(ApplicationThread, self).__init__()
        self.application = application
        self.port = port

    def __del__(self):
        self.wait()

    def run(self):
        self.application.run(port=self.port, threaded=True)

"""
# This part allows you to open external links in the standard browser,
# but has been discarded because potential dead links should be avoided
# in the application.

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

def init_gui(application, port=PORT, argv=None, title=TITLE, icon=ICON):
    """
    Initializes the Qt web engine, starts the web application, and loads the
    main page.
    """
    if argv is None:
        argv = sys.argv
    
    # Starting the Flask application.
    qtapp = PyQt5.QtWidgets.QApplication(argv)
    webapp = ApplicationThread(application, port)
    webapp.start()
    qtapp.aboutToQuit.connect(webapp.terminate)

    # Setting width and height individually based on the 
    # screen resolution: 93% of the screen for width,
    # 80% for height.
    screen = qtapp.primaryScreen()
    size = screen.size()
    width = size.width() - (size.width() / 100 * 7)
    height = size.height() - (size.height() / 100 * 20)

    # Applying settings and loading the main page.
    webview = PyQt5.QtWebEngineWidgets.QWebEngineView()
    webview.resize(width, height)
    webview.setWindowTitle(title)
    webview.setWindowIcon(PyQt5.QtGui.QIcon(icon))
    webview.load(PyQt5.QtCore.QUrl("http://localhost:{}".format(port)))
    
    # If the user clicks a download button, a window pops up.
    webview.page().profile().downloadRequested.connect(download_requested)

    # Show the webview.
    webview.show()
    return qtapp.exec_()

def run():
    """
    Calls the main function.
    """
    sys.exit(init_gui(application.web.app))
