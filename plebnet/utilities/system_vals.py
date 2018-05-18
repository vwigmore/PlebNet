"""

This file contains the variables which are used throughout PlebNet.

"""

# Total imports
import os

# Partial imports

# Local imports

# File parameters


""" MAIN PATHS """
PLEBNET_CONFIG = os.path.expanduser("~/.plebnet.cfg")
PLEBNET_HOME = os.path.expanduser("~/PlebNet")
TRIBLER_HOME = os.path.expanduser("~/PlebNet/tribler")

""" PROCESS IDENTIFICATION FILES """
TRIBLER_PID = "twistd_tribler.pid"
TUNNEL_HELPER_PID = "twistd_th.pid"
IRC_PID = "Documents/ircbot.pid"

""" DATE AND TIME VARIABLES """
TIME_IN_HOUR = 60.0 * 60.0
TIME_IN_DAY = TIME_IN_HOUR * 24.0
MAX_DAYS = 5

""" EXIT CODES """
FAILURE = 0
SUCCESS = 1
UNKNOWN = 2
