import application
import dariah_topics
import pathlib
import logging
import lda
import time
import flask
import shutil
import sys
import numpy as np
import pandas as pd
import bokeh.plotting
import bokeh.embed
import werkzeug.utils


# These messages are displayed during modeling:
INFO_2A = "FYI: This might take a while..."
INFO_3A = "In the meanwhile, have a look at"
INFO_4A = "our Jupyter notebook introducing"
INFO_5A = "topic modeling with MALLET."


def lda_modeling(document_term_arr, n_topics, n_iter, tempdir):
    """
    Trains an LDA topic model and writes logging to a file.
    """
    file = str(pathlib.Path(tempdir, 'topicmodeling.log'))
    handler = logging.FileHandler(file, 'w')
    lda_log = logging.getLogger('lda')
    lda_log.setLevel(logging.INFO)
    lda_log.addHandler(handler)

    model = lda.LDA(n_topics=n_topics, n_iter=n_iter)
    model.fit(document_term_arr)
    with open(file, 'a', encoding='utf-8') as f:
        f.write('DONE')
    return model


def workflow(tempdir, archive_dir):
    """
    Collects the user input, preprocesses the corpus, trains the LDA model,
    creates visualizations, and dumps generated data.
    """
    try:
        start = time.time()
        user_input = {'files': flask.request.files.getlist('files'),
                      'num_topics': int(flask.request.form['num_topics']),
                      'num_iterations': int(flask.request.form['num_iterations'])}

        if flask.request.files.get('stopword_list', None):
            user_input['stopwords'] = flask.request.files['stopword_list']
        else:
            user_input['mfw'] = int(flask.request.form['mfw_threshold'])

        parameter = pd.Series()
        parameter['Corpus size, in documents'] = len(user_input['files'])
        parameter['Corpus size (raw), in tokens'] = 0

        if len(user_input['files']) < 5:
            raise Exception("Your corpus is too small. Please select at least five text files.")

        yield "running", "Reading and tokenizing corpus ...", INFO_2A, INFO_3A, INFO_4A, INFO_5A
        tokenized_corpus = pd.Series()
        for file in user_input['files']:
            filename = pathlib.Path(werkzeug.utils.secure_filename(file.filename))
            text = file.read().decode('utf-8')
            if filename.suffix != '.txt':
                text = application.utils.remove_markup(text)
            tokens = list(dariah_topics.preprocessing.tokenize(text))
            tokenized_corpus[filename.stem] = tokens
            parameter['Corpus size (raw), in tokens'] += len(tokens)
            file.flush()

        yield "running", "Creating document-term matrix ...", INFO_2A, INFO_3A, INFO_4A, INFO_5A
        document_labels = tokenized_corpus.index
        document_term_matrix = dariah_topics.preprocessing.create_document_term_matrix(tokenized_corpus, document_labels)

        group = ['Document size (raw)' for i in range(parameter['Corpus size, in documents'])]
        corpus_stats = pd.DataFrame({'score': np.array(document_term_matrix.sum(axis=1)),
                                     'group': group})

        yield "running", "Removing stopwords and hapax legomena from corpus ...", INFO_2A, INFO_3A, INFO_4A, INFO_5A
        try:
            stopwords = dariah_topics.preprocessing.find_stopwords(document_term_matrix, user_input['mfw'])
            cleaning = "removed the <b>{0} most frequent words</b>, based on a threshold".format(len(stopwords))
        except KeyError:
            stopwords = user_input['stopwords'].read().decode('utf-8')
            stopwords = dariah_topics.preprocessing.tokenize(stopwords)
            cleaning = "removed the <b>{0} most frequent words</b>, based on an external stopwords list".format(len(stopwords))
        hapax_legomena = dariah_topics.preprocessing.find_hapax_legomena(document_term_matrix)
        features = set(stopwords).union(hapax_legomena)
        features = [token for token in features if token in document_term_matrix.columns]
        document_term_matrix = document_term_matrix.drop(features, axis=1)

        group = ['Document size (clean)' for n in range(parameter['Corpus size, in documents'])]
        corpus_stats = corpus_stats.append(pd.DataFrame({'score': np.array(document_term_matrix.sum(axis=1)),
                                                         'group': group}))

        parameter['Corpus size (clean), in tokens'] = int(document_term_matrix.values.sum())

        document_term_arr = document_term_matrix.as_matrix().astype(int)
        vocabulary = document_term_matrix.columns

        parameter['Size of vocabulary, in tokens'] = len(vocabulary)
        parameter['Number of topics'] = user_input['num_topics']
        parameter['Number of iterations'] = user_input['num_iterations']

        # These messages are displayed during modeling:
        INFO_1B = "Iteration {0} of {1} ..."
        INFO_2B = "You have selected {0} text files,"
        INFO_3B = "containing {0} tokens,"
        INFO_4B = "and {0} unique types"
        INFO_5B = "to uncover {0} topics."
        INFO_2B = INFO_2B.format(parameter['Corpus size, in documents'])
        INFO_3B = INFO_3B.format(parameter['Corpus size (raw), in tokens'])
        INFO_4B = INFO_4B.format(parameter['Size of vocabulary, in tokens'])
        INFO_5B = INFO_5B.format(parameter['Number of topics'])

        yield "running", "Initializing LDA topic model ...", INFO_2B, INFO_3B, INFO_4B, INFO_5B
        model = application.utils.enthread(target=lda_modeling,
                                           args=(document_term_arr,
                                                 user_input['num_topics'],
                                                 user_input['num_iterations'],
                                                 tempdir))
        while True:
            # During modeling the logfile is read continuously and the newest
            # line is sent to the browser as information for the user:
            msg = application.utils.read_logfile(str(pathlib.Path(tempdir, 'topicmodeling.log')))
            if msg == None:
                # When modeling is done, get the model:
                model = model.get()
                break
            else:
                yield "running", INFO_1B.format(msg, parameter['Number of iterations']), INFO_2B, INFO_3B, INFO_4B, INFO_5B

        parameter['The model log-likelihood'] = round(model.loglikelihood())

        yield "running", "Accessing topics ...", INFO_2B, INFO_3B, INFO_4B, INFO_5B
        topics = dariah_topics.postprocessing.show_topics(model=model,
                                                          vocabulary=vocabulary,
                                                          num_keys=8)
        topics.columns = ['Key {0}'.format(i) for i in range(1, 9)]
        topics.index = ['Topic {0}'.format(i) for i in range(1, user_input['num_topics'] + 1)]

        yield "running", "Accessing document topics distributions ...", INFO_2B, INFO_3B, INFO_4B, INFO_5B
        document_topics = dariah_topics.postprocessing.show_document_topics(model=model,
                                                                            topics=topics,
                                                                            document_labels=document_labels)

        yield "running", "Creating visualizations ...", INFO_2B, INFO_3B, INFO_4B, INFO_5B
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

        fig = dariah_topics.visualization.PlotDocumentTopics(document_topics_heatmap)
        heatmap = fig.interactive_heatmap(height=height,
                                          sizing_mode='scale_width',
                                          tools='hover, pan, reset, wheel_zoom, zoom_in, zoom_out')

        yield "running", "Dumping generated data ...", INFO_2B, INFO_3B, INFO_4B, INFO_5B

        bokeh.plotting.output_file(str(pathlib.Path(tempdir, 'heatmap.html')))
        bokeh.plotting.save(heatmap)

        heatmap_script, heatmap_div = bokeh.embed.components(heatmap)

        corpus_boxplot = application.utils.boxplot(corpus_stats)
        corpus_boxplot_script, corpus_boxplot_div = bokeh.embed.components(corpus_boxplot)
        bokeh.plotting.output_file(str(pathlib.Path(tempdir, 'corpus_statistics.html')))
        bokeh.plotting.save(corpus_boxplot)

        if document_topics.shape[1] < 10:
            height = 10 * 30
        else:
            height = document_topics.shape[1] * 30
        topics_barchart = application.utils.barchart(document_topics, height=height, topics=topics)
        topics_script, topics_div = bokeh.embed.components(topics_barchart)
        bokeh.plotting.output_file(str(pathlib.Path(tempdir, 'topics_barchart.html')))
        bokeh.plotting.save(topics_barchart)

        if document_topics.shape[0] < 10:
            height = 10 * 30
        else:
            height = document_topics.shape[0] * 30
        documents_barchart = application.utils.barchart(document_topics.T, height=height)
        documents_script, documents_div = bokeh.embed.components(documents_barchart)
        bokeh.plotting.output_file(str(pathlib.Path(tempdir, 'document_topics_barchart.html')))
        bokeh.plotting.save(documents_barchart)

        end = time.time()
        passed_time = round((end - start) / 60)

        if passed_time == 0:
            parameter['Passed time, in seconds'] = round(end - start)
        else:
            parameter['Passed time, in minutes'] = passed_time

        parameter = pd.DataFrame(pd.Series(parameter))
        topics.to_csv(str(pathlib.Path(tempdir, 'topics.csv')), encoding='utf-8')
        document_topics.to_csv(str(pathlib.Path(tempdir, 'document_topics.csv')), encoding='utf-8')
        parameter.to_csv(str(pathlib.Path(tempdir, 'parameter.csv')), encoding='utf-8')

        shutil.make_archive(str(pathlib.Path(archive_dir, 'topicmodeling')), 'zip', tempdir)
        data = {'cleaning': cleaning,
                'bokeh_resources': 'include',
                'heatmap_script': heatmap_script,
                'heatmap_div': heatmap_div,
                'topics_script': topics_script,
                'topics_div': topics_div,
                'documents_script': documents_script,
                'documents_div': documents_div,
                'corpus_boxplot_script': corpus_boxplot_script,
                'corpus_boxplot_div': corpus_boxplot_div}
        application.utils.compress(data, str(pathlib.Path(tempdir, 'data.pickle')))
        yield 'done', '', '', '', '', ''
    except Exception as error:
        yield 'error', str(error), '', '', '', ''
