#! /usr/bin/env python

import platform
import traceback
import random
import socket
import time
import sys

# as the file is loaded separately, the imports have to be fixed
sys.path.append('/root/PlebNet')
from plebnet.utilities import logger
from plebnet.settings import setup_settings


class Create(object):
    def __init__(self):
        logger.log("preparing an IRC connection")

        # load required settings once
        irc_settings = setup_settings.Init()
        self.server = irc_settings.get_irc_server()
        self.timeout = irc_settings.get_irc_timeout()
        self.channel = irc_settings.get_irc_channel()
        self.port = irc_settings.get_irc_port()
        self.botnick = "plebbot" + str(random.randint(1000, 10000))
        self.sentUser = False
        self.sentNick = False
        self.irc = None
        self.inittime = time.time()
        self.heartbeat = time.time()

        # start running the IRC server
        logger.log("start running an IRC connection on " + self.server + " " + self.channel)
        self.run()

    def run(self):
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.irc.connect((self.server, self.port))
        self.irc.connect(("irc.undernet.org", 6667))

        try:
            while 1:
                # handle heartbeat
                timer = time.time()
                elapsed_time = timer - self.heartbeat

                if elapsed_time > self.timeout:
                    self.heartbeat = timer
                    timestr = time.strftime("%H:%M:%S", time.gmtime(timer - self.inittime))
                    logger.log("Still running an IRC connection: alive for " + timestr)
                    self.send("Still running an IRC connection: alive for " + timestr)

                text = self.irc.recv(2048)
                if len(text) == 0:
                    continue
                logger.log("Received an IRC message: " + text)

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
        except:
            logger.log("An error occurred at the IRC")
            logger.log(traceback.format_exc())
            st = "QUIT :I have to go for now!\n"
            self.irc.send(st)

    def send(self, msg):
        logger.log("Sending an IRC message: " + msg)
        self.irc.send("PRIVMSG " + self.channel + " :" + msg)

    # the reply functions
    def status(self):
        self.send("ik werk prima \n")


bot = Create()
