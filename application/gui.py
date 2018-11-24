from pathlib import Path
import sys

from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import QtWebEngineWidgets
from PyQt5 import QtCore

from application import views


PARENT = Path(__file__).parent
TITLE = "Topics Explorer :: DARIAH-DE"
ICON = str(Path(PARENT, "static", "img", "logos", "favicon-template.png"))
PORT = 5000

# This is for high DPI scaling:
if hasattr(QtCore.Qt, "AA_EnableHighDpiScaling"):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
if hasattr(QtCore.Qt, "AA_UseHighDpiPixmaps"):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


def download_request(item):
        """Opens a file dialog to save the ZIP archive.
        """
        mimetype = item.mimeType()
        if "octet-stream" in mimetype:
            ext = ".png"
        elif "svg" in item.mimeType():
            ext = ".svg"
        elif "zip" in mimetype:
            ext = ".zip"
        else:
            ext = ""

        path = QtWidgets.QFileDialog.getSaveFileName(None,
                                                    "Select destination folder and file name",
                                                    "",
                                                    "")[0]
        item.setPath("{path}{ext}".format(path=path, ext=ext))
        item.accept()


class ApplicationThread(QtCore.QThread):
    def __init__(self, application, port=PORT):
        super(ApplicationThread, self).__init__()
        self.application = application
        self.port = port

    def __del__(self):
        self.wait()

    def run(self):
        self.application.run(port=self.port)


class WebPage(QtWebEngineWidgets.QWebEnginePage):
    def __init__(self, root_url):
        super(WebPage, self).__init__()
        self.root_url = root_url

    def home(self):
        self.load(QtCore.QUrl(self.root_url))

    def acceptNavigationRequest(self, url, kind, is_main_frame):
        ready_url = url.toEncoded().data().decode()
        is_clicked = kind == self.NavigationTypeLinkClicked

        if is_clicked and (self.root_url not in ready_url):
            QtGui.QDesktopServices.openUrl(url)
            return False
        return super(WebPage, self).acceptNavigationRequest(url, kind, is_main_frame)


def init_gui(application, port=PORT, argv=None, title=TITLE, icon=ICON):
    """Initialize Qt web engine, start Flask application.
    """
    if argv is None:
        argv = sys.argv

    # Starting the Flask application:
    qtapp = QtWidgets.QApplication(argv)
    web = ApplicationThread(application, port)
    web.start()
    
    def kill(application=web):
        """Kill the Flask process.
        """
        application.terminate()

    qtapp.aboutToQuit.connect(kill)

    # Setting width and height individually based on the 
    # screen resolution: 93% of the screen for width,
    # 80% for height:
    screen = qtapp.primaryScreen()
    size = screen.size()
    width = size.width() - size.width() / 100 * 7
    height = size.height() - size.height() / 100 * 20

    # Applying settings and loading the home page:
    webview = QtWebEngineWidgets.QWebEngineView()
    webview.resize(width, height)
    webview.setWindowTitle(title)
    webview.setWindowIcon(QtGui.QIcon(icon))
    
    page = WebPage('http://localhost:{}'.format(port))
    page.home()
    webview.setPage(page)
    
    # If the user clicks a download button, a window pops up:
    webview.page().profile().downloadRequested.connect(download_request)

    # Show the webview:
    webview.show()
    return qtapp.exec_()


def run():
    """Run Topics Explorer.
    """
    sys.exit(init_gui(views.web))
