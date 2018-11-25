import logging
from application import views
try:
    from application import gui
except ImportError:
    logging.warning("The `gui` module is not available.")