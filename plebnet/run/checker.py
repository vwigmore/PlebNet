import os
import subprocess

from plebnet.agent.dna import DNA
from plebnet.agent.config import PlebNetConfig
from plebnet.clone import server_installer
from plebnet.controllers import tribler_controller, cloudomate_controller, market_controller
from plebnet.utilities import logger, system_vals


def check():
    """
    Check whether conditions for buying new server are met and proceed if so
    :return:
    """
    print("Checking")
    config = PlebNetConfig()

    dna = DNA()
    dna.read_dictionary()

    if not tribler_controller.running():
        logger.log("Tribler not running")
        success = tribler_controller.start()
        print(success)
        # Now give tribler time to startup
        return success
    # TEMP TO SEE EXITNODE PERFORMANCE, tunnel_helper should merge with market or other way around
    if not os.path.isfile(os.path.join(system_vals.TRIBLER_HOME, 'twistd2.pid')):
        env = os.environ.copy()
        env['PYTHONPATH'] = system_vals.TRIBLER_HOME
        try:
            subprocess.call(['twistd', '--pidfile=twistd2.pid', 'tunnel_helper', '-x', '-M'],
                            cwd=system_vals.TRIBLER_HOME, env=env)
            return True
        except subprocess.CalledProcessError:
            return False
    # TEMP TO SEE EXITNODE PERFORMANCE

    logger.log("test: %s" % config.get('chosen_provider'))
    if not config.get('chosen_provider'):
        logger.log("test: %s" % config.get('chosen_provider'))
        logger.log("Choosing new provider")
        update_choice(config, dna)
        config.save()

    if config.time_since_offer() > system_vals.TIME_IN_HOUR:
        logger.log("Calculating new offer")
        cloudomate_controller.update_offer(config)
        config.save()

    if config.get('chosen_provider'):
        logger.log("market")
        (provider, option, _) = config.get('chosen_provider')
        logger.log('balance: %s' % market_controller.get_btc_balance() )
        if market_controller.get_btc_balance() >= cloudomate_controller.calculate_price(provider, option):
            logger.log("Purchase server")
            transaction_hash, provider = cloudomate_controller.purchase_choice(config)
            if transaction_hash:
                config.get('transactions').append(transaction_hash)
                # evolve yourself positively if you are successful
                own_provider = DNA.get_own_provider(dna)
                DNA.evolve(own_provider, dna, True)
            else:
                # evolve provider negatively if not successful
                DNA.evolve(provider, dna, False)
        config.save()
        # return
    logger.log("install?", "check")
    server_installer.install_available_servers(config, dna)
    config.save()


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

