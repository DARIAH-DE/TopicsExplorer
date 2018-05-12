import pickle
import time
import regex as re
import pathlib
import bokeh.plotting
import bokeh.models
import bokeh.layouts
import pandas as pd
import threading
import lxml
import queue
import socket
import random


TOOLS = "hover, pan, reset, wheel_zoom, zoom_in, zoom_out"
JAVASCRIPT = """
             var f = cb_obj.value;
             var options = %s;
             f = f.replace(/[!\"#$&\'()*+,-.:;<=>?@^_`{}~]/g, "");
             f = f.replace(/\s/g, "");

             for (var i in options) {
                 if (f == options[i]) {
                     console.log("Visible: " + options[i])
                     eval(options[i]).visible = true;
                 }
                 else {
                     console.log("Unvisible: " + options[i])
                     eval(options[i]).visible = false;
                 }
             }
             """


def compress(data, filepath):
    """
    Dumps generated data.
    """
    with open(filepath, 'wb') as file:
        pickle.dump(data, file)


def decompress(filepath):
    """
    Loads dumped data.
    """
    with open(filepath, 'rb') as file:
        return pickle.load(file)


def load_data(tempdir):
    """
    Loads the generated data.
    """
    data_path = str(pathlib.Path(tempdir, 'data.pickle'))
    parameter_path = str(pathlib.Path(tempdir, 'parameter.csv'))
    topics_path = str(pathlib.Path(tempdir, 'topics.csv'))

    data = decompress(data_path)
    parameter = pd.read_csv(parameter_path, index_col=0, encoding='utf-8')
    parameter.columns = ['']  # remove column names
    topics = pd.read_csv(topics_path, index_col=0, encoding='utf-8')

    data['parameter'] = [parameter.to_html(classes='parameter', border=0)]
    data['topics'] = [topics.to_html(classes='topics')]
    return data


def remove_markup(content):
    """
    Removes markup from text. If lxml fails, a simple regex is used.
    """
    try:
        parser = lxml.etree.XMLParser(recover=True)
        tree = lxml.etree.parse(content, parser=parser)
        ns = dict(tei='http://www.tei-c.org/ns/1.0')
        lxml.etree.strip_elements(tree, 'speaker', with_tail=False)
        lxml.etree.strip_elements(tree, 'note', with_tail=False)
        lxml.etree.strip_elements(tree, 'stage', with_tail=False)
        lxml.etree.strip_elements(tree, 'head', with_tail=False)
        text = tree.xpath('//text()')
        text = '\n'.join(text)
        text = re.sub('  ', '', text)
        text = re.sub('    ', '', text)
        text = re.sub('\n{1,6}', '\n', text)
        text = re.sub('\n \n', '\n', text)
        text = re.sub('\t\n', '', text)
        return text
    except:
        text = []
        for line in content:
            line = re.sub('<.*?>', '', line)
            line = re.sub('(<.[^(><.)]+>)|<.?>', '', line)
            line = re.sub('\\n', '', line)
            line = re.sub('[ ]{2,}', ' ', line)
            line = re.sub('<?(.*?)?>', '', line)
            text.append(line)
        return ''.join(text)


def boxplot(stats):
    """
    Creates a boxplot for corpus statistics.
    """
    x_labels = ['Document size (clean)', 'Document size (raw)']

    groups = stats.groupby('group')
    q1 = groups.quantile(q=0.25)
    q2 = groups.quantile(q=0.5)
    q3 = groups.quantile(q=0.75)
    iqr = q3 - q1
    upper = q3 + 1.5 * iqr
    lower = q1 - 1.5 * iqr

    def outliers(group):
        cat = group.name
        return group[(group.score > upper.loc[cat]['score']) |
                     (group.score < lower.loc[cat]['score'])]['score']
    out = groups.apply(outliers).dropna()

    fig = bokeh.plotting.figure(tools='', background_fill_color='#EFE8E2',
                                title='', x_range=x_labels, logo=None,
                                sizing_mode='fixed', plot_width=500,
                                plot_height=350)

    qmin = groups.quantile(q=0.00)
    qmax = groups.quantile(q=1.00)
    upper.score = [min([x, y]) for (x, y) in zip(list(qmax.loc[:, 'score']), upper.score)]
    lower.score = [max([x, y]) for (x, y) in zip(list(qmin.loc[:, 'score']), lower.score)]

    fig.segment(x_labels, upper.score, x_labels, q3.score, line_color='black')
    fig.segment(x_labels, lower.score, x_labels, q1.score, line_color='black')

    fig.vbar(x_labels, 0.7, q2.score, q3.score, fill_color='#729fcf', line_color='black')
    fig.vbar(x_labels, 0.7, q1.score, q2.score, fill_color='#729fcf', line_color='black')

    fig.rect(x_labels, lower.score, 0.2, 0.01, line_color='black')
    fig.rect(x_labels, upper.score, 0.2, 0.01, line_color='black')

    fig.yaxis.axis_label = 'Tokens'
    fig.xgrid.grid_line_color = None
    fig.ygrid.grid_line_color = 'white'
    fig.grid.grid_line_width = 2
    fig.xaxis.major_label_text_font_size = '11pt'
    fig.yaxis.major_label_text_font_size = '9pt'
    return fig


