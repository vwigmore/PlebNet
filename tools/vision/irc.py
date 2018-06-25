import socket
import sys
import time
import re

class IRC:
    
    irc = socket.socket()

    def __init__(self):
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send(self, chan, msg):
        self.irc.send("PRIVMSG %s %s\r\n"%(chan, msg))

    def connect(self, server, channel, botnick):
        print("connecting to: %s"%server)
        self.irc.connect((server, 6667))
        self.irc.send("USER %s %s %s : test!\r\n" % (botnick, botnick, botnick))
        self.irc.send("NICK %s\r\n"%botnick)
        time.sleep(2)
        self.irc.send("JOIN %s\r\n"%channel)

    def get_text(self):
        text = self.irc.recv(2040)
        print(">>>" + text)
        pattern = re.compile('.*\s([0-9]+)')
        match = re.match(pattern, text)
        if match:
            self.irc.send('PONG ' + match.group(1) + '\r\n')

        return text
