import os

# main paths
PLEBNET_CONFIG = os.path.expanduser("~/.plebnet.cfg")
PLEBNET_HOME = os.path.expanduser("~/PlebNet")
TRIBLER_HOME = os.path.expanduser("~/PlebNet/tribler")

# pids
# TRIBLER_PID = "/var/run/twistd_tribler.pid"
# IRC_PID = "/var/run/ircbot.pid"
TRIBLER_PID = "twistd_tribler.pid"
TUNNEL_HELPER_PID = "twistd_th.pid"
IRC_PID = "Documents/ircbot.pid"

# date-time settings
TIME_IN_HOUR = 60.0 * 60.0
TIME_IN_DAY = TIME_IN_HOUR * 24.0
MAX_DAYS = 5

# success
FAILURE = 0
SUCCESS = 1
UNKNOWN = 2
