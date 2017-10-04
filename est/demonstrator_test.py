#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, 'demonstrator')
import demonstrator
from io import BytesIO
import os
import tempfile
import unittest
from pathlib import Path


class DemonstratorTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, demonstrator.app.config['DATABASE'] = tempfile.mkstemp()
        demonstrator.app.testing = True
        self.app = demonstrator.app.test_client()
        self.project_path = Path(__file__).absolute().parent.parent

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(demonstrator.app.config['DATABASE'])

    def test_render_index(self):
        rv = self.app.get('/')
        assert b'index' in rv.data

    def test_topic_modeling(self):
        text_bytes = "This is an example."
        int_bytes = "1"
        stopword_bytes = "this\nis\na\nstopwords\nlist"
        files = (BytesIO(text_bytes), 'document.txt')
        num_topics = BytesIO(int_bytes)
        num_iterations = BytesIO(int_bytes)
        stopword_list = (BytesIO(stopword_bytes), 'stopwords.txt')
        data = {'files': files, 'num_topics': num_topics,
                'num_iterations': num_iterations, 'stopword_list': stopword_list}
        resp = self.app.post('/upload', data=data)


if __name__ == '__main__':
    unittest.main()
