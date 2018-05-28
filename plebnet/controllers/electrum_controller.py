"""
This file is used to control all dependencies with Electrum.

Other files should never have a direct import from Electrum, as the reduces the maintainability of this code.
If Electrum alters its call methods, this should be the only file which needs to be updated in PlebNet.
"""


import os
import tribler_controller as triblercontroller
import market_controller as marketcontroller
import plebnet.settings.plebnet_settings as plebnet_settings
#import electrum
import requests
from requests.exceptions import ConnectionError
#from electrum import Wallet as ElectrumWallet
#from electrum import WalletStorage
#from electrum import keystore
#from electrum.mnemonic import Mnemonic
from plebnet.utilities import logger
#WALLET_FILE = os.path.expanduser("~/.electrum/wallets/default_wallet")
settings = plebnet_settings.get_instance()


def create_wallet(wallet_type):
    if settings.wallets_testnet():
        logger.log("Wallet already created", "create_wallet")
        return True
    if wallet_type != 'BTC' or 'TBTC':
        logger.log("Called wrong wallet type", "create_wallet")
        return False
    start_tribler = triblercontroller.start()
    start_market = marketcontroller.is_market_running()
    if not start_tribler or start_market:
        logger.log("Tribler or the marketplace can't be started", "create_wallet")
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


#def create_wallet():
#    """
#    Create an electrum wallet if it does not exist
#    :return:
#    """
#    if not os.path.isfile(WALLET_FILE):
#        logger.log("Creating wallet", "create_wallet")
#        config = electrum.SimpleConfig()
#        storage = WalletStorage(config.get_wallet_path())
#        passphrase = config.get('passphrase', '')
#        seed = Mnemonic('en').make_seed()
#        k = keystore.from_seed(seed, passphrase)
#        k.update_password(None, None)
#       storage.put('keystore', k.dump())
#       storage.put('wallet_type', 'standard')
#       storage.put('use_encryption', False)
#       storage.write()
#       wallet = ElectrumWallet(storage)
#       wallet.synchronize()
#       logger.log("Your wallet generation seed is:\n\"%s\"" % seed, "create_wallet")
#       logger.log("Please keep it in a safe place; once lost, your wallet cannot be restored.", "create_wallet")
#       wallet.storage.write()
#       logger.log("Wallet saved in '%s'" % wallet.storage.path, "create_wallet")
#   else:
#       logger.log("Wallet already present", "create_wallet")

