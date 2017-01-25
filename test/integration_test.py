from subprocess import check_call
from nose.plugins.skip import SkipTest
from pathlib import Path

project_path = Path(__file__).absolute().parent.parent


def jupyter_integration_test():
    """
    Tries to run the integration test notebook using jupyter.
    """
    try:
        check_call(["jupyter-nbconvert", "--execute",
                    str(Path(project_path, "IntegrationTest_v01.ipynb"))])
    except FileNotFoundError as e:
        raise SkipTest("jupyter-nbconvert not found. Cannot run integration test. "
                   + str(e))
