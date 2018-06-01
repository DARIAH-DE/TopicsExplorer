#!/usr/bin/env python3

import application
import pathlib
import tempfile
import pytest


class TestWebApplication:
    def setup_method(self):
        """
        Creating a Flask app and temporary folders.
        """
        self.app, self.dumpdir, self.archivedir = application.config.create_app()
    
    def test_temporary_folders(self):
        """
        Tests if temporary folders are set up correctly.
        """
        tempdir = tempfile.gettempdir()
        correct_dumpdir = str(pathlib.Path(tempdir, "topicsexplorerdump"))
        correct_archivedir = str(pathlib.Path(tempdir, "topicsexplorerdata"))
        
        assert self.dumpdir == correct_dumpdir
        assert self.archivedir == correct_archivedir

    def test_configs(self):
        """
        Tests if the config loads correctly.
        """
        cwd = pathlib.Path.cwd()

        assert self.app.config['DEBUG'] == False
        assert self.app.import_name == 'application.config'
        assert self.app.template_folder == 'templates'
        assert self.app.static_folder == str(pathlib.Path(cwd, 'application', 'static'))