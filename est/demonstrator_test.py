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


int_bytes = b"1"
stopword_bytes = b"this\nis\na\nstopwords\nlist"
text_bytes = b"""
I had called upon my friend, Mr. Sherlock Holmes, one day in the autumn
of last year, and found him in deep conversation with a very stout,
florid-faced elderly gentleman, with fiery red hair. With an apology for
my intrusion, I was about to withdraw, when Holmes pulled me abruptly into
the room and closed the door behind me.

"Wedlock suits you," he remarked. "I think Watson, that you have put on
seven and a half pounds since I saw you."

"Seven," I answered.

"Indeed, I should have thought a little more. Just a trifle more, I
fancy, Watson. And in practice again, I observe. You did not tell me
that you intended to go into harness."

"Then how do you know?"
"""

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
        files = (BytesIO(text_bytes), 'document.txt')
        num_topics = BytesIO(int_bytes)
        num_iterations = BytesIO(int_bytes)
        stopword_list = (BytesIO(stopword_bytes), 'stopwords.txt')
        data = {'files': files, 'num_topics': num_topics,
                'num_iterations': num_iterations, 'stopword_list': stopword_list}
        resp = self.app.post('/upload', data=data)


if __name__ == '__main__':
    unittest.main()
