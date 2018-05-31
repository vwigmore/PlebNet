"""
This subclass of settings is used to store the agent configuration.

This configuration should contain values which are set on initialization
of the first parent, and can change during the cloning process or during
the lifespan of the specific agent.

The file it self can be found in the PATH_TO_FILE location.
"""

# Total imports
import os
# Partial imports
from appdirs import user_config_dir, user_data_dir
from shutil import copy2 as copy
# Local imports
from plebnet.settings import setting

# File parameters
file_name = 'agent_setup.cfg'

conf_path = user_config_dir()
data_path = user_data_dir()
init_path = os.path.join(os.path.expanduser("~/PlebNet"), 'plebnet/settings/configuration')

init_file = os.path.join(init_path, file_name)
conf_file = os.path.join(conf_path, file_name)


# TODO: extend settings: prevent double code with plebnet_settings
def get_instance():
    global instance
    if not instance:
        instance = AgentSettings()
    return instance


def store(args):
    get_instance()
    for arg in vars(args):
        if (arg in dir(instance)) and getattr(args, arg):
            getattr(instance, arg)(str(getattr(args, arg)))
    instance.settings.write()


class AgentSettings(object):

    def __init__(self):
        # file does not exist --> copy the initial file
        if not os.path.isfile(conf_file):
            copy(init_file, conf_path)

        self.settings = setting.Settings(conf_file)

    """ THE ATTRIBUTE METHODS FOR THE SELF SECTION """

    def self_id(self, value=None): return self.settings.handle("self", "id", value)


# {'child_index': 0,
#                        'expiration_date': 0,
#                        'last_offer_date': 0,
#                        'last_offer': {'MC': 0,
#                                       'BTC:': 0.0},
#                        'excluded_providers': [],
#                        'chosen_provider': None,
#                        'bought': [],
#                        'installed': [],
#                        'transactions': []}