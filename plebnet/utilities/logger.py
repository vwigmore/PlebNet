"""
This file is used for logging purposes. The messages send here will be
printed to the log file and when run from a command UI, will be printed
in a color.
"""

# Total imports
import logging
import os

# Partial imports

# Local imports
from plebnet.utilities.globals import LOGGER_PATH


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def log(msg, method="", name="logger", path=LOGGER_PATH):
    logger = _get_logger(name, path)
    # prepare the output
    tex = _fill(method, 15) + " : " + msg
    # output the log details
    logger.error(tex)
    print(tex)


def success(msg, method="", name="logger", path=LOGGER_PATH):
    logger = _get_logger(name, path)
    tex = _fill(method, 15) + " : " + msg
    # output the log details
    logger.error(tex)
    print(bcolors.OKGREEN + tex + bcolors.ENDC)


def warning(msg, method="", name="logger", path=LOGGER_PATH):
    logger = _get_logger(name, path)
    # prepare the output
    tex = _fill(method, 15) + " : " + msg
    # output the log details
    logger.error(tex)
    print(bcolors.WARNING + tex + bcolors.ENDC)


def error(msg, method="", name="logger", path=LOGGER_PATH):
    logger = _get_logger(name, path)
    # prepare the output
    tex = _fill(method, 15) + " : " + msg
    # output the log details
    logger.error(tex)
    print(bcolors.FAIL + tex + bcolors.ENDC)


def _get_logger(name, path):
    # create a logger

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # create formatter and handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler = logging.FileHandler(path)

        # combine
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def _fill(tex, l):
    if len(tex) > l:
        tex = tex[:l-2] + ".."
    else:
        while len(tex) < l:
            tex = tex + " "
    return tex
