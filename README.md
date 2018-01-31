# Topics Explorer: A GUI for Topics – Easy Topic Modeling
This application introduces an user-friendly Topic Modeling workflow, basically containing text data preprocessing, the actual modeling using [latent Dirichlet allocation](http://www.jmlr.org/papers/volume3/blei03a/blei03a.pdf), as well as various interactive visualizations.

**If you do not know anything about Topic Modeling or programming in general, this is where you start.**

Topics Explorer aims for *simplicity* and *usability*. If you are working with a large corpus (let's say more than 200 documents, 5000 tokens each document) you may wish to use more sophisticated Topic Models such as those implemented in [MALLET](http://mallet.cs.umass.edu/topics.php), which is known to be more robust than standard LDA. Have a look at our Jupyter notebook [introducing Topic Modeling with MALLET](https://github.com/DARIAH-DE/Topics/IntroducingMallet.ipynb).

![Demonstrator Screenshot](screenshot.png)


## Standalone executables
Although this application is built with Python and some JavaScript, it is possible to run it as if it was a native application, without having to install Python or any related packages. There is currently one build for Windows and macOS, respectively.

1. Download `demonstrator-0.0.1-windows.zip` or `demonstrator-0.0.1-mac.zip` from the [release-section](https://github.com/DARIAH-DE/Topics/releases).
2. Open it by double-clicking.
3. Run the app by double-clicking the file `DARIAH Topics Explorer.exe` or `DARIAH Topics Explorer.app`, respectively.


### Troubleshooting
* Please be patient. Depending on corpus size and number of iterations, the process may take some time, meaning something between some seconds and some hours.
* If you are on a Mac and get an error message saying that the file is from an “unidentified developer”, you can override it by holding control while double-clicking. The error message will still appear, but you will be given an option to run the file anyway.
* Please use [GitHub Issues](https://github.com/DARIAH-DE/TopicsExplorer/issues).


## Working with the development version
**Topics Explorer** basically consists of three layers with an user-interface built on top:

<p align="center">
  <img src="layer.png" width=600px/>
</p>


### Requirements
Besides the standalone executables, you have the ability to run the development version. In this case, you will have to install some dependencies, but first of all:

* At least Python 3.6, from [here](https://www.python.org/downloads/). Python 2 is *not* supported.
* If you wish to use *Layer 3* (which is not necessary at all): Node.js, from [here](https://nodejs.org/en/download/).

For Python, you will need the following libraries:
* `[dariah_topics](https://github.com/DARIAH-DE/Topics)` 0.0.5 or higher.
* `[lda](https://github.com/lda-project/lda)` 1.0.5 or higher.
* `[bokeh](https://github.com/bokeh/bokeh)` 0.12.13 or higher.
* `[flask](https://github.com/pallets/flask)` 0.12.2 or higher.
* `[lxml](https://github.com/lxml/lxml)` 4.1.1 or higher.
* `[pandas](https://github.com/pandas-dev/pandas)` 0.21.1 or higher.
* `[numpy](https://github.com/numpy/numpy)` 1.14.0 or higher.

You can install all dependencies using Python's package manager [`pip`](https://pip.pypa.io/en/stable/):

```
pip install -r requirements.txt
```

> If you are on a UNIX-based machine, remember using `pip3` and `python3` instead of `pip` and `python`.

So far, you could run the application via `python webapp.py` and go to `http://127.0.0.1:5000` in any web browser. If you want a more desktop app-like feeling, you can build *Layer 3* on top with [Electron](https://electronjs.org/), a JavaScript framework for creating native applications with web technologies like JavaScript, HTML, and CSS. The dependencies are:

* `[electron](https://github.com/electron/electron)` 1.7.10 or higher.
* `[request-promise](https://github.com/request/request-promise)` 4.2.2 or higher.
* `[request](https://github.com/request/request)` 2.83.1 or higher.

Run the following command via [`npm`](https://www.npmjs.com/get-npm):

```
npm install
```


### Troubleshooting
* When installing `electron` fails, try `sudo npm install -g electron --unsafe-perm=true --allow-root`.
* Please use [GitHub Issues](https://github.com/DARIAH-DE/TopicsExplorer/issues).


## Creating a build for layer 1 and 2
To freeze the Python part with `pyinstaller`, run on macOS:

```
pyinstaller --onefile --add-data static:static --add-data templates:templates --add-data bokeh_templates:bokeh_templates --additional-hooks-dir hooks webapp.py
```

or, for Windows:
```
pyinstaller --onefile --windowed --add-data static;static --add-data templates;templates --add-data bokeh_templates;bokeh_templates --additional-hooks-dir hooks webapp.py
```
## Creating a build for the whole application
To freeze the Electron part with `electron-builder`, run:

```
electron-builder
```
