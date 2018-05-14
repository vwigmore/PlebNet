import os
import subprocess


from plebnet.utilities import logger, system_vals
from plebnet.controllers import market_controller


def running():
    """
    Check if tribler is running.
    :return: True if twistd.pid exists in /root/tribler
    """
    return os.path.isfile(os.path.join(system_vals.TRIBLER_HOME, 'twistd.pid'))


def start():
    """
    Start tribler
    :return:
    """
    env = os.environ.copy()
    env['PYTHONPATH'] = system_vals.TRIBLER_HOME
    try:
        subprocess.call(['twistd', 'plebnet', '-p', '8085', '--exitnode'], cwd=system_vals.TRIBLER_HOME, env=env)
        logger.log('market: ' + str(market_controller.is_market_running()))
        return True
    except subprocess.CalledProcessError:
        return False
