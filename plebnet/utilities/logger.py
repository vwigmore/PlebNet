"""
This file is used for logging purposes. The messages send here will be
printed to the log file and when run from a command UI, will be printed
in a color.
"""

# Total imports
import logging

from logging.handlers import WatchedFileHandler
# Local imports
from plebnet.settings import plebnet_settings

suppress_print = False
settings = plebnet_settings.get_instance()


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def reset():
    if logging.root:
        del logging.root.handlers[:]
        del logging.getLogger().handlers[:]
        del logging.getLogger(settings.logger_filename()).handlers[:]


def _get_logger(name=settings.logger_filename()):
    print("loggername =%s " % name)
    logger = logging.getLogger(name)

    if not logger.handlers:

        logger.setLevel(logging.INFO)

        # create formatter and handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        path = settings.logger_file()
        print("loggerpath =%s " % path)
        # handler = logging.FileHandler(path)
        handler = WatchedFileHandler(path)
        # combine
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def put_msg(msg, color=None, origin="", method=_get_logger().info):
    msg = _fill(origin, 15) + " : " + msg
    if settings.active_logger():
        method(msg)
    if settings.active_verbose():
        if color:
            msg = color + msg + bcolors.ENDC
        print(msg)


def log(msg, origin=""):
    put_msg(msg, origin=origin)
    # # prepare the output
    # tex = _fill(method, 15) + " : " + msg
    # # output the log details
    # _get_logger().info(tex)
    # if not suppress_print: print(tex)


def success(msg, origin=""):
    put_msg(msg, bcolors.OKGREEN, origin=origin)
    # # prepare the output
    # tex = _fill(method, 15) + " : " + msg
    # # output the log details
    # _get_logger().info(tex)
    # if not suppress_print: print(bcolors.OKGREEN + tex + bcolors.ENDC)


def warning(msg, origin=""):
    put_msg(msg, bcolors.WARNING, origin=origin, method=_get_logger().warning)
    # # prepare the output
    # tex = _fill(method, 15) + " : " + msg
    # # output the log details
    # _get_logger().warning(tex)
    # if not suppress_print: print(bcolors.WARNING + tex + bcolors.ENDC)


def error(msg, origin=""):
    put_msg(msg, bcolors.FAIL, origin=origin, method=_get_logger().error)
    # # prepare the output
    # tex = _fill(method, 15) + " : " + msg
    # # output the log details
    # _get_logger().error(tex)
    # if not suppress_print: print(bcolors.FAIL + tex + bcolors.ENDC)


def _fill(tex, leng):
    if len(tex) > leng:
        tex = tex[:leng-2] + ".."
    else:
        while len(tex) < leng:
            tex = tex + " "
    return tex
