# -*- coding: utf-8 -*-

"""
This file is used to control all dependencies with Cloudomate.

Other files should never have a direct import from Cloudomate, as the reduces the maintainability of this code.
If Cloudomate alters its call methods, this should be the only file which needs to be updated in PlebNet.
"""

import cloudomate
import os, io
from os import path
from appdirs import user_config_dir

from cloudomate import wallet as wallet_util
from cloudomate.cmdline import providers as cloudomate_providers
from cloudomate.hoster.vps.clientarea import ClientArea
from cloudomate.util.settings import Settings as AccountSettings
from cloudomate.hoster.vps.proxhost import ProxHost

from plebnet.agent.config import PlebNetConfig
from plebnet.controllers import market_controller
from plebnet.controllers.wallet_controller import TriblerWallet
from plebnet.settings import plebnet_settings
from plebnet.utilities import logger, fake_generator
from plebnet.agent.dna import DNA

def get_vps_providers():
    return cloudomate_providers['vps']


def get_vpn_providers():
    return cloudomate_providers['vpn']

def child_account(index=None):
    """
    This method returns the configuration for a certain child number
    :param index: The number of the child
    :type index: Integer
    :return: configuration of the child
    :rtype: Config
    """
    if index > -1:
        account = AccountSettings()
        account.read_settings(
            os.path.join(user_config_dir(), 'child_config' + str(index) + '.cfg'))
    else:
        account = AccountSettings()
        account.read_settings(
            os.path.join(user_config_dir(), 'child_config' + str(PlebNetConfig().get("child_index")) + '.cfg'))
    return account


def status(provider):
    """
    This method returns the status parameters of a provider as specified in cloudomate.
    :param provider: The provider to check
    :type provider: dict
    :return: status
    :rtype: String
    """
    account = child_account()
    return provider.get_status(account)


def get_ip(provider, account):
    logger.log('get ip: %s' % provider)
    if provider == ProxHost:

        provider_instance = provider(account)
        ip = provider_instance.get_configuration().ip

        return ip
    else:
        client_area = ClientArea(provider._create_browser(), provider.get_clientarea_url(), account)
        logger.log('client area: %s' % client_area.get_services())
        return client_area.get_ip()


def setrootpw(provider, password):
    settings = child_account()
    settings.put('server', 'root_password', password)
    return #provider.set_rootpw(settings)


def options(provider):
    return provider.get_options()


def get_network_fee():
    return wallet_util.get_network_fee()


def pick_provider(providers):
    provider = DNA.choose_provider(providers)
    gateway = get_vps_providers()[provider].get_gateway()
    option, price, currency = pick_option(provider)
    btc_price = gateway.estimate_price(
        wallet_util.get_price(price, currency)) + get_network_fee()
    return provider, option, btc_price


def pick_option(provider):
    """
    Pick most favorable option at a provider. For now pick cheapest option
    :param provider:
    :return: (option, price, currency)
    """
    vpsoptions = options(cloudomate_providers['vps'][provider])
    if len(vpsoptions) == 0:
        return

    cheapest_option = 0
    for item in range(len(vpsoptions)):
        if vpsoptions[item].price < vpsoptions[cheapest_option].price:
            cheapest_option = item

    logger.log("cheapest option: %s" % str(vpsoptions[cheapest_option]))

    return cheapest_option, vpsoptions[cheapest_option].price, 'USD'


def update_offer(config):
    if not config.get('chosen_provider'):
        return
    (provider, option, _) = config.get('chosen_provider')
    btc_price = calculate_price(provider, option) * 1.15
    place_offer(btc_price, config)


def calculate_price(provider, option):
    logger.log('provider: %s option: %s' % (provider, option), "cloudomate_controller")
    vps_option = options(cloudomate_providers['vps'][provider])[option]
    gateway = cloudomate_providers['vps'][provider].get_gateway()
    btc_price = gateway.estimate_price(
        wallet_util.get_price(vps_option.price, 'USD')) + get_network_fee()
    return btc_price


def calculate_price_vpn(vpn_provider):
    logger.log('vpn provider: %s' % (vpn_provider), "cloudomate_controller")
    # option is assumed to be the first one
    vpn_option = options(get_vpn_providers()[vpn_provider])[0]
    gateway = get_vpn_providers()[vpn_provider].get_gateway()
    btc_price = gateway.estimate_price(
        cloudomate.wallet.get_price(vpn_option.price, 'USD')) + cloudomate.wallet.get_network_fee()
    return btc_price

