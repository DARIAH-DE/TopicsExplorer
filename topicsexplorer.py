#!/usr/bin/env python3

import argparse
import logging
import sys
import webbrowser

from application import views
try:
    from application import gui
except:
    logging.warning("Module `gui` is not available.")


NAME = "DARIAH Topics Explorer"
DESCRIPTION = "Explore your own text collection with a topic model – without prior knowledge."


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog=NAME,
                                     description=DESCRIPTION)
    parser.add_argument("--browser",
                        action="store_true",
                        help="Use this parameter to open the UI in your default web browser.")
    parser.add_argument("--frozen",
                        action="store_true",
                        help="Simulate a frozen application.")

    args = parser.parse_args()

    if args.browser:
        #webbrowser.open("http://localhost:5010/")
        views.web.run(port="5010", debug=True)
    elif getattr(sys, "frozen", False) or args.frozen:
        views.web.run()
    else:
        try:
            gui.run()
        except NameError:
            raise AttributeError("Frontend is not available. "
                                 "Append parameter `--browser`.")
