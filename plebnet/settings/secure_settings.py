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
PATH_TO_FILE = "plebnet/settings/configuration/secure.cfg"

instance = None


def get_instance():
    global instance
    if not instance:
        instance = Init()
    return instance


class Init(object):

    def __init__(self):
        self.filename = os.path.join(os.path.expanduser("~/PlebNet"), PATH_TO_FILE)
        self.settings = setting.Settings(self.filename)
        self.settings.load()

    """THE GETTERS FOR THE GITHUB SECTION"""

    def github_username(self, value=None): return self.settings.handle("github", "username", value)

    def github_password(self, value=None): return self.settings.handle("github", "password", value)


def store(args):
    get_instance()
    if args.github_username: instance.set_github_username(args.github_username)
    if args.github_password: instance.set_github_password(args.github_password)
    instance.settings.write()
