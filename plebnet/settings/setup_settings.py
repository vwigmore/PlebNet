import os

from plebnet.settings import setting


PATH_TO_FILE = "plebnet/settings/configuration/setup.cfg"


class Init(object):

    def __init__(self):
        self.filename = os.path.join(os.path.expanduser("~/PlebNet"), PATH_TO_FILE)
        self.settings = setting.Settings(self.filename)
        self.settings.load()

    # the getters for the irc section

    def get_irc_channel(self): return self.settings.get("irc", "channel")

    def get_irc_server(self): return self.settings.get("irc", "server")

    def get_irc_port(self): return int(self.settings.get("irc", "port"))

    def get_irc_nick(self): return self.settings.get("irc", "nick")

    def get_irc_timeout(self): return int(self.settings.get("irc", "timeout"))

    # setters

    def set_irc_channel(self, value): return self.settings.set("irc", "channel", value)

    def set_irc_server(self, value): return self.settings.set("irc", "server", value)

    def set_irc_port(self, value): return self.settings.set("irc", "port", value)

    def set_irc_nick(self, value): return self.settings.set("irc", "nick", value)

    def set_irc_timeout(self, value): return self.settings.set("irc", "timeout", value)

    # the getters for the vps section

    def get_vps_host(self): return self.settings.get("vps", "host")

    def get_vps_life(self): return self.settings.get("vps", "initdate")

    def get_vps_dead(self): return self.settings.get("vps", "finaldate")
