from pathlib import Path
import tempfile


TEMPDIR = tempfile.gettempdir()
DATABASE = str(Path(TEMPDIR, "topicsexplorer.db"))
LOGFILE = str(Path(TEMPDIR, "topicsexplorer.log"))