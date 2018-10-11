
import flask
import cophi



def workflow():
    # Fetch user input:
    data = get_forms("files", "num_topics", "num_iterations")
    # Get Document objects:
    documents = get_documents(data["files"])
    # Construct Corpus object:
    corpus = get_corpus(documents)
    # Get stopwords:
    stopwords = get_stopwords(data, corpus)
    # Get hapax legomena:
    hapax = get_hapax(corpus)
    # Construct features to drop:
    features = get_features(corpus, stopwords, hapax)
    # Clean corpus:
    corpus = get_clean_corpus(corpus, features)


def get_forms(files, num_topics, num_iterations):
    """Get forms values.
    """
    logging.info("Fetching input data...")
    data = {"files": flask.request.files.getlist(files),
            "num_topics": int(flask.request.form[num_topics]),
            "num_iterations": int(flask.request.form[num_iterations])}
    if flask.request.files.get("stopwords", None):
        data["stopwords"] = flask.request.files["stopwords"]
    else:
        data["mfw"] = int(flask.request.form["mfw"])
    return data


def get_documents(textfiles):
    logging.info("Start processing text files...")
    for textfile in textfiles:
        filepath = pathlib.Path(werkzeug.utils.secure_filename(textfile.filename))
        title = filepath.stem
        logging.info("Reading {}...".format(title))
        suffix = filepath.suffix
        content = textfile.read().decode("utf-8")
        # REMOVE MARKUP
        yield cophi.model.Document(content, title)


def get_corpus(documents):
    logging.info("Constructing document-term matrix...")
    return cophi.model.Corpus(documents)


def get_stopwords(data, corpus):
    logging.info("Fetching stopwords...")
    try:
        threshold = data["mfw"]
        logging.info("Getting the {} most frequent words...".format(threshold))
        stopwords = corpus.mfw(threshold)
    except KeyError:
        logging.info("Reading external stopwords list...")
        textfile = data["stopwords"].read().decode("utf-8")
        stopwords = textfile.split("\n")
    return stopwords


def get_hapax(corpus):
    logging.info("Fetching hapax legomena...")
    return corpus.hapax()


def get_features(corpus, stopwords, hapax):
    logging.info("Constructing a list of features to drop...")
    features = set(stopwords).union(hapax)
    return [feature for feature in features if feature in corpus.dtm.vocabulary]

def get_clean_corpus(corpus, features):
    logging.info("Cleaning corpus...")
    return corpus.drop(corpus.dtm, features)




        
        progress += user_input["num_iterations"] + 1
        yield "running", "Determining model log-likelihood ...", progress / complete * 100, "", "", "", "", ""
        parameter["The model log-likelihood"] = round(model.loglikelihood())

        progress += 1
        yield "running", "Accessing topics ...", progress / complete * 100, "", "", "", "", ""
        topics = dariah_topics.postprocessing.show_topics(model=model,
                                                          vocabulary=vocabulary,
                                                          num_keys=8)
        topics.columns = ["Key {0}".format(i) for i in range(1, 9)]
        topics.index = ["Topic {0}".format(i) for i in range(1, user_input["num_topics"] + 1)]

        progress += 1
        yield "running", "Accessing distributions ...", progress / complete * 100, "", "", "", "", ""
        document_topics = dariah_topics.postprocessing.show_document_topics(model=model,
                                                                            topics=topics,
                                                                            document_labels=document_labels)
        
        progress += 1
        yield "running", "Creating visualizations ...", progress / complete * 100, "", "", "", "", ""
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

        progress += 1
        yield "running", "Creating heatmap ...", progress / complete * 100, "", "", "", "", ""
        fig = dariah_topics.visualization.PlotDocumentTopics(document_topics_heatmap)
        heatmap = fig.interactive_heatmap(height=height,
                                          sizing_mode="scale_width",
                                          tools="hover, pan, reset, wheel_zoom, zoom_in, zoom_out")
        bokeh.plotting.output_file(str(pathlib.Path(tempdir, "heatmap.html")))
        bokeh.plotting.save(heatmap)

        heatmap_script, heatmap_div = bokeh.embed.components(heatmap)

        progress += 1
        yield "running", "Creating boxplot ...", progress / complete * 100, "", "", "", "", ""
        corpus_boxplot = application.utils.boxplot(corpus_stats)
        corpus_boxplot_script, corpus_boxplot_div = bokeh.embed.components(corpus_boxplot)
        bokeh.plotting.output_file(str(pathlib.Path(tempdir, "corpus_statistics.html")))
        bokeh.plotting.save(corpus_boxplot)

        if document_topics.shape[1] < 15:
            height = 580
        else:
            height = document_topics.shape[1] * 25
        
        progress += 1
        yield "running", "Creating barcharts ...", progress / complete * 100, "", "", "", "", ""
        topics_barchart = application.utils.barchart(document_topics, height=height, topics=topics)
        topics_script, topics_div = bokeh.embed.components(topics_barchart)
        bokeh.plotting.output_file(str(pathlib.Path(tempdir, "topics_barchart.html")))
        bokeh.plotting.save(topics_barchart)

        if document_topics.shape[0] < 15:
            height = 580
        else:
            height = document_topics.shape[0] * 25
        documents_barchart = application.utils.barchart(document_topics.T, height=height)
        documents_script, documents_div = bokeh.embed.components(documents_barchart)
        bokeh.plotting.output_file(str(pathlib.Path(tempdir, "document_topics_barchart.html")))
        bokeh.plotting.save(documents_barchart)

        end = time.time()
        passed_time = round((end - start) / 60)

        if passed_time == 0:
            parameter["Passed time, in seconds"] = round(end - start)
        else:
            parameter["Passed time, in minutes"] = passed_time

        progress += 1
        yield "running", "Dumping generated data ...", progress / complete * 100, "", "", "", "", ""
        parameter = pd.DataFrame(pd.Series(parameter))
        topics.to_csv(str(pathlib.Path(tempdir, "topics.csv")), encoding="utf-8", sep=";")
        document_topics.to_csv(str(pathlib.Path(tempdir, "document_topics.csv")), encoding="utf-8", sep=";")
        parameter.to_csv(str(pathlib.Path(tempdir, "parameter.csv")), encoding="utf-8", sep=";")
        
        progress += 1
        yield "running", "Zipping generated data ...", progress / complete * 100, "", "", "", "", ""
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
        
        progress = complete
        yield "running", "Building results page ...", progress / complete * 100, "", "", "", "", ""
        application.utils.compress(data, str(pathlib.Path(tempdir, "data.pickle")))
        yield "done", "", progress / complete * 100, "", "", "", "", ""
    except UnicodeDecodeError:
        message = "There must be something wrong in one or more of your text files. "\
                  "Maybe not encoded in UTF-8? Or, maybe an unsupported file format? "\
                  "You can use only plain text and XML."
        yield "error", message, "", "", "", "", "", ""
    except Exception as error:
        yield "error", str(error), "", "", "", "", "", ""