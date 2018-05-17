import os
import subprocess


from plebnet.utilities import logger, system_vals
from plebnet.controllers import market_controller


def running():
    """
    Check if tribler is running.
    :return: True if twistd.pid exists in /root/tribler
    """

    # TODO: kijken of het proces draait ipv het bestand aanwezig is
    path = os.path.join(system_vals.TRIBLER_HOME, system_vals.TRIBLER_PID)
    return os.path.isfile(path)


def start():
    """
    Start tribler
    :return:
    """
    env = os.environ.copy()
    env['PYTHONPATH'] = system_vals.TRIBLER_HOME
    try:
        success = subprocess.call(['twistd', '--pidfile='+system_vals.TRIBLER_PID,
                                   'plebnet', '-p', '8085', '--exitnode'],
                                  cwd=system_vals.TRIBLER_HOME, env=env)
        if not success:
            logger.error('Failed to start Tribler', "tribler_controller")
            return False
        logger.success('Tribler is started', "tribler_controller")

        logger.log('market running: ' + str(market_controller.is_market_running()))
        return True
    except subprocess.CalledProcessError as e:
        logger.error(e.output, "Tribler starter", "tribler_controller")
        return False