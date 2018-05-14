import os
import subprocess

from plebnet.utilities import logger

#TODO alle bestandspaden in 1 file, vanuit daar vervolgens inladen --> improved maintainability
PLEBNET_HOME = os.path.expanduser("~/PlebNet")
DEAMON = "plebnet/communication/irc/initIRC.sh"
CLIENT = "plebnet/communication/irc/ircbot.py"
PATH_TO_DEAMON = os.path.join(PLEBNET_HOME, DEAMON)
PATH_TO_CLIENT = os.path.join(PLEBNET_HOME, CLIENT)

# TODO: implement send_heartbeat
# TODO: implement send_msg(args)


def init_irc_client(args=None):

    logger.log("the IRC client is initializing", "init_irc_client")

    subprocess.call('sudo chmod +x %s' % PATH_TO_CLIENT, shell=True)
    subprocess.call('sudo chmod +x %s' % PATH_TO_DEAMON, shell=True)

    logger.log("the IRC client is initialized", "init_irc_client")


def start_irc_client(args=None):
    logger.log("the IRC client is starting", "start_irc_client")

    # run the init file
    success = subprocess.call('sudo %s start' % PATH_TO_DEAMON, shell=True)
    if success:
        logger.log("the IRC client is started", "start_irc_client")
    else:
        logger.error("the IRC client failed to start", "start_irc_client")
    return success


def stop_irc_client(args=None):
    logger.log("the IRC client is stopping", "stop_irc_client")

    # run the init file
    success = subprocess.call('sudo %s stop' % PATH_TO_DEAMON, shell=True)
    if success:
        logger.log("the IRC client is stopped", "stop_irc_client")
    else:
        logger.error("the IRC client is not stopped", "stop_irc_client")
    return success


def restart_irc_client(args=None):
    stop_irc_client()
    success = start_irc_client()
    return success


def status_irc_client(args=None):
    subprocess.call('sudo %s status' % PATH_TO_DEAMON, shell=True)
