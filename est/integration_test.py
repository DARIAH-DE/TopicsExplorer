from subprocess import check_output, STDOUT, CalledProcessError
from nose.plugins.skip import SkipTest
from pathlib import Path
import logging
import re

project_path = Path(__file__).absolute().parent.parent


def jupyter_integration_test():
    """
    Integration test notebook (via Jupyter)
    """
    #Test Introducing_lda.ipynb
    try:
        check_output(["jupyter-nbconvert", "--execute",
                     "--log-level=ERROR",
                     "--ExecutePreprocessor.iopub_timeout=30",
                      "--ExecutePreprocessor.timeout=None",
                    str(Path(project_path, "Introducing_lda.ipynb"))],
                     stderr=STDOUT, universal_newlines=True)
    except FileNotFoundError as e:
        raise SkipTest("jupyter-nbconvert not found. Cannot run integration test. "
                   + str(e))
    except CalledProcessError as e:
        message = e.output
        cellinfo = re.search('nbconvert.preprocessors.execute.CellExecutionError: (.+)$',
                  message, re.MULTILINE | re.DOTALL)
        if cellinfo:
            message = cellinfo.group(1)
        logging.error(message)
    
    #Test Introducing_gensim.ipynb
    try:
        check_output(["jupyter-nbconvert", "--execute",
                     "--log-level=ERROR",
                     "--ExecutePreprocessor.iopub_timeout=30",
                      "--ExecutePreprocessor.timeout=None",
                    str(Path(project_path, "Introducing_gensim.ipynb"))],
                     stderr=STDOUT, universal_newlines=True)
    except FileNotFoundError as e:
        raise SkipTest("jupyter-nbconvert not found. Cannot run integration test. "
                   + str(e))
    except CalledProcessError as e:
        message = e.output
        cellinfo = re.search('nbconvert.preprocessors.execute.CellExecutionError: (.+)$',
                  message, re.MULTILINE | re.DOTALL)
        if cellinfo:
            message = cellinfo.group(1)
        logging.error(message)
        
    #Test Introducing_MALLET.ipynb
    try:
        check_output(["jupyter-nbconvert", "--execute",
                     "--log-level=ERROR",
                     "--ExecutePreprocessor.iopub_timeout=30",
                      "--ExecutePreprocessor.timeout=None",
                    str(Path(project_path, "Introducing_MALLET.ipynb"))],
                     stderr=STDOUT, universal_newlines=True)
    except FileNotFoundError as e:
        raise SkipTest("jupyter-nbconvert not found. Cannot run integration test. "
                   + str(e))
    except CalledProcessError as e:
        message = e.output
        cellinfo = re.search('nbconvert.preprocessors.execute.CellExecutionError: (.+)$',
                  message, re.MULTILINE | re.DOTALL)
        if cellinfo:
            message = cellinfo.group(1)
        logging.error(message)
        raise
