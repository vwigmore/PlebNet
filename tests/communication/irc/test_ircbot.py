import unittest

from plebnet.communication.irc import ircbot

reply_host = "My host is : "
reply_ping = "PONG 1234"
reply_alive = "I am alive, for"

line_ping = "PING 1234"
line_host = "a b c :!host"
line_alive = "a b c :!alive"


class TestIRCbot(unittest.TestCase):

    msgs = None

    def setUp(self):
        global msgs
        # store originals
        self.original_send = ircbot.Create.send
        self.original_run = ircbot.Create.run
        self.original_init_irc = ircbot.Create.init_irc
        # modify
        ircbot.Create.send = self.append_msg
        ircbot.Create.run = self.skip
        ircbot.Create.init_irc = self.skip
        # create instance with modified properties
        self.instance = ircbot.Create()
        # empty the send messages
        msgs = []

    def tearDown(self):
        # restore originals
        ircbot.Create.send_msg = self.original_send
        ircbot.Create.send_run = self.original_run
        ircbot.Create.init_irc = self.original_init_irc

    """ USED FOR REPLACEMENTS """

    def append_msg(self, msg): msgs.append(msg)

    def skip(self): pass

    class irc_server(object):
        def __init__(self):
            pass

        def recv(self, x=None):
            return ""

    """ THE ACTUAL TESTS """

    def test_handle_lines_ping(self):
        self.instance.handle_line(line_ping)
        self.assertIn(reply_ping, msgs[0])

    def test_handle_lines_host(self):
        self.instance.handle_line(line_host)
        self.assertIn(reply_host, msgs[0])

    def test_keep_running(self):
        self.instance.irc = self.irc_server()
        msg = "%s\r\n%s\r\n%s\r\n" % (line_ping, line_host, line_alive)
        self.instance.keep_running(msg)
        self.assertIn(reply_ping, msgs[0])
        self.assertIn(reply_host, msgs[1])
        self.assertIn(reply_alive, msgs[2])


if __name__ == '__main__':
    unittest.main()