def purchase_choice_vpn(config):
    provider = plebnet_settings.get_instance().vpn_host()

    provider_instance = get_vpn_providers()[provider](child_account())

    # no need to generate new child config

    wallet = TriblerWallet(plebnet_settings.get_instance().wallets_testnet_created())
    c = cloudomate_providers['vpn'][provider]

    configurations = c.get_options()
    # option is assumbed to be the first vpn provider option
    option = configurations[0]

    transaction_hash = provider_instance.purchase(wallet, option)

    if not transaction_hash:
        logger.warning("Failed to purchase vpn")
        return plebnet_settings.FAILURE
    if False:
        logger.warning("Insufficient funds to purchase server")
        return plebnet_settings.UNKNOWN

    config.get('bought').append((provider, transaction_hash, config.get('child_index')))
    config.get('transactions').append(transaction_hash)
    config.save()

    return plebnet_settings.SUCCESS


def purchase_choice(config):
    """
    Purchase the cheapest provider in chosen_providers. If buying is successful this provider is moved to bought. In any
    case the provider is removed from choices.
    :param config: config
    :return: success
    """

    (provider, option, _) = config.get('chosen_provider')
    provider_instance = cloudomate_providers['vps'][provider](child_account())
    PlebNetConfig().increment_child_index()
    fake_generator.generate_child_account()

    wallet = TriblerWallet(plebnet_settings.get_instance().wallets_testnet_created())
    c = cloudomate_providers['vps'][provider]

    configurations = c.get_options()
    option = configurations[option]

    transaction_hash = provider_instance.purchase(wallet, option)

    if not transaction_hash:
        logger.warning("Failed to purchase server")
        return plebnet_settings.FAILURE
    # TODO: how to spot the difference?
    if False:
        logger.warning("Insufficient funds to purchase server")
        return plebnet_settings.UNKNOWN

    config.get('bought').append((provider, transaction_hash, config.get('child_index')))
    config.get('transactions').append(transaction_hash)
    config.set('chosen_provider', None)
    config.save()

    return plebnet_settings.SUCCESS


def place_offer(chosen_est_price, config):
    """
    Sell all available MB for the chosen estimated price on the Tribler market.
    :param config: config
    :param chosen_est_price: Target amount of BTC to receive
    :return: success of offer placement
    """
    available_mb = market_controller.get_balance('MB')
    if available_mb == 0:
        logger.log("No MB available")
        return False
    config.bump_offer_date()

    coin = 'TBTC' if plebnet_settings.get_instance().wallets_testnet() else 'BTC'

    config.set('last_offer', {coin: chosen_est_price, 'MB': available_mb})
    price_per_unit = max(0.0001, chosen_est_price / float(available_mb))
    return market_controller.put_ask(price=price_per_unit,
                                     price_type=coin,
                                     quantity=available_mb,
                                     quantity_type='MB',
                                     timeout=plebnet_settings.TIME_IN_HOUR)


def save_info_vpn():
    """
    Stores the child vpn information
    :param location: where to store the config
    :return:
    """
    vpn = get_vpn_providers()[plebnet_settings.get_instance().vpn_host()](child_account())
    info = vpn.get_configuration()
    child_index = PlebNetConfig().get('child_index')
    prefix = plebnet_settings.get_instance().vpn_child_prefix()


    dir = path.expanduser(plebnet_settings.get_instance().vpn_config_path())
    credentials = prefix + child_index +plebnet_settings.get_instance().vpn_credentials_name()
    # own_credentials is for when the file is renamed back to me_credentials
    own_credentials = plebnet_settings.get_instance().vpn_own_prefix() \
                      + plebnet_settings.get_instance().vpn_credentials_name()
    ovpn = prefix + child_index +plebnet_settings.get_instance().vpn_config_name()

    with io.open(path.join(dir, ovpn), 'w', encoding='utf-8') as ovpn_file:
        ovpn_file.write(info.ovpn + '\nauth-user-pass ' + own_credentials)

    with io.open(path.join(dir, credentials), 'w', encoding='utf-8') as credentials_file:
        credentials_file.writelines([info.username + '\n', info.password])

    print("Saved VPN configuration to " + dir)

    return True
