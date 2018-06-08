"""
This file is used to control all dependencies of the Electrum wallet using the Tribler API.

Other files should never have a direct import from Electrum, as the reduces the maintainability of this code.
If Electrum alters its call methods, this should be the only file which needs to be updated in PlebNet.
"""

import os
import json
import subprocess
import market_controller as marketcontroller
import plebnet.settings.plebnet_settings as plebnet_settings
import requests
from requests.exceptions import ConnectionError
from plebnet.utilities import logger

WALLET_FILE = os.path.expanduser("~/.electrum/wallets/default_wallet")
settings = plebnet_settings.get_instance()


def create_wallet(wallet_type):
    if wallet_type == 'TBTC' and settings.wallets_testnet_created():
        logger.log("Testnet wallet already created", "create_wallet")
        return True
    if wallet_type != 'BTC' and wallet_type != 'TBTC':
        logger.log("Called unknown wallet type", "create_wallet")
        return False
    start_market = marketcontroller.is_market_running()
    if not start_market:
        logger.log("The marketplace can't be started", "create_wallet")
        return False
    try:
        data = ['curl', '-X', 'PUT', 'http://localhost:8085/wallets/' + wallet_type, '--data', '\"password=' + settings.wallets_password() + '\"']
        response = subprocess.Popen(data, stdout=subprocess.PIPE).communicate()[0]
        message = json.loads(response)

        if 'created' in message:
            logger.log("Wallet created successfully", "create_wallet")
            return True
        elif message['error'] == 'this wallet already exists':
            logger.log("The wallet was already created", "create_wallet")
            return True
        else:
            logger.log(str(message['error']), "create_wallet")
            return False
    except ConnectionError:
        logger.log("connection error while creating a wallet", "create_wallet")
        return False


class TriblerWallet(object):
    """
    This class expects Tribler to be running and uses the wallet created via Tribler.
    Either a TBTC or a BTC wallet.
    """

    def __init__(self, testnet=None):
        if testnet:
            self.coin = 'TBTC'
        else:
            self.coin = 'BTC'

    def get_balance(self):
        """
        Returns the balance of the current wallet
        :return: the balance
        """
        data = ['curl', '-X', 'GET', 'http://localhost:8085/wallets/' + self.coin + '/balance']

        response = subprocess.Popen(data, stdout=subprocess.PIPE).communicate()[0]
        available = json.loads(response)['balance']['available']
        return float(available)

    def pay(self, address, amount, fee=None):
        """

        :param address: the address of the receiver
        :param amount: the amount to be sent excluding fee
        :param fee: the fee to be used, 0 if None
        :return: the transaction hash
        """

        tx_fee = 0 if fee is None else fee

        if self.get_balance() < amount + tx_fee:
            print('Not enough funds')
            return

        data = ['curl', '-X', 'POST', 'http://localhost:8085/wallets/' + self.coin + '/transfer',
                '--data', 'amount=' + str(amount + tx_fee) + '&destination=' + address]

        response = subprocess.Popen(data, stdout=subprocess.PIPE).communicate()[0]

        if not response:
            print('Transaction unsuccessfull')
        else:
            print('Transaction successful')
            transaction_hash = json.loads(response)['txid']
            print(transaction_hash)
            return transaction_hash


def get_wallet_address(type):
    try:
        return requests.get('http://localhost:8085/wallets/').json()[type]['address']
    except ConnectionError:
        return "No %s wallet found" % type


def get_TBTC_wallet(): return get_wallet_address('TBTC')


def get_BTC_wallet(): return get_wallet_address('BTC')


def get_MB_wallet(): return get_wallet_address('MB')


def get_balance(type):
    try:
        return requests.get('http://localhost:8085/wallets/').json()[type]['balance']['available']
    except ConnectionError:
        return "No %s wallet found" % type


def get_TBTC_balance(): return get_balance('TBTC')


def get_BTC_balance(): return get_balance('BTC')


def get_MB_balance(): return get_balance('MB')


