DARIAH Topics Explorer
======================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

This application introduces an user-friendly Topic Modeling workflow, basically containing text data preprocessing, the actual modeling using `latent Dirichlet allocation <http://www.jmlr.org/papers/volume3/blei03a/blei03a.pdf>`_, as well as various interactive visualizations.

.. note:: If you do not know anything about Topic Modeling or programming in general, this is where you start.

Getting started
~~~~~~~~~~~~~~~
Windows and macOS users **do not** have to install additional software.

1. Go to the `release-section <https://github.com/DARIAH-DE/TopicsExplorer/releases>`_ and download the ZIP archive for your OS.
2. Open it by double-clicking.
3. Unzip the archive, e.g. using `7-zip <http://www.7-zip.org>`_.
4. Run the app by double-clicking the file **DARIAH Topics Explorer**.

.. note:: If you are on a Mac and get an error message saying that the file is from an “unidentified developer”, you can override it by holding control while double-clicking. The error message will still appear, but you will be given an option to run the file anyway.


Troubleshooting
~~~~~~~~~~~~~~~
* Please be patient. Depending on corpus size and number of iterations, the process may take some time, meaning something between some seconds and some hours.
* If you are confronted with any problems regarding the application, use `GitHub issues <https://github.com/DARIAH-DE/TopicsExplorer/issues>`_, but suggestions for improvements, wishes, or hints on typos are of course also welcome.


About this application
~~~~~~~~~~~~~~~~~~~~~
.. image:: _static/screenshot.png

**Topics Explorer** aims for simplicity and usability. If you are working with a large corpus (let's say more than 200 documents, 5000 tokens each document) you may wish to use more sophisticated topic models such as those implemented in `MALLET <http://mallet.cs.umass.edu/topics.php>`_, which is known to be more robust than standard LDA. Have a look at our Jupyter notebook `introducing Topic Modeling with MALLET <https://github.com/DARIAH-DE/Topics/blob/master/IntroducingMallet.ipynb>`_.

About DARIAH-DE
~~~~~~~~~~~~~~~
`DARIAH-DE <https://de.dariah.eu/>`_ supports research in the humanities and cultural sciences with digital methods and procedures. The research infrastructure of DARIAH-DE consists of four pillars: teaching, research, research data and technical components. As a partner in `DARIAH-EU <http://dariah.eu/>`_, DARIAH-DE helps to bundle and network state-of-the-art activities of the digital humanities. Scientists use DARIAH, for example, to make research data available across Europe. The exchange of knowledge and expertise is thus promoted across disciplines and the possibility of discovering new scientific discourses is encouraged.

This application has been developed with support from the DARIAH-DE initiative, the German branch of DARIAH-EU, the European Digital Research Infrastructure for the Arts and Humanities consortium. Funding has been provided by the German Federal Ministry for Research and Education (BMBF) under the identifier 01UG1610J.

.. image:: _static/dariah-de_logo.png

.. image:: _static/bmbf_logo.png
