"""
This file is used to control all dependencies with Tribler.

Other files should never have a direct import from Tribler, as the reduces the maintainability of this code.
If Tribler alters its call methods, this should be the only file which needs to be updated in PlebNet.
"""

import os
import subprocess
import requests

from requests.exceptions import ConnectionError

from plebnet.utilities import logger
from plebnet.settings import plebnet_settings
from plebnet.controllers import market_controller

setup = plebnet_settings.get_instance()

def running():
    """
    Check if tribler is running.
    :return: True if twistd.pid exists in /root/tribler
    """

    # TODO: kijken of het proces draait ipv het bestand aanwezig is
    path = os.path.join(setup.tribler_home(), setup.tribler_pid())
    return os.path.isfile(path)


def start():
    """
    Start tribler
    :return:
    """
    env = os.environ.copy()
    env['PYTHONPATH'] = setup.tribler_home()
    try:
        if setup.wallets_testnet():
            success = subprocess.call(['twistd', '--pidfile='+setup.tribler_pid(),'plebnet', '-p', '8085', '--testnet', '--exitnode'],
                                  cwd=setup.tribler_home(), env=env)
        else:
            success = subprocess.call(['twistd', '--pidfile='+setup.tribler_pid(),'plebnet', '-p', '8085', '--exitnode'],
                                  cwd=setup.tribler_home(), env=env)

        if not success:
            logger.error('Failed to start Tribler', "tribler_controller")
            return False
        logger.success('Tribler is started', "tribler_controller")

        logger.log('market running: ' + str(market_controller.is_market_running()))
        logger.log('testnet: ' + setup.wallets_testnet())
        return True
    except subprocess.CalledProcessError as e:
        logger.error(e.output, "tribler_controller")
        return False


def get_uploaded():
    try:
        # return requests.get('http://localhost:8085/statistics/dispersy').json()['dispersy_statistics']['total_uploaded']
        tu = requests.get('http://localhost:8085/trustchain/statistics').json()['statistics']['total_up']
        tu = int(tu)/1024.0/1024.0
        return tu
        # return requests.get('http://localhost:8085/trustchain/statistics').json()['statistics']['total_up']
    except ConnectionError:
        return "Unable to retrieve amount of uploaded data"


def get_helped_by():
    try:
        return requests.get('http://localhost:8085/trustchain/statistics').json()['statistics']['peers_that_helped_pk']
    except ConnectionError:
        return "Unable to retrieve amount of peers that helped this agent"


def get_helped():
    try:
        return requests.get('http://localhost:8085/trustchain/statistics').json()['statistics']['peers_that_pk_helped']
    except ConnectionError:
        return "Unable to retrieve amount of peers helped by this agent"


def get_downloaded():
    try:
        # return requests.get('http://localhost:8085/statistics/dispersy').json()['dispersy_statistics']['total_downloaded']
        td = requests.get('http://localhost:8085/trustchain/statistics').json()['statistics']['total_down']
        td = int(td)/1024.0/1024.0
        return td
        # return requests.get('http://localhost:8085/trustchain/statistics').json()['statistics']['total_down']
    except ConnectionError:
        return "Unable to retrieve amount of downloaded data"
