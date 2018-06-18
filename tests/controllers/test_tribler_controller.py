import unittest
import subprocess
import plebnet.controllers.tribler_controller as Tribler
from mock.mock import MagicMock
from plebnet.utilities import logger
import plebnet.settings.plebnet_settings as Settings


class TestTriblerController(unittest.TestCase):

    def test_start(self):
        self.true_logger_log = logger.log
        self.true_logger_success = logger.success
        self.true_subprocess_call = subprocess.call
        self.true_setup = Settings.Init.wallets_testnet

        logger.log = MagicMock()
        logger.success = MagicMock()
        Settings.Init.wallets_testnet = MagicMock(return_value=True)
        subprocess.call = MagicMock(return_value=True)
        assert(Tribler.start())

        Settings.Init.wallets_testnet = self.true_setup
        subprocess.call = self.true_subprocess_call
        logger.log = self.true_logger_log
        logger.success = self.true_logger_success

    def test_start_False(self):
        self.true_subprocess_call = subprocess.call
        self.true_logger_error = logger.error
        self.true_setup = Settings.Init.wallets_testnet

        subprocess.call = MagicMock(return_value=False)
        Settings.Init.wallets_testnet = MagicMock(return_value=False)
        logger.error = MagicMock()
        self.assertFalse(Tribler.start())

        subprocess.call = self.true_subprocess_call
        logger.error = self.true_logger_error
        Settings.Init.wallets_testnet = self.true_setup


    def test_start_exception(self):
        self.true_subprocess_call = subprocess.call
        self.true_logger_error = logger.error
        self.true_setup = Settings.Init.wallets_testnet

        subprocess.call = MagicMock(side_effect=subprocess.CalledProcessError(returncode=2,cmd=['bad']))
        Settings.Init.wallets_testnet = MagicMock(return_value=True)
        logger.error = MagicMock()
        self.assertFalse(Tribler.start())

        logger.error = self.true_logger_error
        subprocess.call = self.true_subprocess_call
        Settings.Init.wallets_testnet = self.true_setup

if __name__ == '__main__':
    unittest.main()