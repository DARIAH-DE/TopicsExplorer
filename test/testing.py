from dariah_topics import preprocessing
import glob
import os.path
from pathlib import Path

project_path = Path(__file__).absolute().parent.parent
basepath =  str(project_path)

#path_txt = "grenzbote_plain/*/"

path_txt = "corpus_txt"

doclist_txt = preprocessing.create_document_list(path_txt)

doc_labels = list(preprocessing.get_labels(doclist_txt))

corpus_txt = preprocessing.read_from_txt(doclist_txt)

#doc_tokens = preprocessing.tokenizer(corpus_txt)

with open(os.path.join(basepath, "tutorial_supplementals/stopwords/en"), 'r', encoding = 'utf-8') as f:
    stopword_list = f.read().split('\n')

stopword_list = set(stopword_list)

doc_tokens = [list(preprocessing.tokenize(txt)) for txt in list(corpus_txt)]

#print(list(doc_tokens[0]))

id_types, doc_ids  = preprocessing.create_dictionaries(doc_labels, doc_tokens)

print(len(doc_labels), len(doc_tokens), len(id_types), len(doc_ids))

sparse_df = preprocessing.create_mm(doc_labels, doc_tokens, id_types, doc_ids)

with open("gb_all.mm", 'a', encoding = "utf-8") as f:
    f.write("%%MatrixMarket matrix coordinate real general\n")
    sparse_df.to_csv( f, sep = ' ', header = None)

sparse_df_stopwords_removed = preprocessing.remove_features(sparse_df, id_types, stopword_list)

with open("gb_all_features_removed.mm", 'a', encoding = "utf-8") as f:
    f.write("%%MatrixMarket matrix coordinate real general\n")
    sparse_df_stopwords_removed.to_csv( f, sep = ' ', header = None)
