#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name='dariah_topics',
    version='0.2.0dev0',
    description='DARIAH Topic Modelling',
    # url
    author="DARIAH-DE Wuerzburg Group",
    author_email="pielstroem@biozentrum.uni-wuerzburg.de",
    # license
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ],
    # keywords
    packages=find_packages(exclude=['corpus_*', 'docs', 'tests']),
    install_requires=[
        'pandas>=0.19.2',
        'regex>=2017.01.14',
        'gensim>=0.13.2',
        'matplotlib>=1.5.3',
        'numpy>=1.3',
        'scipy>=0.7',
    ],
    # pip install -e .[demonstrator,vis,evaluation]
    extras_require={
        'demonstrator': [
            'flask>=0.11.1'
        ],
        'vis': [
            #'wordcloud>=1.3.1',
            #'pyLDAvis>=2.0.0',    # to feature 'pyldavis'
        ],
        'evaluation': [
            'wikipedia>=1.4.0',
            'lxml>=3.6.4'
        ]
    }
)
