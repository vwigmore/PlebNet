import unittest
from plebnet.agent.dna import DNA
from plebnet.agent.config import PlebNetConfig
from plebnet.clone import server_installer
from plebnet.controllers import tribler_controller, cloudomate_controller, market_controller, wallet_controller
from plebnet.communication.irc import irc_handler
from plebnet.settings import plebnet_settings
from mock.mock import MagicMock
from plebnet.utilities import logger, fake_generator
import plebnet.agent.core as Core
import mock
import os
from appdirs import user_config_dir

from plebnet.agent.dna import DNA


class TestCore(unittest.TestCase):

    def test_create_wallet_testnet(self):
        self.settings = plebnet_settings.Init.wallets_testnet
        self.logger = logger.log
        self.wallet = wallet_controller.create_wallet
        self.wallet_created = plebnet_settings.Init.wallets_testnet_created
        self.initiated = plebnet_settings.Init.wallets_initiate_once
        self.write = plebnet_settings.write

        plebnet_settings.Init.wallets_testnet = MagicMock(return_value=True)
        logger.log = MagicMock()
        wallet_controller.create_wallet = MagicMock(return_value=True)
        plebnet_settings.Init.wallets_testnet_created = MagicMock()
        plebnet_settings.Init.wallets_initiate_once = MagicMock()
        plebnet_settings.write = MagicMock()

        Core.create_wallet()
        self.assertEqual(os.environ.get('TESTNET'), '1')
        os.environ['TESTNET'] = '0'

        plebnet_settings.Init.wallets_testnet = self.settings
        logger.log = self.logger
        wallet_controller.create_wallet = self.wallet
        plebnet_settings.Init.wallets_testnet_created = self.wallet_created
        plebnet_settings.Init.wallets_initiate_once = self.initiated
        plebnet_settings.write = self.write

    def test_create_wallet_bitcoin(self):
        self.settings = plebnet_settings.Init.wallets_testnet
        self.logger = logger.log
        self.wallet = wallet_controller.create_wallet
        self.initiated = plebnet_settings.Init.wallets_initiate_once
        self.write = plebnet_settings.setting.Settings.write

        plebnet_settings.Init.wallets_testnet = MagicMock(return_value=False)
        logger.log = MagicMock()
        wallet_controller.create_wallet = MagicMock(return_value=True)
        plebnet_settings.Init.wallets_initiate_once = MagicMock()
        plebnet_settings.setting.Settings.write = MagicMock()

        Core.create_wallet()
        plebnet_settings.Init.wallets_initiate_once.assert_called_once()
        plebnet_settings.setting.Settings.write.assert_called_once()

        plebnet_settings.Init.wallets_testnet = self.settings
        logger.log = self.logger
        wallet_controller.create_wallet = self.wallet
        plebnet_settings.Init.wallets_initiate_once = self.initiated
        plebnet_settings.setting.Settings.write = self.write

    def test_check_tribler_true(self):
        self.running = tribler_controller.running
        self.logger = logger.log

        tribler_controller.running = MagicMock(return_value=True)
        logger.log = MagicMock()
        assert Core.check_tribler()

        tribler_controller.running = self.running
        logger.log = self.logger

    def test_check_tribler_false(self):
        self.running = tribler_controller.running
        self.start = tribler_controller.start
        self.logger = logger.log

        tribler_controller.start = MagicMock()
        tribler_controller.running = MagicMock(return_value=False)
        logger.log = MagicMock()
        self.assertFalse(Core.check_tribler())

        tribler_controller.running = self.running
        logger.log = self.logger
        tribler_controller.start = self.start

    def test_setup(self):
        self.logger = logger.log
        self.provider = cloudomate_controller.get_vps_providers
        self.DNA = DNA.read_dictionary
        self.settings = plebnet_settings.Init.wallets_testnet
        self.fake = fake_generator.generate_child_account
        self.irc_nic = plebnet_settings.Init.irc_nick
        self.irc_def = plebnet_settings.Init.irc_nick_def
        self.save = PlebNetConfig.save
        self.init_client = irc_handler.init_irc_client
        self.start_client = irc_handler.start_irc_client
        self.success = logger.success

        args = MagicMock()
        args.testnet = True
        logger.log = MagicMock()
        fake_generator.generate_child_account = MagicMock()
        plebnet_settings.Init.wallets_testnet = MagicMock()
        cloudomate_controller.get_vps_providers = MagicMock()
        DNA.read_dictionary = MagicMock()
        plebnet_settings.Init.irc_nick = MagicMock()
        plebnet_settings.Init.irc_nick_def = MagicMock()
        PlebNetConfig.save = MagicMock()
        irc_handler.init_irc_client = MagicMock()
        irc_handler.start_irc_client = MagicMock()
        logger.success = MagicMock()

        Core.setup(args)
        logger.success.assert_called_once()

        logger.log = self.logger
        cloudomate_controller.get_vps_providers = self.provider
        DNA.read_dictionary = self.DNA
        plebnet_settings.Init.wallets_testnet = self.settings
        fake_generator.generate_child_account = self.fake
        plebnet_settings.Init.irc_nick = self.irc_nic
        plebnet_settings.Init.irc_nick_def = self.irc_def
        PlebNetConfig.save = self.save
        irc_handler.init_irc_client = self.init_client
        irc_handler.start_irc_client = self.start_client
        logger.success = self.success

    def test_check(self):
        self.logger = logger.log
        self.wallet_created = plebnet_settings.Init.wallets_testnet_created
        self.tribler = Core.check_tribler
        self.DNA = DNA.read_dictionary
        self.initiated = plebnet_settings.Init.wallets_initiate_once
        self.cw = Core.create_wallet
        self.sp = Core.select_provider
        self.hm = market_controller.has_matchmakers
        self.uo = Core.update_offer
        self.ap = Core.attempt_purchase
        self.iv = Core.install_vps

        logger.log = MagicMock()
        plebnet_settings.Init.wallets_testnet_created = MagicMock(return_value=True)
        Core.check_tribler = MagicMock(return_value=False)
        DNA.read_dictionary = MagicMock()
        plebnet_settings.Init.wallets_initiate_once = MagicMock(return_value=False)
        Core.create_wallet = MagicMock()
        Core.select_provider = MagicMock()
        market_controller.has_matchmakers = MagicMock(return_value=True)
        Core.update_offer = MagicMock()
        Core.attempt_purchase = MagicMock()
        Core.install_vps = MagicMock()

        Core.check()
        os.environ['TESTNET'] = '0'

        plebnet_settings.Init.wallets_testnet_created = MagicMock(return_value=False)
        Core.check_tribler = MagicMock(return_value=True)

        Core.check()
        Core.install_vps.assert_called_once()
        Core.attempt_purchase.assert_called_once()
        Core.create_wallet.assert_called_once()

        logger.log = self.logger
        plebnet_settings.Init.wallets_testnet_created = self.wallet_created
        Core.check_tribler = self.tribler
        DNA.read_dictionary = self.DNA
        plebnet_settings.Init.wallets_initiate_once = self.initiated
        Core.create_wallet = self.cw
        Core.select_provider = self.sp
        market_controller.has_matchmakers = self.hm
        Core.update_offer = self.uo
        Core.attempt_purchase = self.ap
        Core.install_vps = self.iv










if __name__ == '__main__':
    unittest.main()