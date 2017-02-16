from dariah_topics import preprocessing as pre
import glob
import os.path
import pandas as pd
import regex as re
import logging

log = logging.getLogger('testing')
log.addHandler(logging.NullHandler())
logging.basicConfig(level = logging.WARNING,
			format = '%(levelname)s %(name)s: %(message)s')
regular_expression = r'\p{Letter}+\p{Punctuation}?\{Letter}+'

def gensim2dataframe(model):
    num_topics = model.num_topics
    topics_df = pd.DataFrame(index = range(num_topics), columns= range(10))

    topics = model.show_topics(num_topics)
    
    for topic_dist in topics:    
        idx = topic_dist[0]
        temp = re.findall(r"\"(.+?)\"", topics[idx][1])
        topics_df.loc[idx] = temp
    
    return topics_df

path_txt = "/mnt/data/dariah/grenzbote_plain"

doclist_txt = pre.create_document_list(path_txt)
doc_labels = list(pre.get_labels(doclist_txt))

corpus_txt = pre.read_from_txt(doclist_txt)
doc_tokens = [list(pre.tokenize(txt)) for txt in list(corpus_txt)]
id_types, doc_ids = pre.create_dictionaries(doc_labels, doc_tokens)
log.info("Length of id_types: %s", len(id_types))
log.info("Length of doc_ids: %s", len(doc_ids))
sparse_bow = pre.create_mm(doc_labels, doc_tokens, id_types, doc_ids)
doc2id = {value : key for key, value in doc_ids.items()}
type2id = {value : key for key, value in id_types.items()}

hapax_from_remove = pre.find_hapax(sparse_bow, id_types)
stopwords_from_remove = set(pre.find_stopwords(sparse_bow, id_types))

features_to_be_removed = hapax_from_remove.union(set(stopwords_from_remove))

sparse_bow_short = pre.remove_features(sparse_bow, id_types,features_to_be_removed)

pre.save_bow_mm(sparse_bow_short, "gensim_txt")

mm = MmCorpus("gensim_txt.mm")

model = LdaModel(corpus=mm, id2word=type2id, num_topics=40, passes = 50, iterations = 20)

topics = model.show_topics(num_topics = 40)
topics

topics_df = gensim2dataframe(model)

topics_df.to_csv("gensim_output.csv")
