"""
This subclass of settings is used to store the setup configuration.

This configuration should only contain values which are set on initialization
of the first parent, and should not change during the cloning process.

The file it self can be found in the PATH_TO_FILE location.
"""

# Total imports
import os

# Partial imports

# Local imports
from plebnet.settings import setting

# File parameters
PATH_TO_FILE = "plebnet/settings/configuration/setup.cfg"


class Init(object):

    def __init__(self):
        self.filename = os.path.join(os.path.expanduser("~/PlebNet"), PATH_TO_FILE)
        self.settings = setting.Settings(self.filename)
        self.settings.load()

    """THE GETTERS FOR THE IRC SECTION"""

    def get_irc_channel(self): return self.settings.get("irc", "channel")

    def get_irc_server(self): return self.settings.get("irc", "server")

    def get_irc_port(self): return int(self.settings.get("irc", "port"))

    def get_irc_nick(self): return self.settings.get("irc", "nick")

    def get_irc_timeout(self): return int(self.settings.get("irc", "timeout"))

    """THE GETTERS FOR THE VPS SECTION"""

    def get_vps_host(self): return self.settings.get("vps", "host")

    def get_vps_life(self): return self.settings.get("vps", "initdate")

    def get_vps_dead(self): return self.settings.get("vps", "finaldate")
