# Topics – Easy Topic Modeling in Python

Topics is a gentle introduction to Topic Modeling. It provides a convenient, modular workflow that can be entirely controlled from within and which comes with a well documented [Jupyter notebook](http://jupyter.org/), integrating three of the most popular LDA implementations: [Gensim](https://radimrehurek.com/gensim/), [MALLET](http://mallet.cs.umass.edu/), and [lda](http://pythonhosted.org/lda/index.html). Users not yet familiar with working with Python scripts can test basic topic modeling in a [Flask](http://flask.pocoo.org/)-based [GUI demonstrator](/demonstrator/README.md).

### Getting Started

#### Windows

1.  Download and install the latest version of [WinPython](https://winpython.github.io/). 
2.  Download and install [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).
3.  Open the **WinPython PowerShell Prompt.exe** in your **WinPython** folder and type `git clone https://github.com/DARIAH-DE/Topics.git` to clone **Topics** into your WinPython folder.
4.  Type `cd .\Topics` in **WinPython PowerShell** to navigate to the **Topics** folder. 
5a. Either: Type `pip install .` in **Winpython PowerShell** to install packages required by **Topics** 
5b. Or: Type `pip install -r requirements.txt` in **Winpython PowerShell** to install **Topics** with additional development packages.
6.  Type `jupyter notebook` in **WinPython PowerShell** to open Jupyter, select one of the files with suffix `.ipynb` and follow the instructions.
7.  **Note**: For the development packages the Python module **future** is needed. Depending in your WinPython and your Windows version you might have to install **future** manually.
8.  Therefore, download the latest [future-x.xx.x-py3-none-any.whl](http://www.lfd.uci.edu/~gohlke/pythonlibs/)-wheel.
9.  Open the **WinPython Control Panel.exe** in your **WinPython** folder
10. Install the **future**-wheel via the **WinPython Control Panel.exe**


#### macOS and Linux

1. Download and install [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git), 
2. Open the [command-line interface](https://en.wikipedia.org/wiki/Command-line_interface), type `git clone https://github.com/DARIAH-DE/Topics.git` to clone **Topics** into your working directory.
3. **Note**: The distribution packages `libfreetype6-dev` and `libpng-dev` and a compiler for C++, e.g. [gcc](https://gcc.gnu.org/) have to be installed.
4. Open the [command-line interface](https://en.wikipedia.org/wiki/Command-line_interface), navigate to the folder **Topics**  and type `pip install . --user` to install the required packages 
5. Install [Jupyter](http://jupyter.readthedocs.io/en/latest/install.html) and run it by typing `jupyter notebook` in the command-line
5. Access the folder **Topics** through Jupyter in your browser, select one of the files with suffix `.ipynb` and follow the instructions.


#### Working with MALLET

1. Download and unzip [MALLET](http://mallet.cs.umass.edu).
2. Set the environment variable for MALLET.


For more detailed instructions, have a look at [this](http://programminghistorian.org/lessons/topic-modeling-and-mallet).