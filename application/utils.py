import pathlib
import logging


def setup_logging(level=logging.INFO):
    logfile = "topicsexplorer.log"
    logging.basicConfig(level=level,
                        format="(%(asctime)s) %(message)s",
                        datefmt="%H:%M:%S",
                        filename=logfile,
                        filemode="w")
    return logfile

def get_status(logfile):
    with pathlib.Path(logfile).open("r", encoding="utf-8") as logfile:
        messages = logfile.readlines()
        latest_message = messages[-1].strip()
        return latest_message