"""
This file is used to control all dependencies of the Electrum wallet using the Tribler API.

Other files should never have a direct import from Electrum, as the reduces the maintainability of this code.
If Electrum alters its call methods, this should be the only file which needs to be updated in PlebNet.
"""

import os
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
        data = {'password': settings.wallets_password()}
        r = requests.put('http://localhost:8085/wallet/' + wallet_type, data=data)
        response = r.json()
        if 'created' in response:
            logger.log("Wallet created successfully", "create_wallet")
            return True
        elif response['error']['message'] == 'this wallet already exists':
            logger.log("The wallet was already created", "create_wallet")
            return True
        else:
            logger.log(response['error']['message'], "create_wallet")
            return False
    except ConnectionError:
        logger.log("connection error while creating a wallet", "create_wallet")
        return False




