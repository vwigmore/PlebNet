import sys
import os
sys.path.append(os.path.abspath('../tracker'))

import tracker_bot as tbot 
import socket 
import logging
import random 

from threading import Thread 
from time import sleep
from appdirs import user_config_dir

version = tbot.version
timeout = tbot.timeout 
patience = tbot.patience 

channel = tbot.channel 
nick = tbot.nick 
server = tbot.server 
port = tbot.port 
ask = tbot.ask 

commands = tbot.commands 

log_file_name = tbot.log_file_name 
log_data_name = tbot.log_data_name
log_file_path = tbot.log_file_path 


class Watcher(Thread):

    def __init__(self, nickname = None):
        self.channel = channel
        self.server = server
        self.timeout = timeout
        self.channel = channel
        self.port = port

        self.nick = nickname or nick
        self.ident = self.nick
        self.gecos = "%s version %s" % (self.nick, version)

        self.irc = None

        Thread.__init__(self)

    def run(self):
        try:
            self.init_irc()
        except Exception, e:
            self.log("failed to start running an tracker bot  on " + self.server + " " + self.channel)
            self.log(e)            

        thread_listen = Thread(target=self.listen)
        thread_listen.start()
        sleep(20)
        thread_asking = Thread(target=self.ask)
        thread_asking.start()

if __name__ == '__main__':
    w = Watcher('wing')
    w.daemon = True
    w.start()