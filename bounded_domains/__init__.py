__version__ = "0.1.0"


# setup module logging
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, os.getenv("LOGLEVEL", "WARNING")))
logger_consolehandler = logging.StreamHandler()
logger_consolehandler.setLevel(getattr(logging, os.getenv("LOGLEVEL", "WARNING")))
logger.addHandler(logger_consolehandler)

from .domains import *
from .graph import *
from .utils import *
