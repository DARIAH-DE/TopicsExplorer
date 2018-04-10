# DARIAH Topics Explorer
This application introduces an **user-friendly topic modeling workflow**, basically containing text data preprocessing, the actual modeling using [latent Dirichlet allocation](http://www.jmlr.org/papers/volume3/blei03a/blei03a.pdf), as well as various interactive visualizations.

> If you do not know anything about Topic Modeling or programming in general, this is where you start.

## Getting started
Windows and macOS users **do not** have to install additional software, except the application itself:

1. Go to the [release-section](https://github.com/DARIAH-DE/TopicsExplorer/releases) and download the ZIP archive for your OS.
2. Unzip the archive, e.g. using [7-zip](http://www.7-zip.org/).
3. Run the app by double-clicking the file `DARIAH Topics Explorer`.

> If you are on a Mac and get an error message saying that the file is from an “unidentified developer”, you can override it by holding control while double-clicking. The error message will still appear, but you will be given an option to run the file anyway.

Linux user have to use the development version, but Windows and macOS users can of course also do this:

1. Go to the [release-section](https://github.com/DARIAH-DE/TopicsExplorer/releases) and download the **source code** as ZIP archive.
2. Unzip the archive, e.g. using `unzip` via the command-line.
3. Make sure you have Python 3.6 and [Pipenv](https://docs.pipenv.org/) installed.
4. Run `pipenv install`, and afterwards `pipenv shell`.
5. To start the application, type `python topicsexplorer.py`, and press enter.

## The application
![Demonstrator Screenshot](docs/images/screenshot.png)

Topics Explorer aims for **simplicity and usability**. If you are working with a large corpus (let's say more than 200 documents, 5000 tokens each document) you may wish to use more sophisticated topic models such as those implemented in [MALLET](http://mallet.cs.umass.edu/topics.php), which is known to be more robust than standard LDA. Have a look at our Jupyter notebook introducing [topic modeling with MALLET](https://github.com/DARIAH-DE/Topics/blob/master/IntroducingMallet.ipynb).

## Example visualization
The following visualization is based on the distribution of 10 topics over a total of 10 novels (written by Charles Dickens, George Eliot, Joseph Fielding, William Thackeray, and Anthony Trollope). But first of all, the algorithm produces so-called topics:

<center>
                  <table border="0" class="dataframe">
                    <thead>
                      <tr style="text-align: right;">
                        <th></th>
                        <th>Key 1</th>
                        <th>Key 2</th>
                        <th>Key 3</th>
                        <th>Key 4</th>
                        <th>Key 5</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <th>Topic 1</th>
                        <td>captain</td>
                        <td>lord</td>
                        <td>whom</td>
                        <td>over</td>
                        <td>young</td>
                      </tr>
                      <tr>
                        <th>Topic 2</th>
                        <td>phineas</td>
                        <td>laura</td>
                        <td>lord</td>
                        <td>finn</td>
                        <td>kennedy</td>
                      </tr>
                      <tr>
                        <th>Topic 3</th>
                        <td>jarndyce</td>
                        <td>quite</td>
                        <td>sir</td>
                        <td>richard</td>
                        <td>ada</td>
                      </tr>
                      <tr>
                        <th>Topic 4</th>
                        <td>jones</td>
                        <td>indeed</td>
                        <td>adams</td>
                        <td>answered</td>
                        <td>may</td>
                      </tr>
                      <tr>
                        <th>Topic 5</th>
                        <td>our</td>
                        <td>these</td>
                        <td>can</td>
                        <td>honour</td>
                        <td>without</td>
                      </tr>
                      <tr>
                        <th>Topic 6</th>
                        <td>lopez</td>
                        <td>duke</td>
                        <td>wharton</td>
                        <td>course</td>
                        <td>duchess</td>
                      </tr>
                      <tr>
                        <th>Topic 7</th>
                        <td>crawley</td>
                        <td>george</td>
                        <td>osborne</td>
                        <td>rebecca</td>
                        <td>amelia</td>
                      </tr>
                      <tr>
                        <th>Topic 8</th>
                        <td>peggotty</td>
                        <td>aunt</td>
                        <td>mother</td>
                        <td>steerforth</td>
                        <td>murdstone</td>
                      </tr>
                      <tr>
                        <th>Topic 9</th>
                        <td>thought</td>
                        <td>way</td>
                        <td>too</td>
                        <td>down</td>
                        <td>went</td>
                      </tr>
                      <tr>
                        <th>Topic 10</th>
                        <td>tom</td>
                        <td>adam</td>
                        <td>maggie</td>
                        <td>work</td>
                        <td>tulliver</td>
                      </tr>
                    </tbody>
                  </table>
                </center>

These topics describe the semantic structures of a text corpus. Every document of the corpus consists, to a certain degree, of every topic. This distribution is visualized in a heatmap; the darker the blue, the higher the proportion.

![Heatmap](docs/images/heatmap.png)

> **DARIAH Topics Explorer** allows you to analyze and explore your own text corpora using topic models – without prior knowledge or special prerequisites.

## Troubleshooting
* Please be patient. Depending on corpus size and number of iterations, the process may take some time, meaning something between some seconds and some hours.
* If you are confronted with any problems regarding the application, use [GitHub issues](https://github.com/DARIAH-DE/TopicsExplorer/issues) – but suggestions for improvements, wishes, or hints on typos are of course also welcome.

## Developing
If you want to run the development version, you can either `git clone` this repository, or download the [ZIP archive](https://github.com/DARIAH-DE/TopicsExplorer/archive/master.zip).

### Requirements
You can install all dependencies using [Pipenv]](https://docs.pipenv.org/):

```
pipenv install
```

After spawning a shell within the virtualenv (`pipenv shell`), you could run the application via `python webapp.py` and go to `http://127.0.0.1:5000` in any web browser. If you want a more desktop app-like feeling, you can wrap a Qt-based web engine around:

```
python topicsexplorer.py
```

### Creating a standalone build
To freeze the Python scripts and create a standalone executable with [PyInstaller](http://www.pyinstaller.org/), simply run:

```
git checkout pyinstaller
git merge origin/master
git push origin pyinstaller
pyinstaller topicsexplorer.spec
```

## About DARIAH-DE
[DARIAH-DE](https://de.dariah.eu) supports research in the humanities and cultural sciences with digital methods and procedures. The research infrastructure of DARIAH-DE consists of four pillars: teaching, research, research data and technical components. As a partner in [DARIAH-EU](http://dariah.eu/), DARIAH-DE helps to bundle and network state-of-the-art activities of the digital humanities. Scientists use DARIAH, for example, to make research data available across Europe. The exchange of knowledge and expertise is thus promoted across disciplines and the possibility of discovering new scientific discourses is encouraged.

This application has been developed with support from the DARIAH-DE initiative, the German branch of DARIAH-EU, the European Digital Research Infrastructure for the Arts and Humanities consortium. Funding has been provided by the German Federal Ministry for Research and Education (BMBF) under the identifier 01UG1610J.

![DARIAH-DE](https://raw.githubusercontent.com/DARIAH-DE/Topics/testing/docs/images/dariah-de_logo.png)
![BMBF](https://raw.githubusercontent.com/DARIAH-DE/Topics/testing/docs/images/bmbf_logo.png)
