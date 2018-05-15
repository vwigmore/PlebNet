import os
import subprocess

from plebnet.agent.dna import DNA
from plebnet.agent.config import PlebNetConfig
from plebnet.clone import server_installer
from plebnet.controllers import tribler_controller, cloudomate_controller, market_controller
from plebnet.utilities import logger, system_vals

log_name = "agent.core"


def check():
    """
    Check whether conditions for buying new server are met and proceed if so
    :return:
    """
    logger.log("Checking PlebNet", log_name)
    config = PlebNetConfig()

    # TODO: DNA static singular maken --> dan kan dit weg
    dna = DNA()
    dna.read_dictionary()

    # these require time to setup, continue in the next iteration
    if not check_tribler():
        return
    if not check_tunnel_helper():
        return

    select_provider(config, dna)
    update_offer(config, dna)
    attempt_purchase(config, dna)
    install_vps(config, dna)


def check_tribler():
    if tribler_controller.running():
        logger.log("Tribler is already running", log_name)
        return True
    else:
        tribler_controller.start()
        return False


def check_tunnel_helper():
    # TEMP TO SEE EXITNODE PERFORMANCE, tunnel_helper should merge with market or other way around
    if not os.path.isfile(os.path.join(system_vals.TRIBLER_HOME, system_vals.TUNNEL_HELPER_PID)):
        logger.log("Starting tunnel_helper", log_name)
        env = os.environ.copy()
        env['PYTHONPATH'] = system_vals.TRIBLER_HOME
        try:
            subprocess.call(['twistd', '--pidfile='+system_vals.TUNNEL_HELPER_PID, 'tunnel_helper', '-x', '-M'],
                            cwd=system_vals.TRIBLER_HOME, env=env)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(e.output, log_name)
            return False
    return True
    # TEMP TO SEE EXITNODE PERFORMANCE


def select_provider(config, dna):
    if not config.get('chosen_provider'):
        logger.log("No provider chosen yet", log_name)
        update_choice(config, dna)
        logger.log("Provider chosen: %s" % config.get('chosen_provider'), log_name)
        config.save()
        return False
    return True


def update_offer(config, dna):
    # check if the stored prices should be updated.
    if config.time_since_offer() > system_vals.TIME_IN_HOUR:
        logger.log("Calculating new offer", log_name)
        cloudomate_controller.update_offer(config, dna)
        config.save()


def attempt_purchase(config, dna):
    # try to purchase the chosen vps.
    (provider, option, _) = config.get('chosen_provider')
    if market_controller.get_btc_balance() >= cloudomate_controller.calculate_price(provider, option):
        logger.log("Try to buy a new server from %s" % provider, log_name)
        success = cloudomate_controller.purchase_choice(config)
        if success == system_vals.SUCCESS:
            # evolve yourself positively if you are successful
            own_provider = DNA.get_own_provider(dna)
            DNA.evolve(own_provider, dna, True)
        elif success == system_vals.FAILURE:
            # evolve provider negatively if not successful
            DNA.evolve(provider, dna, False)


def install_vps(config, dna):
    server_installer.install_available_servers(config, dna)


#TODO: dit moet naar agent.DNA, maar die is nu al te groot
def update_choice(config, dna):
    all_providers = dna.vps

    logger.log("test_update choice: %s" % all_providers, "update_choice")

    excluded_providers = config.get('excluded_providers')
    available_providers = list(set(all_providers.keys()) - set(excluded_providers))
    providers = {k: all_providers[k] for k in all_providers if k in available_providers}

    logger.log("Providers: %s" % providers, "update_choice")
    logger.log("provider_values: %s" % providers.values(), "update_choice")

    if providers >= 1 and sum(providers.values()) > 0:
        providers = DNA.normalize_excluded(providers)
        choice = (provider, option, price) = cloudomate_controller.pick_provider(providers)
        config.set('chosen_provider', choice)
        logger.log("First provider: %s" % provider, "update_choice")

