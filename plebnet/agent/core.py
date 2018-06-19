"""
A package which handles the main behaviour of the PlebNet agent:
- Set all configuration files.
- Check if Tribler and the Tribler Marketplace are running.
- Create the necessary wallets.
- Check if a new child agent can be bought and do so if possible.
"""

import os
import random
import time

from plebnet.agent.dna import DNA
from plebnet.agent.config import PlebNetConfig
from plebnet.clone import server_installer
from plebnet.controllers import tribler_controller, cloudomate_controller, market_controller, wallet_controller
from plebnet.communication.irc import irc_handler
from plebnet.settings import plebnet_settings
from plebnet.utilities import logger, fake_generator


settings = plebnet_settings.get_instance()
log_name = "agent.core"  # Used for identifying the origin of the log message.
config = None  # Used to store the configuration and only load once.
dna = None  # Used to store the DNA of the agent and only load once.


def setup(args):
    """
    This method should only be called once and is responsible for the initial setup of the PlebNet
    agent. All necessary configuration files are created and IRC communication is started.
    :param args: If running in Testnet mode.
    """
    global dna, config
    logger.log("Setting up PlebNet")

    # Prepare the DNA configuration
    dna = DNA()
    dna.read_dictionary(cloudomate_controller.get_vps_providers())
    if args.test_net:
        settings.wallets_testnet("1")
        settings.settings.write()
        dna.read_dictionary({'proxhost': cloudomate_controller.get_vps_providers()['proxhost']})
    dna.write_dictionary()

    # Prepare first child configuration
    fake_generator.generate_child_account()

    # Set general info about the PlebNet agent
    settings.irc_nick(settings.irc_nick_def() + str(random.randint(1000, 10000)))
    config = PlebNetConfig()
    config.set('expiration_date', time.time() + 30 * plebnet_settings.TIME_IN_DAY)
    config.save()

    # Prepare the IRC Client
    irc_handler.init_irc_client()
    irc_handler.start_irc_client()

    logger.success("PlebNet is ready to roll!")


def check():
    """
    The method is the main function which should run periodically. It controls the behaviour of the agent,
    starting Tribler and buying servers.
    """
    global config, dna
    logger.log("Checking PlebNet", log_name)

    # Read general configuration
    if settings.wallets_testnet_created():
        os.environ['TESTNET'] = '1'
    config = PlebNetConfig()
    dna = DNA()
    dna.read_dictionary()

    # Requires time to setup, continue in the next iteration.
    if not check_tribler():
        return

    if not settings.wallets_initiate_once():
        create_wallet()
    select_provider()

    # These need a matchmaker, otherwise agent will be stuck waiting.
    if market_controller.has_matchmakers():
        update_offer()
        attempt_purchase()
    install_vps()


def create_wallet():
    """
    Checks if a Bitcoin (BTC) wallet or a Testnet Bitcoin (TBTC) wallet needs to be made.
    """
    if settings.wallets_testnet():
        # Attempt to create Testnet wallet
        logger.log("create Testnet wallet")
        x = wallet_controller.create_wallet('TBTC')
        if x:
            settings.wallets_testnet_created("1")
            settings.wallets_initiate_once("1")
            settings.settings.write()
            os.environ['TESTNET'] = '1'
    else:
        # Attempt to create Bitcoin wallet
        logger.log("create Bitcoin wallet")
        y = wallet_controller.create_wallet('BTC')
        if y:
            settings.wallets_initiate_once("1")
            settings.settings.write()

def check_tribler():
    """
    Check whether Tribler is running and configured properly, otherwise start Tribler.
    :return: True if tribler is running, False otherwise.
    :rtype: Boolean
    """
    if tribler_controller.running():
        logger.log("Tribler is already running", log_name)
        return True
    else:
        tribler_controller.start()
        return False


def update_offer():
    """
    Check if an hour as passed since the last offer made, if passed calculate a new offer.
    """
    if config.time_since_offer() > plebnet_settings.TIME_IN_HOUR:
        logger.log("Calculating new offer", log_name)
        cloudomate_controller.update_offer(config)
        config.save()


def attempt_purchase():
    """
    Check if enough money to buy a server, and if so, do so,
    """
    (provider, option, _) = config.get('chosen_provider')
    if settings.wallets_testnet():
        domain = 'TBTC'
    else:
        domain = 'BTC'
    if market_controller.get_balance(domain) >= cloudomate_controller.calculate_price(provider, option):
        logger.log("Try to buy a new server from %s" % provider, log_name)
        success = cloudomate_controller.purchase_choice(config)
        if success == plebnet_settings.SUCCESS:
            # Evolve yourself positively if you are successful
            dna.evolve(True)
        elif success == plebnet_settings.FAILURE:
            # Evolve provider negatively if not successful
            dna.evolve(False, provider)
            config.set('chosen_provider', None)
            config.save()


def install_vps():
    """
    Calls the server install for installing all purchased servers.
    """
    server_installer.install_available_servers(config, dna)


def select_provider():
    """
    Check whether a provider is already selected, otherwise select one based on the DNA.
    """
    if not config.get('chosen_provider'):
        logger.log("No provider chosen yet", log_name)
        all_providers = dna.vps
        excluded_providers = config.get('excluded_providers')
        available_providers = list(set(all_providers.keys()) - set(excluded_providers))
        providers = {k: all_providers[k] for k in all_providers if k in available_providers}

        if providers >= 1 and sum(providers.values()) > 0:
            providers = DNA.normalize_excluded(providers)
            choice = cloudomate_controller.pick_provider(providers)
            config.set('chosen_provider', choice)
        logger.log("Provider chosen: %s" % str(config.get('chosen_provider')), log_name)
        config.save()
