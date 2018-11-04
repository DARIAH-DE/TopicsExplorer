#!/usr/bin/env python3

import argparse
import webbrowser

from application import testing


NAME = "DARIAH Topics Explorer"
DESCRIPTION = "Explore your own text collection with a topic model – without prior knowledge."

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog=NAME,
                                     description=DESCRIPTION)
    parser.add_argument("--browser",
                        action="store_true",
                        help="Use this parameter to open the UI in "
                             "your default web browser.")
    parser.add_argument("--debug",
                        action="store_true",
                        help="Run the application in debug mode.")
    args = parser.parse_args()

    if args.browser:
        #webbrowser.open("http://127.0.0.1:5000/")
        testing.app.run(debug=args.debug)
    else:
        pass

