#!/usr/bin/env python3

import argparse
import application


DESCRIPTION = "Run DARIAH Topics Explorer either as a web application in "\
              "the browser, or as a desktop application with its own window. "\
              "If you do not specify any parameters, the desktop application "\
              "is started."

parser = argparse.ArgumentParser(description=DESCRIPTION)
parser.add_argument('--browser', action='store_true',
                    help="Opens the UI in the standard browser.")

args = vars(parser.parse_args())

if args['browser']:
    import webbrowser
    webbrowser.open('http://127.0.0.1:5000/')
    application.web.app.run()
else:
    application.gui.run()
