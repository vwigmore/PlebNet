#! /usr/bin/env python

import sys
import os
import socket 
import logging
import random 

import threading
from time import sleep
from appdirs import user_config_dir

# load defaults
version = "0.1"
timeout = 60*10
patience = 2 # waiting time between asks, for order, prevent flooding

channel = "#plebnet123"
nick = "watcher"
server = "irc.undernet.org"
port = 6669
ask = True

commands = ["!MB_balance", "!BTC_balance", "!TBTC_balance", "!matchmakers", "!uploaded", "!downloaded"]

log_file_name = "tracker.log"
log_data_name = "tracker.data"
log_file_path = user_config_dir()


class Watcher:
    def __init__(self, nickname = None):
        self.name = nickname 

        logging.basicConfig(format="%(threadName)s:%(message)s", level='NOTSET')        

        global t
        t = threading.Timer(1, self.listen)
        t.daemon = True
        t.start()

        global tt
        tt = threading.Timer(1, self.ask)
        tt.daemon = True
        tt.start()        

        while True:
            sleep(1)

    def listen(self):
        logging.info("listening! %d" % threading.active_count())
        t = threading.Timer(1, self.listen)
        t.daemon = True
        t.start()

    def ask(self):
        logging.info("ask! %d" % threading.active_count())
        tt = threading.Timer(5, self.ask)
        tt.daemon = True
        tt.start()        
 
if __name__ == '__main__':
    Watcher()