from subprocess import check_output, STDOUT, CalledProcessError
from nose.plugins.skip import SkipTest
from pathlib import Path
import logging

project_path = Path(__file__).absolute().parent.parent


def jupyter_integration_test():
    """
    Tries to run the integration test notebook using jupyter.
    """
    try:
        check_output(["jupyter-nbconvert", "--execute",
                    str(Path(project_path, "IntegrationTest_v01.ipynb"))],
                     stderr=STDOUT, universal_newlines=True)
    except FileNotFoundError as e:
        raise SkipTest("jupyter-nbconvert not found. Cannot run integration test. "
                   + str(e))
    except CalledProcessError as e:
        logging.error(e.output)
        raise
