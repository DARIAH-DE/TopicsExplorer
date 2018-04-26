import application
import pathlib
import sys
import PyQt5.QtGui
import PyQt5.QtWidgets
import PyQt5.QtWebEngineWidgets
import PyQt5.QtCore


class ApplicationThread(PyQt5.QtCore.QThread):
    def __init__(self, application, port=5000):
        super(ApplicationThread, self).__init__()
        self.application = application
        self.port = port

    def __del__(self):
        self.wait()

    def run(self):
        self.application.run(port=self.port, threaded=True)


class WebPage(PyQt5.QtWebEngineWidgets.QWebEnginePage):
    def __init__(self, root_url):
        super(WebPage, self).__init__()
        self.root_url = root_url

    def home(self):
        self.load(PyQt5.QtCore.QUrl(self.root_url))

    def acceptNavigationRequest(self, url, kind, is_main_frame):
        """Open external links in browser and internal links in the webview"""
        ready_url = url.toEncoded().data().decode()
        is_clicked = kind == self.NavigationTypeLinkClicked
        if is_clicked and self.root_url not in ready_url:
            PyQt5.QtGui.QDesktopServices.openUrl(url)
            return False
        return super(WebPage, self).acceptNavigationRequest(url, kind, is_main_frame)


def init_gui(application, port=5000, argv=None):
    if argv is None:
        argv = sys.argv

    title = 'Topics Explorer'
    icon = str(pathlib.Path('application', 'static', 'img', 'app_icon.png'))

    qtapp = PyQt5.QtWidgets.QApplication(argv)
    webapp = ApplicationThread(application, port)
    webapp.start()
    qtapp.aboutToQuit.connect(webapp.terminate)

    window = PyQt5.QtWidgets.QMainWindow()

    screen = qtapp.primaryScreen()
    size = screen.size()
    width = size.width() - (size.width() / 100 * 7)
    height = size.height() - (size.height() / 100 * 20)

    window.resize(width, height)
    window.setWindowTitle(title)
    window.setWindowIcon(PyQt5.QtGui.QIcon(icon))

    webview = PyQt5.QtWebEngineWidgets.QWebEngineView(window)
    window.setCentralWidget(webview)

    page = WebPage('http://localhost:{}'.format(port))
    page.home()
    webview.setPage(page)

    def download_requested(item):
        path = PyQt5.QtWidgets.QFileDialog.getSaveFileName(None,
                                                           'Select destination folder and file name',
                                                           '',
                                                           'Zip files (*.zip)')[0]
        item.setPath('{path}.{ext}'.format(path=path, ext='zip'))
        item.accept()

    webview.page().profile().downloadRequested.connect(download_requested)

    window.show()
    return qtapp.exec_()


def run():
    sys.exit(init_gui(application.web.app))
