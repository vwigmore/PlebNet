import platform
import random
import socket
# import sys

from plebnet.utilities import logger


class create(object):
    def __init__(self):
        print("creating an IRC connection")
        logger.log("IRC", "info", "creating an IRC connection")

        # dit moet ingeladen worden
        self.server = "irc.undernet.org"
        self.channel = "#plebnet123"

        self.botnick = "plebbot" + str(random.randint(1000, 10000))
        self.sentUser = False
        self.sentNick = False
        print("start running")
        self.run()

        # reload(sys)
        # sys.setdefaultencoding("utf8")

    def status(self):
        return irc_setup.get("irc", "status")

    def run(self):
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.irc.connect((self.server, 6667))

        try:
            while 1:
                logger.log("IRC", "info", "new round")
                text = self.irc.recv(2048)
                if len(text) == 0:
                    continue

                if text.find("PING") != -1:
                    st = "PONG " + text.split()[1] + "\n"
                    self.irc.send(st)

                if not self.sentUser:
                    st = "USER " + self.botnick + " " + self.botnick + " " + self.botnick + " : This is a fun bot \n"
                    self.irc.send(st)
                    self.sentUser = True
                    continue

                if self.sentUser and not self.sentNick:
                    st = "NICK " + self.botnick + "\n"
                    self.irc.send(st)
                    self.sentNick = True
                    continue

                if text.find("255 " + self.botnick) != -1:
                    st = "JOIN " + self.channel + "\n"
                    self.irc.send(st)

                if text.find("statusupdate") != -1:
                    st = "PRIVMSG " + self.channel + " :" + "ik werk prima: " + self.status() + "\n"
                    self.irc.send(st)

        except KeyboardInterrupt:
            st = "QUIT :I have to go for now!\n"
            self.irc.send(st)
            # sys.exit()


bot = create()
