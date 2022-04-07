import webbrowser

from topicsexplorer import views


if __name__ == "__main__":
    webbrowser.open("http://localhost:5001/")
    views.web.run(port=5001)
