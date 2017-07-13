# -*- coding: utf-8 -*-

"""LDA visualization.

This module contains functions for LDA visualization provided by `DARIAH-DE`_.

.. _Gensim:
    https://radimrehurek.com/gensim/index.html
.. _Mallet:
    http://mallet.cs.umass.edu/
.. _DARIAH-DE:
    https://de.dariah.eu
    https://github.com/DARIAH-DE
"""

__author__ = "DARIAH-DE"
__authors__ = "Steffen Pielstroem, Sina Bock, Severin Simmler"
__email__ = "pielstroem@biozentrum.uni-wuerzburg.de"
__version__ = "0.1"
__date__ = "2017-01-20"


from bokeh.charts import HeatMap
import logging
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
#from wordcloud import WordCloud
import numpy as np
import os
import pandas as pd
#import pyLDAvis.gensim
import regex


log = logging.getLogger('visualization')
log.addHandler(logging.NullHandler())
logging.basicConfig(level = logging.ERROR,
                    format = '%(levelname)s %(name)s: %(message)s')

class Visualization:
    def __init__(self, lda_model, corpus, dictionary, doc_labels, interactive=False):
        """Loads Gensim output for further processing.

        The output folder should contain ``corpus.mm``, ``corpus.lda``, as well as
        ``corpus_doclabels.txt`` (for heatmap) or ``corpus.dict`` (for interactive
        visualization).

        Args:
            lda_model: Path to output folder.
            corpus:
            dictionary:
            doc_labels:
            interactive (bool, optional): True if interactive visualization,
                False if heatmap is desired. Defaults to False.

        Returns:
            If `interactive == False`: corpus, model, doc_labels.
            If `interactive == True`: corpus, model, dictionary.

        Raises:
            OSError: If directory or files not found.
            ValueError: If no matching values found.
            Unexpected error: Everything else.

        Note: Currently not in use due to dependencies
        """
        try:
            log.info("Accessing corpus ...")
            self.corpus = corpus
            log.debug("Corpus available.")

            log.info("Accessing model ...")
            self.model = lda_model
            log.debug("Model available.")

            if interactive == False:
                log.debug(":param: interactive == False.")
                log.info("Accessing doc_labels ...")
                self.doc_labels = doc_labels
                log.debug("doc_labels accessed.")

            elif interactive == True:
                log.debug(":param: interactive == True.")
                log.info("Accessing dictionary ...")
                self.dictionary = dictionary
                log.debug("Dictionary available.")
                log.debug("Corpus, model and dictionary available.")

        except OSError as err:
            log.error("OS error: {0}".format(err))
            raise
        except ValueError:
            log.error("Value error: No matching value found.")
            raise
        except:
            import sys
            log.error("Unexpected error:", sys.exc_info()[0])
            sys.exit(1)
            raise

    def make_heatmap(self):
        """Generates heatmap from LDA model.

        The ingested data (e.g. with `load_gensim_output()`) has to be transmitted
        as parameters.

        Args:
            corpus: Corpus created by Gensim, e.g. corpus.mm.
            model: LDA model created by Gensim, e.g. corpus.lda.
            doc_labels (list[str]): List of document labels, e.g. corpus_doclabels.txt.

        Returns:
            Matplotlib heatmap figure.

        ToDo:
            * add colorbar
            * create figure dynamically?
                http://stackoverflow.com/questions/23058560/plotting-dynamic-data-using-matplotlib

        Note: Currently not in use due to dependencies
        """
        no_of_topics = self.model.num_topics
        no_of_docs = len(self.doc_labels)
        doc_topic = np.zeros((no_of_docs, no_of_topics))

        log.info("Accessing topic distribution and topic probability ...")
        for doc, i in zip(self.corpus, range(no_of_docs)):
            topic_dist = self.model.__getitem__(doc)
            for topic in topic_dist: # topic_dist is a list of tuples (topic_id, topic_prob)
                doc_topic[i][topic[0]] = topic[1]
        log.debug("Topic distribution and topic probability available.")

        log.info("Accessing plot labels ...")
        topic_labels = []
        for i in range(no_of_topics):
            topic_terms = [x[0] for x in self.model.show_topic(i, topn=3)] # show_topic() returns tuples (word_prob, word)
            topic_labels.append(" ".join(topic_terms))
        log.debug("%s plot labels available.", len(topic_labels))

        log.info("Creating heatmap figure ...")
        if no_of_docs > 20 or no_of_topics > 20:
            fig = plt.figure(figsize=(20,20))    # if many items, enlarge figure
        else:
            fig = plt.figure()
            ax = fig.add_subplot(1,1,1)
            ax.pcolor(doc_topic, norm=None, cmap='Reds')
            ax.set_yticks(np.arange(doc_topic.shape[0])+1.0)
            ax.set_yticklabels(self.doc_labels)
            ax.set_xticks(np.arange(doc_topic.shape[1])+0.5)
            ax.set_xticklabels(topic_labels, rotation='90')
            ax.invert_yaxis()
            fig.tight_layout()
            self.heatmap_vis = fig
            log.debug("Heatmap figure available.")

    def save_heatmap(self, path, filename='heatmap', ext='png', dpi=200):
        """Saves Matplotlib heatmap figure.

        The created visualization (e.g. with `make_heatmap()`) has to be
        transmitted as parameter.

        Args:
            heatmap: plt.figure created by ``matplotlib.pyplot``.
            path(str): Path to output folder. Defaults to global variable `path`.

        Returns:
            ~/out/corpus_heatmap.png

        Note: Currently not in use due to dependencies
        """
        log.info("Saving heatmap figure...")
        try:
            if not os.path.exists(path):
                os.makedirs(path)
            self.heatmap_vis.savefig(os.path.join(path, filename + '.' + ext), dpi=dpi)
            log.debug("Heatmap figure available at %s/%s.%s", path, filename, ext)
        except AttributeError:
            log.error("Run make_heatmap() before save_heatmp()")
            raise
        except FileNotFoundError:
            pass

    def make_interactive(self):
        """Generates interactive visualization from LDA model.

        The ingested data (e.g. with `load_gensim_output()`) has to be transmitted
        as parameters.

        Args:
            corpus: Corpus created by Gensim, e.g. corpus.mm.
            model: LDA model created by Gensim, e.g. corpus.lda.
            dictionary(dict): Dictionary created by Gensim, e.g. corpus.dict.

        Returns:
            pyLDAvis visualization.

        Note: Currently not in use due to dependencies
        """
        log.info("Accessing model, corpus and dictionary ...")
        self.interactive_vis = pyLDAvis.gensim.prepare(self.model, self.corpus, self.dictionary)
        log.debug("Interactive visualization available.")

    def save_interactive(self, path, filename='corpus_interactive'):
        """Saves interactive visualization.
        The created visualization (e.g. with `make_interactive()`) has to be
        transmitted as parameter.

        Args:
            vis: Interactive visualization created by pyLDAvis.
            path(str): Path to output folder. Defaults to global variable `path`.

        Returns:
            ~/out/corpus_interactive.html
            ~/out/corpus_interactive.json
        """
        try:
            if not os.path.exists(path):
                os.makedirs(path)
            log.info("Saving interactive visualization ...")
            pyLDAvis.save_html(self.interactive_vis, os.path.join(path, 'corpus_interactive.html'))
            pyLDAvis.save_json(self.interactive_vis, os.path.join(path, 'corpus_interactive.json'))
            pyLDAvis.prepared_data_to_html(self.interactive_vis)
            log.debug("Interactive visualization available at %s/corpus_interactive.html and %s/corpus_interactive.json", path, path)
        except AttributeError:
            log.error("Running make_interactive() before save_interactive() ...")
            raise
        except FileNotFoundError:
            pass

