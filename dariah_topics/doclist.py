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
from abc import abstractmethod, abstractproperty
from copy import deepcopy

class BaseDocList:
    """

    """

    def __init__(self, basepath):
        self.basepath = Path(basepath)
        self._segment_counts = None

    def copy(self):
        return deepcopy(self)

    def full_path(self, document, as_str=False):
        """
        Constructs a full path for the given document.

        Args:
            document: this is one document in the way the subclass chooses to
                represent documents.
            as_str (bool): if True, the result is a str, otherwise it is a `Path`

        Notes:
            The default implementation passed document on to `Path()`.
            Implementers will most probably want to override this.
        """
        path = Path(self.basepath, document)
        if as_str:
            path = str(path)
        return path

    @abstractmethod
    def get_docs(self):
        """
        Returns a sequence of documents, in the form the implementing class
        chooses.

        Note:
            Subclasses may implement a method `_get_item(self, index)`, with
            index being integer or slice, to speed access up.
        """
        pass

    def full_paths(self, as_str=False):
        """
        Returns a list of full paths. Calls full_path.
        """
        return [self.full_path(doc, as_str) for doc in self.get_docs()]

    @abstractmethod
    def label(self, document):
        """
        Returns a label suitable for the document.
        """
        pass

    def __iter__(self):
        """
        When used as an iterable, this object looks like an iterable of full paths.
        """
        return iter(self.full_paths(as_str=True))

    def __len__(self):
        """
        When used as a sequence, this object looks like a sequence of full paths.
        """
        return len(self.get_docs())

    def __getitem__(self, index):
        """
        When used as a sequence, this object looks like a sequence of full paths.
        """
        try:
            selection = self._getitem(index)
        except AttributeError:
            selection = self.get_docs()[index]

        if isinstance(index, slice):
            return [self.full_path(doc, as_str=True) for doc in selection]
        else:
            return self.full_path(selection, as_str=True)

    def labels(self):
        """
        Returns a list of (human-readable) labels for all documents.
        """
        return [self.label(doc) for doc in self.get_docs()]

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
        Yields a tuple (document, segment_no) for each segment, with document
        being the internal representation of each document and segment_count an
        integer starting at 0
        """
        for document, segment_count in zip_longest(self.get_docs(),
                                                   self.segment_counts()):
            if segment_count is None:
                yield (document, None)
            else:
                for segment_no in range(segment_count):
                    yield (document, segment_no)


class PathDocList(BaseDocList):
    """
    Document list based on a list of Paths.
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
        """
        self.basepath = Path(basepath)
        self._segment_counts = None
        if filenames is None:
            self._files = [p.relative_to(self.basepath)
                           for p in self.basepath.glob(glob_pattern)]
        else:
            paths = (Path(name) for name in filenames)
            if glob_pattern is not None:
                paths = (path for path in paths if path.match(glob_pattern))
            self._files = list(paths)

    def get_docs(self):
        return self._files

    def label(self, document):
        return document.stem
