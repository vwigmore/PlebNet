from irc import *
import os, random
import time

channel = "#plebnet123"
server = "irc.undernet.org"
nickname = "wing_test"

irc = IRC()
irc.connect(server,channel,nickname)

while 1:
    text = irc.get_text()
    print text

    if "PRIVMSG" in text and channel in text and "hello" in text:
        irc.send(channel, "!alive")

    time.sleep(5) 