def barchart(document_topics, height, topics=None, script=JAVASCRIPT, tools=TOOLS):
    """
    Creates an interactive barchart for document-topics proportions.
    """
    y_range = document_topics.columns.tolist()
    fig = bokeh.plotting.figure(y_range=y_range, plot_height=height, tools=tools,
                                toolbar_location='right', sizing_mode='scale_width',
                                logo=None)

    plots = {}
    options = document_topics.index.tolist()
    for i, option in enumerate(options):
        x_axis = document_topics.loc[option]
        source = bokeh.models.ColumnDataSource(dict(Describer=y_range, Proportion=x_axis))
        option = re.sub(' ', '_', option)
        bar = fig.hbar(y='Describer', right='Proportion', source=source,
                       height=0.5, color='#053967')
        if i == 0:
            bar.visible = True
        else:
            bar.visible = False
        plots[exclude_punctuations(option)] = bar

    fig.xgrid.grid_line_color = None
    fig.x_range.start = 0
    fig.select_one(bokeh.models.HoverTool).tooltips = [('Proportion', '@Proportion')]
    fig.xaxis.axis_label = 'Proportion'
    fig.xaxis.major_label_text_font_size = '9pt'
    fig.yaxis.major_label_text_font_size = '9pt'

    options = list(plots.keys())
    callback = bokeh.models.CustomJS(args=plots, code=script % options)

    if len(options) < 11:
        auto_warning = 'not'
        if topics is not None:
            selection = [' '.join(topics.iloc[i].tolist()) + ' ...' for i in range(topics.shape[0])]
            menu = [(select, option) for select, option in zip(selection, options)]
            label = "Select topic to display proportions"
        else:
            menu = [(select, option) for select, option in zip(document_topics.index, options)]
            label = "Select document to display proportions"
        dropdown = bokeh.models.widgets.Dropdown(label=label, menu=menu, callback=callback)
        return bokeh.layouts.column(dropdown, fig, sizing_mode='scale_width'), auto_warning
    else:
        auto_warning = 'include'
        if topics is not None:
            what = 'topic'
        else:
            what = 'document'
        textfield = bokeh.models.widgets.AutocompleteInput(completions=document_topics.index.tolist(),
                                                           placeholder="Type a {} name".format(what),
                                                           css_classes=['customTextInput'],
                                                           callback=callback)
        return bokeh.layouts.row(fig, textfield, sizing_mode='scale_width'), auto_warning


def read_logfile(logfile):
    """
    Reads a logfile and returns the current number of iterations.
    """
    time.sleep(3)
    pattern = re.compile('-?\d+')
    with open(logfile, 'r', encoding='utf-8') as file:
        text = file.readlines()
        line = text[-1][:-1]

        if 'likelihood' in line:
            return pattern.findall(line)[0]
        elif 'n_documents' in line:
            return 0
        elif 'vocab_size' in line:
            return 0
        elif 'n_words' in line:
            return 0
        elif 'n_topics' in line:
            return 0
        elif 'n_iter' in line:
            return 0


def enthread(target, args):
    """
    Threads a process.
    """
    q = queue.Queue()
    def wrapper():
        q.put(target(*args))
    t = threading.Thread(target=wrapper)
    t.start()
    return q


def is_connected(host='8.8.8.8', port=53, timeout=3):
    """
    Checks if your machine is connected to the internet.
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except:
        return False


def exclude_punctuations(s):
    """
    Excludes punctuations from a string.
    """
    exclude = set('!"#$&\'()*+,-.:;<=>?@^_`{}~')
    s = ''.join(c for c in s if c not in exclude)
    return re.sub(' ', '', s)
    

def unlink_content(directory, pattern='*'):
    """
    Deletes the content of a directory.
    """
    for p in pathlib.Path(directory).rglob(pattern):
        if p.is_file():
            p.unlink()
