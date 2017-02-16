from dariah_topics.preprocessing import segment_fuzzy, split_paragraphs
from nose.tools import eq_
from itertools import chain
import re

_DEMO_DPAR = """
"Wedlock suits you," he remarked. "I think Watson, that you have put on
seven and a half pounds since I saw you."

"Seven," I answered.

"Indeed, I should have thought a little more. Just a trifle more, I
fancy, Watson. And in practice again, I observe. You did not tell me
that you intended to go into harness."

"Then how do you know?"
"""

_DEMO_SPAR = '''"Wedlock suits you," he remarked. "I think Watson, that you have put on seven and a half pounds since I saw you."
"Seven," I answered.
"Indeed, I should have thought a little more. Just a trifle more, I fancy, Watson. And in practice again, I observe. You did not tell me that you intended to go into harness."
"Then how do you know?"'''


def test_split_paragraphs_spar():
    chunked = split_paragraphs(_DEMO_SPAR)
    eq_(len(chunked), 4, msg='not 4 chunks: ' + str(chunked))


def test_split_paragraphs_dpar():
    chunked = split_paragraphs(_DEMO_DPAR, sep=r'\n\n')
    eq_(len(chunked), 4, msg='not 4 chunks: ' + str(chunked))


def test_split_paragraphs_dpar_re():
    chunked = split_paragraphs(_DEMO_DPAR, sep=re.compile(r'\n\n'))
    eq_(len(chunked), 4, msg='not 4 chunks: ' + str(chunked))









def test_plain_segments():
    """segment_size chunks, zero tolerance"""
    document = ("01234 "*4).split()
    segments = list(segment_fuzzy(document, segment_size=5))
    eq_(segments, [[['0', '1', '2', '3', '4']],
                   [['0', '1', '2', '3', '4']],
                   [['0', '1', '2', '3', '4']],
                   [['0', '1', '2', '3', '4']]])


def test_shorter_segments():
    """shorter segments than chunks, no tolerance"""
    document = ("01234 "*4).split()
    segments = list(segment_fuzzy(document, segment_size=4))
    eq_(segments, [[['0', '1', '2', '3']],
                   [['4'], ['0', '1', '2']],
                   [['3', '4'], ['0', '1']],
                   [['2', '3', '4'], ['0']],
                   [['1', '2', '3', '4']]])


def test_tolerance():
    """chunk size within tolerance"""
    document = ("01234 "*4).split()
    segments = list(segment_fuzzy(document, segment_size=4, tolerance=1))
    eq_(segments, [[['0', '1', '2', '3', '4']],
                   [['0', '1', '2', '3', '4']],
                   [['0', '1', '2', '3', '4']],
                   [['0', '1', '2', '3', '4']]])


def test_tolerance_2():
    """segment size ~ 2*chunk_size"""
    document = ("01234 "*4).split()
    segments = list(segment_fuzzy(document, segment_size=8, tolerance=2))
    eq_(segments, [[['0', '1', '2', '3', '4'],
                    ['0', '1', '2', '3', '4']],
                   [['0', '1', '2', '3', '4'],
                    ['0', '1', '2', '3', '4']]])


def test_overlong_chunk():
    """single chunk is longer than two segments"""
    document = "012345678901234 01234".split()
    segments = list(segment_fuzzy(document, segment_size=4, tolerance=1))
    flattened = [ list(chain.from_iterable(seg)) for seg in segments ]
    lengths = list(map(len, flattened))
    assert min(lengths[:-1]) >= 3, "a segment is too short in " + str(segments)
    assert max(lengths) <= 5, "a segment is too long in " + str(segments)
