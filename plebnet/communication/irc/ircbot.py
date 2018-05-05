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

        self.nick = "plebbot" + str(random.randint(1000, 10000))
        self.ident = "plebber"
        self.gecos = "Plebbot version 1.0"

        self.sentUser = False
        self.sentNick = False
        self.irc = None
        self.init_time = time.time()
        self.last_beat = time.time()

        # start running the IRC server
        logger.log("start running an IRC connection on " + self.server + " " + self.channel)
        self.run()

    def run(self):
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.irc.connect((self.server, self.port))
        self.irc.connect(("irc.undernet.org", 6667))

        try:
            buffer = ""

            # init the contact
            # self.send("USER %s %s %s %s\r\n" % (self.nick, self.nick, self.nick, self.nick))
            # self.irc.send("NICK %s\r\n" % self.nick)
            # self.irc.send("USER %s %s %s : %s\r\n" % (self.nick, self.nick,  self.nick, self.gecos))
            # time.sleep(30)
            # time.sleep(30)
            # self.irc.send("JOIN " + self.channel + "\n")
            # time.sleep(10)

            while 1:

                self.heartbeat()

                buffer = buffer + self.irc.recv(2048)
                lines = str.split(buffer, "\r\n")
                buffer = lines.pop()

                for line in lines:
                    logger.log("Received IRC message: " + line)

                for line in lines:
                    self.handle_line(line)

        except KeyboardInterrupt:
            st = "QUIT :I have to go for now!\r\n"
            self.irc.send(st)
            # sys.exit()
        except:
            logger.log("An error occurred at the IRC")
            logger.log(traceback.format_exc())
            st = "QUIT :I have to go for now!\r\n"
            self.irc.send(st)

    def heartbeat(self):
        timer = time.time()
        elapsed_time = timer - self.last_beat

        if elapsed_time > self.timeout and self.sentUser and self.sentNick:
        # if elapsed_time > self.timeout:
            self.last_beat = timer
            time_str = time.strftime("%H:%M:%S", time.gmtime(timer - self.init_time))
            logger.log("IRC is still running: alive for " + time_str)
            self.send("IRC is still running: alive for %s\r\n" % time_str)

    def handle_line(self, line):
        # logger.log("Received IRC message: " + line)

        line = str.rstrip(line)
        words = str.split(line)

        if words[0] == "PING":
            st = "PONG %s\n" % words[1]
            self.irc.send(st)

        elif not self.sentNick:
            # time.sleep(30)
            st = "NICK %s\r\n" % self.nick
            logger.log("Sending an IRC message: " + st)
            self.irc.send(st)
            self.sentNick = True

        elif not self.sentUser:
            # st = "USER " + self.nick + " " + self.nick + " " + self.nick + " : This is a fun bot \n"
            st = "USER %s %s %s :%s\r\n" % (self.nick, self.nick, self.nick, self.gecos)
            logger.log("Sending an IRC message: " + st)
            self.irc.send(st)
            self.sentUser = True

        elif line.find("255 " + self.nick) != -1:
            time.sleep(30)
            st = "JOIN " + self.channel + "\r\n"
            logger.log("Sending an IRC message: " + st)
            self.irc.send(st)

        elif line.find("statusupdate") != -1:
            self.status()

    def send(self, msg):
        logger.log("Sending an IRC message: PRIVMSG %s :%s" % (self.channel,  msg))
        self.irc.send("PRIVMSG %s :%s" % (self.channel,  msg))

    # the reply functions
    def status(self):
        self.send("ik werk prima \r\n")


bot = Create()
