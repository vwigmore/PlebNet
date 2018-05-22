"""
This subclass of settings is used to store the plebnet configuration.

This configuration should contain values which are set on initialization
of the first parent, and can change during the cloning process or during
the lifespan of the specific agent.

The file it self can be found in the PATH_TO_FILE location.
"""

# Total imports
import os

# Partial imports

# Local imports
from plebnet.settings import setting

# File parameters
PATH_TO_FILE = "plebnet/settings/configuration/plebnet.cfg"


class Init(object):

    def __init__(self):
        self.filename = os.path.join(os.path.expanduser("~/PlebNet"), PATH_TO_FILE)
        self.settings = setting.Settings(self.filename)
        self.settings.load()

    def get_logger_path(self):
        path = os.path.expanduser(self.settings.get("paths", "LOGGER_PATH"))
        file = os.path.expanduser(self.settings.get("files", "LOGGER_FILE"))
        return os.path.join(path, file)

    def get_logger_file(self):
        return self.settings.get("files", "LOGGER_FILE")
