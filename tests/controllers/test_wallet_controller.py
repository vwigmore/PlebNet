import json
import subprocess
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

    def test_create_wallet_true(self):
        self.popen = subprocess.Popen.communicate
        self.json = json.loads

        subprocess.Popen.communicate = MagicMock()

        json.loads = MagicMock(return_value= 'created')
        assert walletcontroller.create_wallet('TBTC')

        json.loads = self.json
        subprocess.Popen.communicate = self.popen

    def test_create_wallet_already_created(self):
        self.popen = subprocess.Popen.communicate
        self.json = json.loads
        json.loads = MagicMock(return_value={'error': 'this wallet already exists'})

        assert walletcontroller.create_wallet('TBTC')

        json.loads = self.json
        subprocess.Popen.communicate = self.popen

    def test_create_wallet_different_error(self):
        self.popen = subprocess.Popen.communicate
        self.json = json.loads
        json.loads = MagicMock(return_value={'error': 'unspecified error'})

        self.assertFalse(walletcontroller.create_wallet('TBTC'))

        json.loads = self.json
        subprocess.Popen.communicate = self.popen

    def test_create_wallet_error(self):
        self.popen = subprocess.Popen.communicate
        subprocess.Popen.communicate = MagicMock(side_effect=requests.ConnectionError)

        self.assertFalse(walletcontroller.create_wallet('TBTC'))

        subprocess.Popen.communicate = self.popen

    def test_tribler_wallet_constructor(self):
        r = walletcontroller.TriblerWallet()
        assert r.coin == 'BTC'
        o = walletcontroller.TriblerWallet(True)
        assert o.coin == 'TBTC'

    def test_get_balance(self):
        self.popen = subprocess.Popen.communicate
        self.json = json.loads

        json.loads = MagicMock()
        subprocess.Popen.communicate = MagicMock()
        r = walletcontroller.TriblerWallet()

        r.get_balance()
        json.loads.assert_called_once()
        subprocess.Popen.communicate.assert_called_once()

        json.loads = self.json
        subprocess.Popen.communicate = self.popen

    def test_pay_not_enough_balance(self):
        self.balance = walletcontroller.TriblerWallet.get_balance
        self.popen = subprocess.Popen.communicate
        walletcontroller.TriblerWallet.get_balance = MagicMock(return_value=0)
        subprocess.Popen.communicate = MagicMock()

        r = walletcontroller.TriblerWallet()
        r.pay('address', 30)
        walletcontroller.TriblerWallet.get_balance.assert_called_once()
        subprocess.Popen.communicate.assert_not_called()

        walletcontroller.TriblerWallet.get_balance = self.balance
        subprocess.Popen.communicate = self.popen

    """
    class used so that a mocked object returns a MockResponse object with a __getitem__ attribute that returns false
    """
    class MockResponse(object):

        def __init__(self, obj):
            self.x = obj

        def __getitem__(self, item):
            return self.x

    def test_pay_no_response(self):
        self.balance = walletcontroller.TriblerWallet.get_balance
        self.popen = subprocess.Popen.communicate
        self.json = json.loads
        walletcontroller.TriblerWallet.get_balance = MagicMock(return_value=50)
        subprocess.Popen.communicate = MagicMock(return_value=self.MockResponse(False))
        json.loads = MagicMock()

        r = walletcontroller.TriblerWallet()
        r.pay('address', 30)

        walletcontroller.TriblerWallet.get_balance.assert_called_once()
        subprocess.Popen.communicate.assert_called_once()
        json.loads.assert_not_called()

        walletcontroller.TriblerWallet.get_balance = self.balance
        subprocess.Popen.communicate = self.popen
        json.loads = self.json

    def test_pay(self):
        self.balance = walletcontroller.TriblerWallet.get_balance
        self.popen = subprocess.Popen.communicate
        self.json = json.loads

        walletcontroller.TriblerWallet.get_balance = MagicMock(return_value=50)
        subprocess.Popen.communicate = MagicMock()
        json.loads = MagicMock(returun_value='test')

        r = walletcontroller.TriblerWallet()
        r.pay('address', 30)

        json.loads.assert_called_once()

        walletcontroller.TriblerWallet.get_balance = self.balance
        subprocess.Popen.communicate = self.popen
        json.loads = self.json





if __name__ == '__main__':
    unittest.main()