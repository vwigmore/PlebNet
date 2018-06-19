"""
This file is used to setup a new PlebNet agent on a remote server.

It used the available servers in the configuration and tries to install
the latest version of PlebNet on these servers.
"""

import os
import subprocess

from plebnet.controllers import cloudomate_controller
from plebnet.settings import plebnet_settings as setup
from plebnet.utilities import logger

def install_available_servers(config, dna):
    """
    This function checks if there are any servers ready to be installed and installs PlebNet on them.
    :param config: The configuration of this Plebbot
    :type config: dict
    :param dna: The DNA of this Plebbot
    :type dna: DNA
    :return: None
    :rtype: None
    """
    bought = config.get('bought')
    logger.log("install: %s" % bought, "install_available_servers")

    for provider, transaction_hash, child_index in list(bought):

        # skip vpn providers as they show up as 'bought' as well
        if provider in cloudomate_controller.get_vpn_providers():
            return

        vpn_child_index = None

        try:
            provider_class = cloudomate_controller.get_vps_providers()[provider]
            ip = cloudomate_controller.get_ip(provider_class, cloudomate_controller.child_account(child_index))
        except BaseException as e:
            logger.log(str(e) + "%s not ready yet" % str(provider), "install_available_servers")
            return

        # VPN configuration, enable tun/tap settings
        if provider_class.TUN_TAP_SETTINGS:
            vpn_child_index = child_index
            tun_succes = provider_class.enable_tun_tap()
            logger.log("Enabling %s tun/tap: %s"%(provider, tun_succes))
            if not cloudomate_controller.save_info_vpn(config):
                logger.log("VPN not ready yet, can't save ovpn config")
                return

        logger.log("Installing child on %s with ip %s" % (provider, str(ip)))
        if is_valid_ip(ip):
            account_settings = cloudomate_controller.child_account(child_index)
            parentname = '{0}-{1}'.format(account_settings.get('user', 'firstname'),
                                          account_settings.get('user', 'lastname'))
            dna.create_child_dna(provider, parentname, transaction_hash)

            # Save config before entering possibly long lasting process
            config.save()
            rootpw = account_settings.get('server', 'root_password', vpn_child_index, setup.get_instance().wallets_testnet())
            success = _install_server(ip, rootpw)

            # Reload config in case install takes a long time
            config.load()
            config.get('installed').append({provider: success})
            if [provider, transaction_hash, child_index] in config.get('bought'):
                config.get('bought').remove([provider, transaction_hash, child_index])
            config.save()


def is_valid_ip(ip):
    """
    This methods checks if the provided ip-address is valid
    :param ip: The ipadress to check
    :type ip: String
    :return: True/False
    :rtype: Boolean
    """
    if ip:
        pieces = ip.strip().split('.')
        if len(pieces) != 4:
            return False
        try:
            if 0 <= int(pieces[1]) < 256:
                return all(0 <= int(p) < 256 for p in pieces)
        except ValueError:
            return False
    return False


def _install_server(ip, rootpw, vpn_child_index=None, testnet=False):
    """
    This function starts the actual installation routine.
    :param ip: The ip-address of the remote server
    :type ip: String
    :param rootpw: The root password of the remote server
    :type rootpw: String
    :return: The exit status of the installation
    :rtype: Integer
    """
    settings = setup.get_instance()
    home = settings.plebnet_home()
    script_path = os.path.join(home, "plebnet/clone/create-child.sh")
    logger.log('tot_path: %s' % script_path)

    command = '%s -i %s -p %s' % ("scripts/create-child.sh", ip.strip(), rootpw.strip())

    # additional VPN arguments
    if vpn_child_index:
        prefix = setup.get_instance().vpn_child_prefix()

        dir = os.path.expanduser(setup.get_instance().vpn_config_path())
        credentials = os.path.join(dir, prefix + vpn_child_index + setup.get_instance().vpn_credentials_name())
        ovpn = os.path.join(dir, prefix + vpn_child_index + setup.get_instance().vpn_config_name())
        command += '-conf %s -cred %s' % (ovpn, credentials)

    if testnet:
        command += '-t'

    logger.log("Running %s" % command, '_install_server')
    exitcode = subprocess.call(command, shell=True, cwd=home)
    if exitcode == 0:
        logger.log("Installation successful")
        return True
    else:
        logger.log("Installation unsuccessful, error code: %s" % exitcode)
        return False
