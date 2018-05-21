#!/usr/bin/env python3

import application
import argparse


DESCRIPTION = """
              Run DARIAH Topics Explorer either as a desktop application with 
              its own window, or as a web application in a browser. If you do 
              not specify any parameters, the desktop application is started.
              """

parser = argparse.ArgumentParser(description=DESCRIPTION)
parser.add_argument('--browser', action='store_true',
                    help="Opens the UI in your standard browser.")

args = vars(parser.parse_args())

if args['browser']:
    import webbrowser
    webbrowser.open('http://127.0.0.1:5000/')
    application.web.app.run()
else:
    application.gui.run()
