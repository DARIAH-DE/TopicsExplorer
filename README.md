# Topics - Easy Topic Modeling in Python #

Topics is a gentle introduction to Topic Modeling. It provides a convenient, modular workflow that can be entirely controlled from within and which comes with a well documented [Jupyter notebook](http://jupyter.org/), integrating two of the most popular LDA implementations: [Gensim](https://radimrehurek.com/gensim/) and [Mallet](http://mallet.cs.umass.edu/). Users not yet familiar with working with Python scripts can test basic topic modeling in a [Flask](http://flask.pocoo.org/)-based [GUI demonstrator](/demonstrator/README.md).

### Getting Started

#### Windows

1.  Download and install the latest version of [WinPython](https://winpython.github.io/). 
2.  Download and install [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).
3.  Open the **Winpython PowerShell Promt.exe** in your **WinPython** folder and type 'git clone https://github.com/DARIAH-DE/Topics.git' to clone **Topics** into your WinPython folder.
4.  type 'cd .\Topics' in **Winpython PowerShell** to navigate to the **Topics** folder. 
5a. either: type 'pip install .' in **Winpython PowerShell** to install packages required by **Topics** 
5b. or: type 'pip install -r requirements.txt' in **Winpython PowerShell** to install **Topics** with additional development packages.
6.  type 'jupyter notebook' in **Winpython PowerShell** to open [Jupyter], select [Introduction.ipynb](Introduction.ipynb) and follow the instructions.
7.  Note: For the development packages the Python module **future** is needed. Depending in your WinPython andyour Windows version you might have to install **future** manually.
8.  Therefore download the latest [future-x.xx.x-py3-none-any.whl]-wheel (http://www.lfd.uci.edu/~gohlke/pythonlibs/)
9.  Open the **Winpython Control Panel.exe** in your **WinPython** folder
10. Install the **future**-wheel via the **Winpython Control Panel.exe**

#### Working with Mallet


http://mallet.cs.umass.edu/

download and unzip mallet

set environment variable

Mallet_Home -> Path - no whitespace

Open the Winpython powershell

PS W:\mallet\bin> .\mallet

http://programminghistorian.org/lessons/topic-modeling-and-malletv


#### Unix/Linux

1. Download and install [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git), 
2. Open the [command-line interface](https://en.wikipedia.org/wiki/Command-line_interface), type `git clone https://github.com/DARIAH-DE/Topics.git` and press Enter
3. Note: The distribution packages 'libfreetype6-dev' and 'libpng-dev' and a compiler for c++, e.g [gcc](https://gcc.gnu.org/) have to be installed 
4. Open the [command-line interface](https://en.wikipedia.org/wiki/Command-line_interface), navigate to the folder **Topics**  and type `pip install . --user` to install the required packages 
5. Install [Jupyter](http://jupyter.readthedocs.io/en/latest/install.html) and run it by typing `jupyter notebook` in the command-line
5. Access the folder **Topics** through Jupyter in your browser, open the [Introduction.ipynb](Introduction.ipynb) and follow the instructions




