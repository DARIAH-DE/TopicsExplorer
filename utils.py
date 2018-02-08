#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import lzma
import pickle
import time
import re
from lxml import etree
from bokeh.plotting import figure
from bokeh.models import CustomJS, ColumnDataSource, HoverTool
from bokeh.models.widgets import Dropdown
from bokeh.layouts import column
import lda

__author__ = "Severin Simmler"
__email__ = "severin.simmler@stud-mail.uni-wuerzburg.de"


TOOLS = 'hover, pan, reset, save, wheel_zoom, zoom_in, zoom_out'
JAVASCRIPT = """
             var f = cb_obj.value;
             var options = %s;

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
             console.log(' ')
             """


def compress(data, filepath):
    with open(filepath, 'wb') as file:
        file.write(lzma.compress(pickle.dumps(data, pickle.HIGHEST_PROTOCOL)))


def decompress(filepath):
    with open(filepath, 'rb') as file:
        data = lzma.decompress(file.read())
        return pickle.loads(data)


def process_xml(file):
    ns = dict(tei='http://www.tei-c.org/ns/1.0')
    text = etree.parse(file)
    try:
        text = text.xpath('//tei:text', namespaces=ns)[0]
    except IndexError:
        pass
    return ''.join(text.xpath('.//text()'))


def boxplot(stats):
    x_labels = ['Document size (clean)', 'Document size (raw)']

    groups = stats.groupby('group')
    q1 = groups.quantile(q=0.25)
    q2 = groups.quantile(q=0.5)
    q3 = groups.quantile(q=0.75)
    iqr = q3 - q1
    upper = q3 + 1.5*iqr
    lower = q1 - 1.5*iqr

    def outliers(group):
        cat = group.name
        return group[(group.score > upper.loc[cat]['score']) |
                     (group.score < lower.loc[cat]['score'])]['score']
    out = groups.apply(outliers).dropna()

    fig = figure(tools='save', background_fill_color='#EFE8E2', title='', x_range=x_labels,
                 logo=None, sizing_mode='fixed', plot_width=500, plot_height=350)

    qmin = groups.quantile(q=0.00)
    qmax = groups.quantile(q=1.00)
    upper.score = [min([x,y]) for (x,y) in zip(list(qmax.loc[:,'score']),upper.score)]
    lower.score = [max([x,y]) for (x,y) in zip(list(qmin.loc[:,'score']),lower.score)]

    fig.segment(x_labels, upper.score, x_labels, q3.score, line_color='black')
    fig.segment(x_labels, lower.score, x_labels, q1.score, line_color='black')

    fig.vbar(x_labels, 0.7, q2.score, q3.score, fill_color='#E08E79', line_color='black')
    fig.vbar(x_labels, 0.7, q1.score, q2.score, fill_color='#3B8686', line_color='black')

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
    y_range = document_topics.columns.tolist()
    fig = figure(y_range=y_range, plot_height=height, tools=tools,
                 toolbar_location='right', sizing_mode='scale_width',
                 logo=None)

    plots = {}
    options = document_topics.index.tolist()
    for i, option in enumerate(options):
        x_axis = document_topics.iloc[i]
        source = ColumnDataSource(dict(Describer=y_range, Proportion=x_axis))
        option = re.sub(' ', '_', option)
        bar = fig.hbar(y='Describer', right='Proportion', source=source,
                       height=0.5, color='#053967')
        bar.visible = False
        plots[option] = bar

    fig.xgrid.grid_line_color = None
    fig.x_range.start = 0
    fig.select_one(HoverTool).tooltips = [('Proportion', '@Proportion')]
    fig.xaxis.axis_label = 'Proportion'
    fig.xaxis.major_label_text_font_size = '9pt'
    fig.yaxis.major_label_text_font_size = '9pt'

    callback = CustomJS(args=plots, code=script % list(plots.keys()))

    menu = [(select, re.sub(' ', '_', option)) for select, option in zip(document_topics.index, options)]
    if topics is not None:
        selection = [' '.join(topics.iloc[i].tolist()) + ' ...' for i in range(topics.shape[0])]
        menu = [(select, re.sub(' ', '_', option)) for select, option in zip(selection, options)]
        dropdown = Dropdown(label='Select topic to display proportion', menu=menu, callback=callback)
    else:
        menu = [(select, option) for select, option in zip(document_topics.index, options)]
        dropdown = Dropdown(label='Select document to display proportion', menu=menu, callback=callback)
    return column(dropdown, fig, sizing_mode='scale_width')


def read_logfile(logfile):
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


def lda_modeling(document_term_arr, n_topics, n_iter):
    model = lda.LDA(n_topics=n_topics, n_iter=n_iter)
    return model.fit(document_term_arr)