def create_doc_topic(corpus, model, doc_labels):
    # Adapted from code by Stefan Pernes
    """Creates a document-topic data frame.

    Args:
        Gensim corpus.
        Gensim model object.
        List of document labels.

    Returns:

    """
    no_of_topics = model.num_topics
    no_of_docs = len(doc_labels)
    doc_topic = np.zeros((no_of_docs, no_of_topics))

    for doc, i in zip(corpus, range(no_of_docs)):       # use document bow from corpus
        topic_dist = model.__getitem__(doc)             # to get topic distribution froom model
        for topic in topic_dist:                        # topic_dist is a list of tuples
            doc_topic[i][topic[0]] = topic[1]           # save topic probability

    topic_labels = []
    for i in range(no_of_topics):
        topic_terms = [x[0] for x in model.show_topic(i, topn=3)]  # show_topic() returns tuples (word_prob, word)
        topic_labels.append(" ".join(topic_terms))

    doc_topic = pd.DataFrame(doc_topic, index = doc_labels, columns = topic_labels)
    doc_topic = doc_topic.transpose()
    # TODO: Stupid construction grown out of quick code adaptations: rewrite the first loop to
    # get rid of the necessity to transpose the data frame!!!
    # TODO: 'visualization' is not the proper place for this function!

    return doc_topic

def doc_topic_heatmap(data_frame):
    # Adapted from code by Stefan Pernes and Allen Riddell
    """Plot documnet-topic distribution in a heat map.

    Args:
        Document-topic data frame.

    Returns:

    """
    data_frame = data_frame.transpose().sort_index()
    doc_labels = list(data_frame.index)
    topic_labels = list(data_frame)
    if len(doc_labels) > 20 or len(topic_labels) > 20: plt.figure(figsize=(20,20))    # if many items, enlarge figure
    plt.pcolor(data_frame, norm=None, cmap='Reds')
    plt.yticks(np.arange(data_frame.shape[0])+1.0, doc_labels)
    plt.xticks(np.arange(data_frame.shape[1])+0.5, topic_labels, rotation='90')
    plt.gca().invert_yaxis()
    plt.tight_layout()

    #plt.savefig(path+"/"+corpusname+"_heatmap.png") #, dpi=80)
    return plt

    # TODO: recode to get rid of transpose in the beginning


