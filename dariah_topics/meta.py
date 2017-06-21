"""Metadata.

This module contains functions for metadata handling
provided by `DARIAH-DE`_.

.. _DARIAH-DE:
    https://de.dariah.eu
    https://github.com/DARIAH-DE
"""

__author__ = "DARIAH-DE"
__authors__ = "Thorsten Vitt"
__email__ = "thorsten.vitt@uni-wuerzburg.de"

import abc
import glob
import os
import pandas as pd
import regex

class AbstractCorpus:
    
    def __init__(self, basedir='.', default_pattern='{Index}.txt'):
        self.basedir = basedir
        self.default_pattern = default_pattern
        self.segments = None
        
    @abc.abstractmethod
    def list_docs(self):
        """
        Returns an iterable over Mappings that describe a corpus.
        
        It is expected that each Mapping has a key 'Index' with
        unique values, and that each call lists the documents in 
        the same order.
        """
    
    def list_segments(self):
        """
        Returns an iterable over Mappings that describe a segmented corpus.
        
        There is a dict for each segment with the metadata, and an int-valued
        item `segment` identifies the segment within its document.
        """
        if self.segments is None:
            raise ValueError("Not segmentized yet")
        for doc, segcount in self.list_docs(), self.segments:
            for seg in range(segcount):
                yield dict(doc, segment=seg)
        
    def filenames(self, basedir=None, pattern=None, segments=False):
        """
        Yields a filename for each entry in the metadata.
        """        
        if basedir is None:
            basedir = self.basedir
        if pattern is None:
            pattern = self.default_pattern        
        items = self.list_segments() if segments else self.list_docs()        
        for doc in items:
            filename = os.path.join(basedir, pattern.format_map(doc))
            yield filename
                        
    def forall(self, function, *args, basedir=None, pattern=None, segments=False, **kwargs):
        """
        Calls the given function for each filename.
        
        If additional positional arguments are given, they must each be an iterable
        of the same length that corresponds to the list of filenames.
        
        So this is essentially equivalent to:
        
            map(partial(function, **kwargs), self.filenames(basedir, pattern), *args)
            
        Todo:
        
            This could get two boolean arguments to enable convenience behaviour:
            
            tee: If True, call the function with a copy of the iterable. Can be
                 as intermediate pipeline step that dumps something.
            consume: If True, consume function's result and return nothing.
            
            Both options would force the pipeline to run immediately.
                 
        """        
        for args in zip(self.filenames(basedir, pattern, segments), *args):
            yield function(*args, **kwargs)
            
    def flatten_segments(self, documents):
        """
        Flatten a segment structure and record segment counts.
        
        `documents` is expected to be an Iterable of documents that matches this 
        corpus' metadata. Each document is expected to be an Iterable of segments.
        Each segment is expected to be an Iterable of features (like tokens).
        
        This method yields each segment, thus it flattens the structure by one 
        level. Additionally, it keeps track of segments by counting the number of 
        segments in each document in this object's `segments` field. Afterwards,
        you can pass `segments=True` to `filenames` and `forall`.
        """
        self.segments = []
        for document in documents:
            self.segments.append(0)
            for segment in document:
                self.segments[-1] += 1
                yield segment

class TableCorpus(AbstractCorpus):
    
    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.metadata = pd.DataFrame(data)
        
    def list_docs(self):
        return (t._asdict() for t in self.metadata.itertuples())
    
def fn2metadata(glob_pattern='corpus/*.txt', fn_pattern=regex.compile('(?<author>[^_]+)_(?<title>.+)'), index=None):
    """
    Extracts basic metadata filenames.
    
    Args:
       glob_pattern (str): A glob pattern matching the files to list, cf. glob.glob
       fn_pattern (re.Regex): A regular expression that extracts metadata fields from the files' base name. 
           The pattern must contain named groups (which have the form `(?<name>pattern)`, where name is
           the name of the metadata field and pattern is the part of the re matching this field name).
           The default will expect file names that contain a `_`, and it will assign everything before
           the _ to the `author` field and everything after to the `title` field.
       index (str): Name of the column that will be used as index column. If None, an artificial index
           (integers, starting at 0) will be used.
    Returns:
        pd.DataFrame with the following columns:
           * basename: filename without path or extension
           * filename: full filename
           * one column for every named pattern that matched for at least one file
    """
    metadata_list = []
    for filename in glob.glob(glob_pattern):
        basename, __ = os.path.splitext(os.path.basename(filename))
        md = fn_pattern.match(basename).groupdict()
        md["basename"] = basename
        md["filename"] = filename
        metadata_list.append(md)
    metadata = pd.DataFrame(metadata_list)
    if index is not None:
        metadata = metadata.set_index(index)
    return metadata