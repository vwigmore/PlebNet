#! /usr/bin/env python

import platform
import random
import socket
import sys

# as the file is loaded separately, the imports have to be fixed
sys.path.append('/root/PlebNet')
from plebnet.utilities import logger
from plebnet.settings import setup_settings


class Create(object):
    def __init__(self):
        logger.log("preparing an IRC connection")

        irc_settings = setup_settings.Init()
        self.server = irc_settings.get_irc_server()
        # dit moet ingeladen worden
        self.channel = "#plebnet123"
        self.botnick = "plebbot" + str(random.randint(1000, 10000))
        self.sentUser = False
        self.sentNick = False
        logger.log("start running an IRC connection")
        self.irc = None
        self.run()

    def run(self):
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.irc.connect((self.server, 6667))

        try:
            while 1:
                logger.log("Still running an IRC connection")
                text = self.irc.recv(2048)
                if len(text) == 0:
                    continue

                if text.find("PING") != -1:
                    st = "PONG " + text.split()[1] + "\n"
                    self.send(st)

                if not self.sentUser:
                    st = "USER " + self.botnick + " " + self.botnick + " " + self.botnick + " : This is a fun bot \n"
                    self.send(st)
                    self.sentUser = True
                    continue

                if self.sentUser and not self.sentNick:
                    st = "NICK " + self.botnick + "\n"
                    self.send(st)
                    self.sentNick = True
                    continue

                if text.find("255 " + self.botnick) != -1:
                    st = "JOIN " + self.channel + "\n"
                    self.send(st)

                if text.find("statusupdate") != -1:
                    self.status()

        except KeyboardInterrupt:
            st = "QUIT :I have to go for now!\n"
            self.irc.send(st)
            # sys.exit()

    def send(self, msg):
        logger.log("Sending an IRC message: " + msg)
        self.irc.send(msg)

    # the reply functions
    def status(self):
        self.send("PRIVMSG " + self.channel + " :" + "ik werk prima \n")


bot = Create()
