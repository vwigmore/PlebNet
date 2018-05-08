import os

from plebnet.settings import setting


class Init(object):

    def __init__(self):
        self.filename = os.path.join(os.path.expanduser("~/PlebNet"), "plebnet/settings/configuration/setup.cfg")
        self.settings = setting.Settings(self.filename)
        self.settings.load()

    # the getters for the irc section

    def get_irc_channel(self): return self.settings.get("irc", "channel")

    def get_irc_server(self): return self.settings.get("irc", "server")

    def get_irc_port(self): return int(self.settings.get("irc", "port"))

    def get_irc_nick(self): return self.settings.get("irc", "nick")

    def get_irc_timeout(self): return int(self.settings.get("irc", "timeout"))

    # the getters for the vps section

    def get_vps_host(self): return self.settings.get("vps", "host")

    def get_vps_life(self): return self.settings.get("vps", "initdate")

    def get_vps_dead(self): return self.settings.get("vps", "finaldate")
