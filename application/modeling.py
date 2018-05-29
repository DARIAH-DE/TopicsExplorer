import application
import dariah_topics
import pathlib
import logging
import lda
import time
import flask
import random
import shutil
import sys
import numpy as np
import pandas as pd
import bokeh.plotting
import bokeh.embed
import werkzeug.utils


def lda_modeling(document_term_arr, n_topics, n_iter, tempdir):
    """
    Trains an LDA topic model and writes logging to a file.
    """
    filepath = str(pathlib.Path(tempdir, "topicmodeling.log"))
    handler = logging.FileHandler(filepath, "w")
    lda_log = logging.getLogger("lda")
    lda_log.setLevel(logging.INFO)
    lda_log.addHandler(handler)
    model = lda.LDA(n_topics=n_topics, n_iter=n_iter)
    model.fit(document_term_arr)
    with open(filepath, "a", encoding="utf-8") as f:
        f.write("DONE")
    return model


def workflow(tempdir, archive_dir):
    """
    Collects the user input, preprocesses the corpus, trains the LDA model,
    creates visualizations, and dumps generated data.
    """
    try:
        start = time.time()
        user_input = {"files": flask.request.files.getlist("files"),
                      "num_topics": int(flask.request.form["num_topics"]),
                      "num_iterations": int(flask.request.form["num_iterations"])}

        if flask.request.files.get("stopword_list", None):
            yield "running", "Collecting external stopwords list ...", "", "", "", "", ""
            user_input["stopwords"] = flask.request.files["stopword_list"]
        else:
            yield "running", "Collecting threshold value for stopwords ...", "", "", "", "", ""
            user_input["mfw"] = int(flask.request.form["mfw_threshold"])

        parameter = pd.Series()
        parameter["Corpus size, in documents"] = len(user_input["files"])
        parameter["Corpus size (raw), in tokens"] = 0

        if len(user_input["files"]) < 5:
            raise Exception("Your corpus is too small. Please select at least five text files.")

        yield "running", "Reading and tokenizing corpus ...", "", "", "", "", ""
        tokenized_corpus = pd.Series()
        for file in user_input["files"]:
            filename = pathlib.Path(werkzeug.utils.secure_filename(file.filename))
            yield "running", "Reading {0} ...".format(filename.stem), "", "", "", "", ""
            text = file.read().decode("utf-8")
            if filename.suffix != ".txt":
                yield "running", "Removing markup from text ...", "", "", "", "", ""
                text = application.utils.remove_markup(text)
            yield "running", "Tokenizing {0} ...".format(filename.stem), "", "", "", "", ""
            tokens = list(dariah_topics.preprocessing.tokenize(text))
            tokenized_corpus[filename.stem] = tokens
            parameter["Corpus size (raw), in tokens"] += len(tokens)
            file.flush()
        
        excerpt_int = random.randint(0, len(tokenized_corpus) - 1)
        excerpt = tokenized_corpus.iloc[excerpt_int]
        token_int = random.randint(1, len(excerpt) - 71)
        excerpt = "..." + " ".join(excerpt[token_int:token_int + 70]) + "..."

        yield "running", "Creating document-term matrix ...", excerpt, "", "", "", ""
        document_labels = tokenized_corpus.index
        document_term_matrix = dariah_topics.preprocessing.create_document_term_matrix(tokenized_corpus, document_labels)

        yield "running", "Determining corpus statistics ...", excerpt, "", "", "", ""
        group = ["Document size (raw)" for i in range(parameter["Corpus size, in documents"])]
        corpus_stats = pd.DataFrame({"score": np.array(document_term_matrix.sum(axis=1)),
                                     "group": group})

        corpus_size = len(user_input["files"])
        token_size = parameter["Corpus size (raw), in tokens"]
        topic_size = user_input["num_topics"]
        iteration_size = user_input["num_iterations"]

        yield "running", "Removing stopwords and hapax legomena from corpus ...", excerpt, corpus_size, token_size, topic_size, iteration_size
        try:
            yield "running", "Determining {0} most frequent words from corpus ...".format(user_input["mfw"]), "", "", "", "", ""
            stopwords = dariah_topics.preprocessing.find_stopwords(document_term_matrix, user_input["mfw"])
            cleaning = "removed the <b>{0} most frequent words</b>, based on a threshold value".format(user_input["mfw"])
        except KeyError:
            yield "running", "Reading external stopwords list ...", "", "", "", "", ""
            stopwords = user_input["stopwords"].read().decode("utf-8")
            stopwords = list(dariah_topics.preprocessing.tokenize(stopwords))
            cleaning = "removed <b>{0} words</b>, based on an external stopwords list".format(len(stopwords))
        
        yield "running", "Determining hapax legomena from corpus ...", "", "", "", "", ""
        hapax_legomena = dariah_topics.preprocessing.find_hapax_legomena(document_term_matrix)
        features = set(stopwords).union(hapax_legomena)
        features = [token for token in features if token in document_term_matrix.columns]
        yield "running", "Removing a total of {0} words from your corpus ...".format(len(features)), "", "", "", "", ""
        document_term_matrix = document_term_matrix.drop(features, axis=1)

        yield "running", "Determining corpus statistics ...", "", "", "", "", ""
        group = ["Document size (clean)" for n in range(parameter["Corpus size, in documents"])]
        corpus_stats = corpus_stats.append(pd.DataFrame({"score": np.array(document_term_matrix.sum(axis=1)),
                                                         "group": group}))
        parameter["Corpus size (clean), in tokens"] = int(document_term_matrix.values.sum())

        yield "running", "Accessing the values of the document-term matrix ...", "", "", "", "", ""
        document_term_arr = document_term_matrix.values.astype(int)
        yield "running", "Accessing the vocabulary of the corpus ...", "", "", "", "", ""
        vocabulary = document_term_matrix.columns

        parameter["Size of vocabulary, in tokens"] = len(vocabulary)
        parameter["Number of topics"] = user_input["num_topics"]
        parameter["Number of iterations"] = user_input["num_iterations"]

        yield "running", "Initializing LDA topic model (this step might take a while) ...", "", "", "", "", ""
        model = application.utils.enthread(target=lda_modeling,
                                           args=(document_term_arr,
                                                 user_input["num_topics"],
                                                 user_input["num_iterations"],
                                                 tempdir))
        while True:
            # During modeling the logfile is read continuously and the newest
            # line is sent to the UI as information for the user:
            msg = application.utils.read_logfile(str(pathlib.Path(tempdir, "topicmodeling.log")))
            if msg == None:
                # When modeling is done, get the model:
                model = model.get()
                break
            else:
                yield "running", msg, "", "", "", "", ""
        
        yield "running", "Determining the log-likelihood for the last iteration ...", "", "", "", "", ""
        parameter["The model log-likelihood"] = round(model.loglikelihood())

        yield "running", "Accessing topics ...", "", "", "", "", ""
        topics = dariah_topics.postprocessing.show_topics(model=model,
                                                          vocabulary=vocabulary,
                                                          num_keys=8)
        topics.columns = ["Key {0}".format(i) for i in range(1, 9)]
        topics.index = ["Topic {0}".format(i) for i in range(1, user_input["num_topics"] + 1)]

        yield "running", "Accessing document-topics distribution ...", "", "", "", "", ""
        document_topics = dariah_topics.postprocessing.show_document_topics(model=model,
                                                                            topics=topics,
                                                                            document_labels=document_labels)

        yield "running", "Creating visualizations ...", "", "", "", "", ""
        if document_topics.shape[0] < document_topics.shape[1]:
            if document_topics.shape[1] < 20:
                height = 20 * 28
            else:
                height = document_topics.shape[1] * 28
            document_topics_heatmap = document_topics.T
        else:
            if document_topics.shape[0] < 20:
                height = 20 * 28
            else:
                height = document_topics.shape[0] * 28
            document_topics_heatmap = document_topics

        yield "running", "Creating heatmap for document-topics distribution ...", "", "", "", "", ""
        fig = dariah_topics.visualization.PlotDocumentTopics(document_topics_heatmap)
        heatmap = fig.interactive_heatmap(height=height,
                                          sizing_mode="scale_width",
                                          tools="hover, pan, reset, wheel_zoom, zoom_in, zoom_out, save")
        #bokeh.plotting.output_file(str(pathlib.Path(tempdir, "heatmap.html")))
        #bokeh.plotting.save(heatmap)

        heatmap_script, heatmap_div = bokeh.embed.components(heatmap)

        yield "running", "Creating boxplot for corpus statistics ...", "", "", "", "", ""
        corpus_boxplot = application.utils.boxplot(corpus_stats)
        corpus_boxplot_script, corpus_boxplot_div = bokeh.embed.components(corpus_boxplot)
        #bokeh.plotting.output_file(str(pathlib.Path(tempdir, "corpus_statistics.html")))
        #bokeh.plotting.save(corpus_boxplot)

        if document_topics.shape[1] < 15:
            height = 580
        else:
            height = document_topics.shape[1] * 25
        yield "running", "Creating barchart for topic-documents distribution ...", "", "", "", "", ""
        topics_barchart = application.utils.barchart(document_topics, height=height, topics=topics)
        topics_script, topics_div = bokeh.embed.components(topics_barchart)
        #bokeh.plotting.output_file(str(pathlib.Path(tempdir, "topics_barchart.html")))
        #bokeh.plotting.save(topics_barchart)

        if document_topics.shape[0] < 15:
            height = 580
        else:
            height = document_topics.shape[0] * 25
        yield "running", "Creating barchart for document-topics distribution ...", "", "", "", "", ""
        documents_barchart = application.utils.barchart(document_topics.T, height=height)
        documents_script, documents_div = bokeh.embed.components(documents_barchart)
        #bokeh.plotting.output_file(str(pathlib.Path(tempdir, "document_topics_barchart.html")))
        #bokeh.plotting.save(documents_barchart)

        end = time.time()
        passed_time = round((end - start) / 60)

        if passed_time == 0:
            parameter["Passed time, in seconds"] = round(end - start)
        else:
            parameter["Passed time, in minutes"] = passed_time

        yield "running", "Dumping generated data ...", "", "", "", "", ""
        parameter = pd.DataFrame(pd.Series(parameter))
        topics.to_csv(str(pathlib.Path(tempdir, "topics.csv")), encoding="utf-8", sep=';')
        document_topics.to_csv(str(pathlib.Path(tempdir, "document_topics.csv")), encoding="utf-8", sep=';')
        parameter.to_csv(str(pathlib.Path(tempdir, "parameter.csv")), encoding="utf-8", sep=';')
        
        yield "running", "Making generated data ready for download ...", "", "", "", "", ""
        archive = str(pathlib.Path(archive_dir, "topicmodeling"))
        shutil.make_archive(archive, "zip", tempdir)

        data = {"cleaning": cleaning,
                "bokeh_resources": "include",
                "heatmap_script": heatmap_script,
                "heatmap_div": heatmap_div,
                "topics_script": topics_script,
                "topics_div": topics_div,
                "documents_script": documents_script,
                "documents_div": documents_div,
                "corpus_boxplot_script": corpus_boxplot_script,
                "corpus_boxplot_div": corpus_boxplot_div,
                "first_topic": list(document_topics.index)[0],
                "first_document": list(document_topics.columns)[0]}
        yield "running", "Everything went well! The results page is currently being created ...", "", "", "", "", ""
        application.utils.compress(data, str(pathlib.Path(tempdir, "data.pickle")))
        yield "done"
    except Exception as error:
        yield "error", str(error)