import os
import subprocess


from plebnet.utilities import logger, system_vals
from plebnet.controllers import market_controller


def running():
    """
    Check if tribler is running.
    :return: True if twistd.pid exists in /root/tribler
    """

    path = os.path.join(system_vals.TRIBLER_HOME, system_vals.TRIBLER_PID)
    return os.path.isfile(path)

    # try:
    #
    #     pid = int(open(path).read())
    #     os.kill(pid, 0)
    #
    # except OSError:
    #     return False
    # except IOError:
    #     # no such file
    #     return False
    # else:
    #     return True

    # return os.path.isfile(os.path.join(system_vals.TRIBLER_HOME, 'twistd_tribler.pid'))
    # return os.path.isfile(os.path.join(system_vals.TRIBLER_HOME, 'twistd.pid'))




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
