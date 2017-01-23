from subprocess import check_call
from nose.plugins.skip import SkipTest


def jupyter_integration_test():
    """
    Tries to run the integration test notebook using jupyter.
    """
    try:
        check_call(["jupyter-nbconvert", "--execute",
                    "IntegrationTest_v01.ipynb"])
    except FileNotFoundError as e:
        raise SkipTest("jupyter-nbconvert not found. Cannot run integration test. "
                   + str(e))