def plot_doc_topics(doc_topic, document_index):
    """Plot topic disctribution in a document.

    Args:
        Document-topic data frame.
        Index of the document to be shown.

    Returns:

    """
    data = doc_topic[list(doc_topic)[document_index]].copy()
    data = data[data != 0]
    data = data.sort_values()
    values = list(data)
    labels = list(data.index)

    plt.barh(range(len(values)), values, align = 'center', alpha=0.5)
    plt.yticks(range(len(values)), labels)
    plt.title(list(doc_topic)[document_index])
    plt.xlabel('Proportion')
    plt.ylabel('Topic')
    plt.tight_layout()
    return plt

#
# Work in progress following
#
def topicwords_in_df(model):
    pattern = regex.compile(r'\p{L}+\p{P}?\p{L}+')
    topics = []
    index = []
    for n, topic in enumerate(model.show_topics()):
        topics.append(pattern.findall(topic[1]))
        index.append("Topic " + str(n+1))
    df = pd.DataFrame(topics, index=index, columns=["Key " + str(x+1) for x in range(len(topics))])
    return df

def show_wordle_for_topic(model, topic_nr, words):
    """Plot wordle for a specific topic

    Args:
        model: Gensim LDA model
        topic_nr(int): Choose topic
        words (int): Number of words to show

    Note: Function does use wordcloud package -> https://pypi.python.org/pypi/wordcloud
         pip install wordcloud

    ToDo: Check if this function should be implemented

    """
    plt.figure()
    plt.imshow(WordCloud().fit_words(dict(model.show_topic(topic_nr, words))))
    plt.axis("off")
    plt.title("Topic #" + str(topic_nr + 1))
    return plt


def get_color_scale(word, font_size, position, orientation, font_path, random_state=None):
    """ Create color scheme for wordle."""
    return "hsl(245, 58%, 25%)" # Default. Uniform dark blue.
    #return "hsl(0, 00%, %d%%)" % random.randint(80, 100) # Greys for black background.
    #return "hsl(221, 65%%, %d%%)" % random.randint(30, 35) # Dark blues for white background

def get_topicRank(topic, topicRanksFile):
    #print("getting topic rank.")
    with open(topicRanksFile, "r") as infile:
        topicRanks = pd.read_csv(infile, sep=",", index_col=0)
        rank = int(topicRanks.iloc[topic]["Rank"])
        return rank

def read_mallet_word_weights(word_weights_file):
    """Reads Mallet output (topics with words and word weights) into dataframe."""
    word_scores = pd.read_table(word_weights_file, header=None, sep="\t")
    word_scores = word_scores.sort_values(columns=[0,2], axis=0, ascending=[True, False])
    word_scores_grouped = word_scores.groupby(0)
    return word_scores_grouped

def get_wordlewords(word_scores_grouped, number_of_top_words, topic_nr):
    """Transform Mallet output for wordle generation."""
    topic_word_scores = word_scores_grouped.get_group(topic_nr)
    top_topic_word_scores = topic_word_scores.iloc[0:number_of_top_words]
    topic_words = top_topic_word_scores.loc[:,1].tolist()
    print(topic_words)
    word_scores = top_topic_word_scores.loc[:,2].tolist()
    print(word_scores)
    wordlewords = ""
    j = 0
    for word in topic_words:
        word = word
        score = word_scores[j]
        j += 1
        wordlewords = wordlewords + ((word + " ") + str(score))
    return wordlewords

def plot_wordle_from_mallet(word_weights_file,
                            topic_nr,
                            number_of_top_words,
                            outfolder,
                            dpi):
    """Generate wordles from Mallet output, using the wordcloud module."""

    word_scores_grouped = read_mallet_word_weights(word_weights_file)
    text = get_wordlewords(word_scores_grouped, number_of_top_words, topic_nr)
    print(text)
    wordcloud = WordCloud(width=600, height=400, background_color="white", margin=4).generate(text)
    default_colors = wordcloud.to_array()
    figure_title = "topic "+ str(topic_nr)
    plt.imshow(default_colors)
    plt.imshow(wordcloud)
    plt.title(figure_title, fontsize=30)
    plt.axis("off")

    ## Saving the image file.
    if not os.path.exists(outfolder):
        os.makedirs(outfolder)

    figure_filename = "wordle_tp"+"{:03d}".format(topic_nr) + ".png"
    plt.savefig(outfolder + figure_filename, dpi=dpi)
    return plt

def plot_wordle_from_lda(model, vocab, topic_nr, words, height, width):
    topic_dist = model.topic_word_[topic_nr]
    topic_words = np.array(vocab)[np.argsort(topic_dist)][:-words:-1]
    token_value = {}
    for token, value in zip(topic_words, topic_dist[:-words:-1]):
        token_value.update({token: value})
    return WordCloud(background_color='white', height=height, width=width).fit_words(token_value)


def doc_topic_heatmap_interactive(doc_topics):
    score = []
    for x in doc_topics.apply(tuple):
        score.extend(x)
    data = {
      'Topic': list(doc_topics.index) * len(doc_topics.columns),
      'Document':  [item for item in list(doc_topics.columns) for i in range(len(doc_topics.index))],
      'Score':   score
    }
    return HeatMap(data, x='Topic', y='Document',values='Score', stat=None, legend=False)
