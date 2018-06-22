"""
A package which handles the main behaviour of the plebbot:
- check if everything is up and running
- check if the configuration is all set properly
- check if a new child can be spawned and do so if possible
"""

import os
import random
import subprocess
import time
import re

from plebnet.agent.dna import DNA
from plebnet.agent.config import PlebNetConfig
from plebnet.clone import server_installer
from plebnet.controllers import tribler_controller, cloudomate_controller, market_controller, wallet_controller
from plebnet.communication.irc import irc_handler
from plebnet.settings import plebnet_settings
from plebnet.utilities import logger, fake_generator


settings = plebnet_settings.get_instance()
log_name = "agent.core"  # used for identifying the origin of the log message
config = None  # Used to store the configuration and only load once
dna = None  # Used to store the DNA of the agent and only load once


def setup(args):
    logger.log("Setting up PlebNet")

    # handle the DNA
    dna = DNA()

    # Prepare Cloudomate
    if args.test_net:
        settings.wallets_testnet("1")
        settings.settings.write()
        dna.read_dictionary({'proxhost': cloudomate_controller.get_vps_providers()['proxhost']})
    else:
        dna.read_dictionary(cloudomate_controller.get_vps_providers())
        dna.remove_provider('proxhost')

    dna.write_dictionary()
    fake_generator.generate_child_account()

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
    The main function to run every interval
    :return: None
    :rtype: None
    """
    global config, dna

    if settings.wallets_testnet_created():
        os.environ['TESTNET'] = '1'    

    logger.log("Checking PlebNet", log_name)
    config = PlebNetConfig()

    # TODO: DNA static singular maken --> dan kan dit weg
    dna = DNA()
    dna.read_dictionary()

    # check if own vpn is installed before continuing
    if not vpn_is_running():
        if not check_vpn_install():
            logger.error("!!! VPN is not installed, child may get banned !!!", "Plebnet Check")

    # these require time to setup, continue in the next iteration
    if not check_tribler():
        return
    if not check_tunnel_helper():
        return

    # Prepare Cloudomate
    if not settings.wallets_initiate_once():
        create_wallet()

    select_provider()

    if market_controller.has_matchmakers():
        update_offer()
        attempt_purchase()
    install_vps()


def create_wallet():
    if settings.wallets_testnet():
        # attempt to create testnet wallet
        logger.log("create Testnet wallet", "setup")
        x = wallet_controller.create_wallet('TBTC')
        if x:
            settings.wallets_testnet_created("1")
            settings.wallets_initiate_once("1")
            settings.settings.write()
            os.environ['TESTNET'] = '1'
    else:
        # attempt to create bitcoin wallet
        y = wallet_controller.create_wallet('BTC')
        if y:
            settings.wallets_initiate_once("1")
            settings.settings.write()


def check_tribler():
    """
    Check whether Tribler is running and configured properly
    :return: True if tribler is running, False otherwise
    :rtype: Boolean
    """
    if tribler_controller.running():
        logger.log("Tribler is already running", log_name)
        return True
    else:
        tribler_controller.start()
        return False


def check_tunnel_helper():
    """
    Temporary function to track the data stream processed by Tribler
    :return: None
    :rtype: None
    """
    # TEMP TO SEE EXITNODE PERFORMANCE, tunnel_helper should merge with market or other way around
    if not os.path.isfile(os.path.join(settings.tribler_home(), settings.tunnelhelper_pid())):
        logger.log("Starting tunnel_helper", log_name)
        env = os.environ.copy()
        env['PYTHONPATH'] = settings.tribler_home()
        try:
            subprocess.call(['twistd', '--pidfile='+settings.tunnelhelper_pid(), 'tunnel_helper', '-x', '-m', '0'], #, '-M'],
                            cwd=settings.tribler_home(), env=env)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(e.output, log_name)
            return False
    return True
    # TEMP TO SEE EXITNODE PERFORMANCE


def check_vpn_install():
    """
    Checks the vpn configuration files (.ovpn, credentials.conf).
    If configuration files exist, no need to purchase VPN configurations.
    :return: True if installing succeeds, False if installing fails or configs are not found
    """
    # chech whether vpn is installed
    if settings.vpn_installed():
        logger.log("VPN is already installed")

    # check OWN configuration files.
    # the vpn configuration given has the "child" prefix (see plebnet_setup.cfg)
    # the prefix needs to be renamed to "own" prefix so that the agent can continue to buy for its children
    credentials = os.path.join(os.path.expanduser(settings.vpn_config_path()),
                               settings.vpn_own_prefix()+settings.vpn_credentials_name())
    vpnconfig = os.path.join(os.path.expanduser(settings.vpn_config_path()),
                             settings.vpn_own_prefix()+settings.vpn_config_name())

    for f in os.listdir(os.path.expanduser(settings.vpn_config_path())):
        if re.match(settings.vpn_child_prefix()+'[0-9]'+settings.vpn_config_name(), f):
            # matches child_0_config.openvpn 
            logger.log("VPN config found, renaming")
            os.rename(f, vpnconfig)
        elif re.match(settings.vpn_child_prefix()+'[0-9]'+settings.vpn_credentials_name(), f):
            # matches child_0_credentials.conf
            logger.log("VPN credentials found, renaming")
            os.rename(f, credentials)

    if os.path.isfile(credentials) and os.path.isfile(vpnconfig):
        # try to install
        if install_vpn():
            settings.vpn_installed("1")
            logger.log("Installing VPN succesful with configurations.")
            return True
        else:
            settings.vpn_installed("0")
            logger.log("Installing VPN failed with configurations!")
            return False
    else:
        logger.log("No VPN configurations found!")
        return False


def attempt_purchase_vpn():
    """
    Attempts to purchase a VPN, checks first if balance is sufficient
    The success message is stored to prevent further unecessary purchases.
    """
    provider = cloudomate_controller.get_vpn_providers()[settings.vpn_host()]
    if settings.wallets_testnet():
        domain = 'TBTC'
    else:
        domain = 'BTC'
    if market_controller.get_balance(domain) >= cloudomate_controller.calculate_price_vpn(provider):
        logger.log("Try to buy a new VPN from %s" % provider, log_name)
        success = cloudomate_controller.purchase_choice_vpn(config)
        if success == plebnet_settings.SUCCESS:
            logger.info("Purchasing VPN succesful!", log_name)
        elif success == plebnet_settings.FAILURE:
            logger.error("Error purchasing vpn", log_name)


def update_offer():
    """
    check if the stored prices for the selected provider should be updated.
    This does not have to happen every iteration as they do not change that often
    :return: None
    :rtype: None
    """
    if config.time_since_offer() > plebnet_settings.TIME_IN_HOUR:
        logger.log("Calculating new offer", log_name)
        cloudomate_controller.update_offer(config)
        config.save()


def attempt_purchase():
    """
    Check if rich enough to buy a server, and if so, do so
    :return: None
    :rtype: None
    """
    # try to purchase the chosen vps.
    (provider, option, _) = config.get('chosen_provider')
    if settings.wallets_testnet():
        domain = 'TBTC'
    else:
        domain = 'BTC'
    if market_controller.get_balance(domain) >= cloudomate_controller.calculate_price(provider, option):
        logger.log("Try to buy a new server from %s" % provider, log_name)
        success = cloudomate_controller.purchase_choice(config)
        if success == plebnet_settings.SUCCESS:
            # evolve yourself positively if you are successful
            dna.evolve(True)

            # purchase VPN with same config if server allows for it
            if cloudomate_controller.get_vps_providers()[provider].TUN_TAP_SETTINGS:
                attempt_purchase_vpn()
        elif success == plebnet_settings.FAILURE:
            # evolve provider negatively if not successful
            dna.evolve(False)


def install_vps():
    """
    Tries to install all purchased servers, can be skipped if the server is not configured yet.
    :return: None
    :rtype: None
    """
    server_installer.install_available_servers(config, dna)


def install_vpn():
    """
    Attempts to install the vpn using the credentials.conf and .ovpn configuration files
    :return: True if installing succeeded, otherwise it will raise an exception.
    """

    logger.log("Installing VPN")

    try_install = subprocess.Popen(['openvpn', '--config', settings.vpn_own_prefix()+settings.vpn_config_name(), '--daemon'],
                                  cwd=os.path.expanduser(settings.vpn_config_path()),
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
    result, error = try_install.communicate()
    exitcode = try_install.wait()

    if exitcode != 0:
        if error.decode('ascii') == "":
            error = result
        logger.log("ERROR installing VPN, Code: " + str(exitcode) + " - Message: " + error.decode('ascii'))
        return False
    else:
        pid = try_install.pid
        settings.vpn_pid(pid)
        settings.vpn_running("1")
        return True


def vpn_is_running():
    """
    :return: True if vpn is running, else false
    """
    pid = settings.vpn_pid()
    check = subprocess.call(['ps', '-p', str(pid)])
    if check == 0:
        settings.vpn_running("1")
        return True
    else:
        settings.vpn_running("0")
        settings.vpn_pid(0)
        return False


# TODO: dit moet naar agent.DNA, maar die is nu al te groot
def select_provider():
    """
    Check whether a provider is already selected, otherwise select one based on the dna
    :return: None
    :rtype: None
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
