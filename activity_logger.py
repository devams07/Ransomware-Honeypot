# activity_logger.py
import logging
from logging.handlers import RotatingFileHandler
import pathlib
import sys

LOG_PATH = pathlib.Path("activity.log")

def get_logger(name: str = "honeypot", level=logging.INFO):
    """
    Creates (or returns) a logger that writes to activity.log (rotating)
    and to stdout. Use get_logger(__name__) in your scripts.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # already configured

    logger.setLevel(level)

    # File handler (rotates to keep file manageable)
    fh = RotatingFileHandler(LOG_PATH, maxBytes=2_000_000, backupCount=3, encoding="utf-8")
    fh.setLevel(level)
    fh_formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s",
                                     datefmt="%Y-%m-%d %H:%M:%S")
    fh.setFormatter(fh_formatter)
    logger.addHandler(fh)

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch_formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s", datefmt="%H:%M:%S")
    ch.setFormatter(ch_formatter)
    logger.addHandler(ch)

    # Don't propagate to root to avoid duplicate logs
    logger.propagate = False
    return logger
