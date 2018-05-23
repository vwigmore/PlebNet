"""
This file is used to setup a new PlebNet agent on a remote server.

It used the available servers in the configuration and tries to install
the latest version of PlebNet on these servers.
"""

import os
import re
import subprocess

# TODO: remove these imports from cloudomate and get them from the controller.
from cloudomate.cmdline import providers
from cloudomate.util.settings import Settings as AccountSettings

from plebnet.controllers import cloudomate_controller
from plebnet.utilities import logger, globals


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
    logger.log("instal: %s" % bought, "install_available_servers")
    for provider, transaction_hash, child_index in bought:
        logger.log("Checking whether %s is activated" % provider)

        # try:
        ip = cloudomate_controller.get_ip(providers['vps'][provider])
        # except BaseException as e:
        #    print(e)
        #    print("%s not ready yet" % provider)
        #    return

        logger.log("Installling child on %s " % provider)
        logger.log('ip: %s' % ip)
        if is_valid_ip(ip):
            account_settings = cloudomate_controller.child_account(child_index)
            rootpw = account_settings.get('server', 'root_password')
            providers['vps'][provider].br = providers['vps'][provider]._create_browser()
            # cloudomatecontroller.setrootpw(cloudomate_providers['vps'][provider], rootpw)
            parentname = '{0}-{1}'.format(account_settings.get('user', 'firstname'), account_settings.get('user', 'lastname'))
            dna.create_child_dna(provider, parentname, transaction_hash)
            # Save config before entering possibly long lasting process
            config.save()
            success = _install_server(ip, rootpw)
            # send_child_creation_mail(ip, rootpw, success, config, user_options, transaction_hash)
            # # Reload config in case install takes a long time
            config.load()
            config.get('installed').append({provider: success})
            if [provider, transaction_hash, child_index] in bought:
                bought.remove([provider, transaction_hash])
            config.save()


def is_valid_ip(ip):
    """
    This methods checks if the provided ip-address is valid
    :param ip: The ipadress to check
    :type ip: String
    :return: True/False
    :rtype: Boolean
    """
    pieces = ip.split('.')
    if len(pieces) != 4:
        return False
    try:
        return all(0 <= int(p) < 256 for p in pieces)
    except ValueError:
        return False


def _install_server(ip, rootpw):
    """
    This function starts the actual installation routine.
    :param ip: The ip-address of the remote server
    :type ip: String
    :param rootpw: The root password of the remote server
    :type rootpw: String
    :return: The exit status of the installation
    :rtype: Integer
    """
    script_path = os.path.join(globals.PLEBNET_HOME, "/scripts/create-child.sh")
    logger.log('tot_path: %s' % script_path)
    command = '%s %s %s' % ("scripts/create-child.sh", ip.strip(), rootpw.strip())
    print("Running %s" % command)
    success = subprocess.call(command, shell=True, cwd=globals.PLEBNET_HOME)
    if success:
        logger.log("Installation successful")
    else:
        logger.log("Installation unsuccesful")
    return success
