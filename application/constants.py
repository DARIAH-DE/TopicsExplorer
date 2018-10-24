import tempfile
import pathlib

TEMPDIR = tempfile.gettempdir()
DATABASE_URI = str(pathlib.Path(TEMPDIR, "topicsexplorer.db"))
LOGFILE = str(pathlib.Path(TEMPDIR, "topicsexplorer.log"))