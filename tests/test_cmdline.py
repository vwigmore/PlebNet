import unittest
import sys

# from unittest.mock import Mock
from mock.mock import Mock
from argparse import Namespace
from mock.mock import patch

from plebnet import cmdline
from plebnet.agent import core
from plebnet.communication.irc import irc_handler


class TestCMDLine(unittest.TestCase):

    def setUp(self):
        self.argv = sys.argv

    def tearDown(self):
        sys.argv = self.argv

    def test_setup(self):
        # store originals
        self.setup = core.setup
        # modify
        core.setup = Mock()
        sys.argv = ['plebnet', 'setup']
        # run
        cmdline.execute()
        # test
        core.setup.assert_called()
        core.setup.assert_called_once_with(Namespace(test_net=False))
        # restore
        core.setup = self.setup

    def test_setup_test(self):
        # store originals
        self.setup = core.setup
        # modify
        core.setup = Mock()
        sys.argv = ['plebnet', 'setup', '-test']
        # run
        cmdline.execute()
        # test
        core.setup.assert_called_once_with(Namespace(test_net=True))
        # restore
        core.setup = self.setup

    def test_check(self):
        # store originals
        self.check = core.check
        # modify
        core.check = Mock()
        sys.argv = ['plebnet', 'check']
        # run
        cmdline.execute()
        # test
        core.check.assert_called()
        # restore
        core.check = self.check

    def test_irc_status(self):
        self.original = irc_handler.status_irc_client
        irc_handler.status_irc_client = Mock()
        sys.argv = ['plebnet', 'irc', 'status']
        cmdline.execute()
        irc_handler.status_irc_client.assert_called()
        irc_handler.status_irc_client = self.original


if __name__ == '__main__':
    unittest.main()
