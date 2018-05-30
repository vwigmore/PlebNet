import responses
import requests
import unittest

import plebnet.controllers.wallet_controller as walletcontroller
import plebnet.controllers.market_controller as marketcontroller
import plebnet.settings.plebnet_settings as plebnet_settings

from mock.mock import MagicMock
from plebnet.utilities import logger


class TestWalletController(unittest.TestCase):

    def setUp(self):
        self.settings_true = plebnet_settings.Init.wallets_testnet_created
        self.true_logger = logger.log
        self.true_market = marketcontroller.is_market_running
        self.settings_password = plebnet_settings.Init.wallets_password
        logger.log = MagicMock()
        plebnet_settings.Init.wallets_testnet_created = MagicMock(return_value=False)
        marketcontroller.is_market_running = MagicMock(return_value=True)
        plebnet_settings.Init.wallets_password = MagicMock(return_value="plebnet")

    def tearDown(self):
        logger.log = self.true_logger
        plebnet_settings.Init.wallets_testnet_created = self.settings_true
        marketcontroller.is_market_running = self.true_market
        plebnet_settings.Init.wallets_password = self.settings_password

    def test_create_wallet_testnet_created(self):
        plebnet_settings.Init.wallets_testnet_created = MagicMock(return_value=True)
        assert walletcontroller.create_wallet('TBTC')

    def test_create_wallet_wrong_type(self):
        self.assertFalse(walletcontroller.create_wallet('nonesense'))

    def test_create_wallet_no_market(self):
        marketcontroller.is_market_running = MagicMock(return_value=False)
        self.assertFalse(walletcontroller.create_wallet('TBTC'))

    @responses.activate
    def test_create_wallet_true(self):
        responses.add(responses.PUT, 'http://localhost:8085/wallet/TBTC', json={'created': True})
        assert walletcontroller.create_wallet('TBTC')

    @responses.activate
    def test_create_wallet_already_created(self):
        responses.add(responses.PUT, 'http://localhost:8085/wallet/TBTC', json={'error': 'this wallet already exists'})
        assert walletcontroller.create_wallet('TBTC')

    @responses.activate
    def test_create_wallet_different_error(self):
        responses.add(responses.PUT, 'http://localhost:8085/wallet/TBTC', json={'error': 'unspecified error'})
        self.assertFalse(walletcontroller.create_wallet('TBTC'))

    def test_create_wallet_error(self):
        self.requests = requests.put
        requests.put = MagicMock(side_effect=requests.ConnectionError)
        self.assertFalse(walletcontroller.create_wallet('TBTC'))
        requests.put = self.requests


if __name__ == '__main__':
    unittest.main()