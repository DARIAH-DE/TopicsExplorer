import pandas as pd
import re
import os
import csv



class ReadFromTXT:
    
    def __init__(self, doclist):

        self.doclist = doclist
        
    def __iter__(self):
        for file in self.doclist:
            with open(file, 'r', encoding = "utf-8") as f:
                
                yield f.read()
                
                
class Segmenter:
    
    def __init__(self, doc, length):
        
        self.doc = doc
        self.length = length
        
    def __iter__(self):

        """
        Yields document slizes with length words.
        Can be used to produce list pof lists with document-segments relationships.
        
        Args:
            doc (Iterable): An iterable of tokens that is to be segmented. Preferably as stream of documents.
            length (int): Target size of each segment. The last segment will probably be smaller.
            
        Todo:
            Implement fuzzy option to consider paragraph breaks.
        """
        
        doc = self.doc.split()
        for i, word in enumerate(doc):
            if i % self.length == 0:
                yield doc[i : i + self.length]
                
                



path = "corpus_off/"
docs = []
#doc_labels = []
columns = ['ParagraphId', 'TokenId', 'Lemma', 'CPOS', 'NamedEntity']
pos_tags = ['ADJ', "V"]
files = sorted(os.listdir(path=path))

class filterPOS(object):
    
    def __init__(self, path, files, pos_tags):
        
        self.path = path
        self.files = files
        self.pos_tags = pos_tags
        self.columns = ['ParagraphId', 'TokenId', 'Lemma', 'CPOS', 'NamedEntity']
        self.doc = pd.DataFrame()
        self.labels = []
    
    
    def getLabels(self):
        for self.file in self.files:
            if not self.file.startswith("."):
                filepath = os.path.join(self.path, self.file)

                label = os.path.basename(self.file)

                df = pd.read_csv(filepath, sep="\t", quoting=csv.QUOTE_NONE)
                df = df[self.columns]

                for p in pos_tags:
                    self.doc = self.doc.append(df.loc[df["CPOS"] == p])
                yield label

    def getLemma(self):
        for self.file in self.files:
            if not self.file.startswith("."):
                filepath = os.path.join(self.path, self.file)

                label = os.path.basename(self.file)

                df = pd.read_csv(filepath, sep="\t", quoting=csv.QUOTE_NONE)
                df = df[self.columns]

                for p in pos_tags:
                    yield df.loc[df["CPOS"] == p]["Lemma"]
