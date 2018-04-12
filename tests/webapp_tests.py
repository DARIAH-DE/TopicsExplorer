#!/usr/bin/env python3

import webapp

class TestConfig:
    def test_dev_config(self):
        """
        Tests if the development config loads correctly.
        """

        app = webapp.app.test_client()

        assert app.config['DEBUG'] is True

    def test_prod_config(self):
        """
        """

    def test_pyinstaller_config(self):
        """
        """
