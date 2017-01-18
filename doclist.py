"""
Maintaining Lists of Documents
==============================

A __document list__ manages a list of documents. There are various
implementations of varying powerfulness, all have the following in common:

* A document list keeps a fixed list of documents in order, i.e. after you
  created the list you can call the iteration functions and get the same file
  at the same position (even if, e.g., the underlying directory changes). So
  these files can be matched with lists of document _contents_.

* A document list separates a _base directory_ with some way to form _file
  names_. Thus, you can easily create a mirror (of, e.g., files transformed
  in some way) in a different directory, or modify the way filenames are formed.

Segments
--------

"""

from pathlib import Path
from itertools import zip_longest

class SimpleDocList:
    """
    Very simple document list based on file name globbing.
    """

    def __init__(self, basepath, glob_pattern='*', filenames=None):
        """
        Creates a new document list either from the given file names
        or by looking for files matching the glob_pattern in the basepath.

        Args:
            basepath (Path or str): Root directory where your corpus resides
            glob_pattern (str): A file glob pattern matching the files to
                include.
            filenames (list): An iterable of paths or file names relative to
                basepath. If `None`, look for files on the file system.

        Examples:
            All existing '*.txt' files in the 'corpus_txt' directory
            >>> SimpleDocList('corpus_txt', '*.txt')


        """
        self.basepath = Path(basepath)
        self.segments = None
        if filenames is None:
            self._files = list(p.relative_to(self.basepath)
                            for p in self.basepath.glob(glob_pattern))
        else:
            self._files = list(Path(name) for name in filenames)

    def full_paths(self, as_strlist=False):
        """
        Returns an iterable of full paths for the (unsegmented) files.

        Args:
            as_strlist(bool): if True, the result is a `list` of `str`ings.

        Returns:
            Iterable over `Path`s representing the full paths.
        """
        result = (Path(self.basepath, p) for p in self._files)
        if as_strlist:
            result = list(map(str, result))
        return result

    def __iter__(self):
        return iter(self.full_paths())

    def labels(self):
        return (path.stem for path in self._files)

    def copy(self):
        """
        Returns a copy of this list.
        """

    def flatten_segments(self, segmented_docs):
        """
        Records and flattens segment counts according to the stream of documents.

        Assume you have three documents

        A : I am an example document
        B : Me too
        C : All examples reference themselves

            docs = SimpleDocList('.', filenames=['A','B','C'])

        Now, you have an (external) segmenter function that segments each document
        into segments each being at most two tokens long. The data structure your
        segmenter will produce looks similar to the following:

             segmented_corpus = \
                   [[['I', 'am'], ['an', 'example'], ['document']],
                    [['Me', 'too']],
                    [['All', 'examples'], ['reference', 'themselves']]]

        Now, if you run docs.flatten_segments(self), it will do two things: it will
        record how many segments each document has (A: 3, B: 1, C: 2), and it will
        return a structure flattened by one level as in the following:

            [['I', 'am'], ['an', 'example'], ['document'], ['Me', 'too'],
             ['All', 'examples'], ['reference', 'themselves']]

        I.e. the result will look like a corpus of six shorter documents. This
        matches with the iteration you get when you call docs.segments().

        Args:
            segmented_docs: Iterable of documents, each document being an
               iterable of segments.

        Returns:
            Iterable of segments.

        Notes:
            Instead of lists you will receive generators, but you can iterate
            over these as well.
        """
        segment_counts = []
        self._segment_counts = segment_counts
        for doc in segmented_docs:
            segment_counts.append(0)
            for segment in doc:
                segment_counts[-1] += 1
                yield segment

    def segment_counts(self):
        """
        Returns an iterable of the number of each segments for each document.
        """
        return self._segment_counts


    def segments(self):
        """
        Returns a tuple (filename, segment_no) for each segment, with filename
        being the full path to the document and segment_no an integer starting at 0
        """
        for filename, segment_count in zip_longest(self.full_paths(),
                                                   self.segment_counts()):
            if segment_count is None:
                yield (filename, None)
            else:
                for segment_no in range(segment_count):
                    yield (filename, segment_no)
