import preprocessing
import logging
import glob

log = logging.getLogger('preprocessing')
log.addHandler(logging.NullHandler())
logging.basicConfig(level = logging.DEBUG,
                    format = '%(asctime)s %(levelname)s %(name)s: %(message)s',
                    datefmt = '%d-%b-%Y %H:%M:%S')

#path_txt = "grenzbote_plain/*/"

path_txt = "corpus_txt"

doclist_txt = preprocessing.create_document_list(path_txt)

doc_labels = list(preprocessing.get_labels(doclist_txt))

log.debug("Document labels available (%i).", len(doc_labels))

corpus_txt = preprocessing.read_from_txt(doclist_txt)

#doc_tokens = preprocessing.tokenizer(corpus_txt)

doc_tokens = [list(preprocessing.tokenize(txt)) for txt in list(corpus_txt)]

#print(list(doc_tokens[0]))

id_types, doc_ids  = preprocessing.create_dictionaries(doc_labels, doc_tokens)

#termdoc_matrix = {v : k for k, v in id_types.items()}

#id_docs = {v : k for k, v in doc_ids.items()}

#largecounter = preprocessing.create_large_counter(doc_labels, doc_tokens, termdoc_matrix)

#largecounter = {id_docs[key] : value for key, value in largecounter.items()}

#sparse_index = preprocessing.create_sparse_index(largecounter)

print(len(doc_labels), len(doc_tokens), len(id_types), len(doc_ids))

sparse_df = preprocessing.create_mm(doc_labels, doc_tokens, id_types, doc_ids)

with open("gb_all.mm", 'a', encoding = "utf-8") as f:
    f.write("%%MatrixMarket matrix coordinate real general\n")
    sparse_df.to_csv( f, sep = ' ', header = None)
    
