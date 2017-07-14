from dariah_topics.doclist import PathDocList
from pathlib import Path
from nose.tools import eq_

project_path = Path(__file__).absolute().parent.parent


def setup():
    global corpus_txt, docs, testfilenames, segments
    testfilenames = ['file1.txt', 'file2.txt', 'subdir/file3.txt']
    corpus_txt = PathDocList(str(project_path.joinpath('grenzboten_sample')))
    docs = PathDocList('test', filenames=testfilenames)
    segments = [
        # file1:
        ["First segment", "second segment"],
        # file2:
        ["second file, only one segment"],
        # file3:
        ["lots", "of", "segments"]]


def test_pdl_glob():
    """The glob created list should contain the 17 files from corpus_txt"""
    eq_(len(corpus_txt), 17, msg="Not 17 texts: " + str(docs))


def test_pdl_list():
    """Listing a pathlist should return the full paths to the files"""
    eq_(list(docs), ['test/file1.txt', 'test/file2.txt',
                     'test/subdir/file3.txt'])


def test_get_docs():
    """get_docs returns the plain file names"""
    eq_(list(map(str, docs.get_docs())), testfilenames)


def test_full_path():
    """full_path can construct a full path."""
    eq_(docs.full_path(Path('example'), as_str=True), 'test/example')


def test_full_paths():
    eq_(docs.full_paths(), [Path('test', fn) for fn in testfilenames])


def test_labels():
    eq_(docs.labels(), ['file1', 'file2', 'file3'])


def test_copy():
    docs2 = docs.copy()
    eq_(type(docs2), type(docs))


def test_flatten_segments():
    recorder = docs.copy()
    flattened = list(recorder.flatten_segments(segments))
    eq_(len(flattened), 6)
    eq_(len(list(recorder.segments())), 6)


def test_segment_filenames():
    recorder = docs.copy()
    list(recorder.flatten_segments(segments))
    eq_(list(recorder.segment_filenames(as_str=True)),
        ['test/file1.0.txt', 'test/file1.1.txt', 'test/file2.0.txt',
         'test/file3.0.txt', 'test/file3.1.txt', 'test/file3.2.txt'])

def test_with_segments():
    recorder = docs.copy()
    list(recorder.flatten_segments(segments))
    segmented = recorder.with_segment_files()
    eq_(list(segmented),
        ['test/file1.0.txt', 'test/file1.1.txt', 'test/file2.0.txt',
         'test/file3.0.txt', 'test/file3.1.txt', 'test/file3.2.txt'])
