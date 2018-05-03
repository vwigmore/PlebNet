import json
import os
import re
import smtplib
import subprocess
import sys
import time
import threading
from argparse import ArgumentParser
from subprocess import CalledProcessError

import cloudomate
import electrum
from cloudomate.cmdline import providers as cloudomate_providers
from cloudomate.util.settings import Settings as UserOptions
from cloudomate.wallet import Wallet
from electrum import Wallet as ElectrumWallet
from electrum import WalletStorage
from electrum import keystore
from electrum.mnemonic import Mnemonic

# new toegevoegd
from plebnet.communication import ircbot

from plebnet import cloudomatecontroller, twitter
from plebnet.agent import marketapi
from plebnet.agent.dna import DNA
from plebnet.cloudomatecontroller import options
from plebnet.config import PlebNetConfig

WALLET_FILE = os.path.expanduser("~/.electrum/wallets/default_wallet")
TRIBLER_HOME = os.path.expanduser("~/PlebNet/tribler")
PLEBNET_CONFIG = os.path.expanduser("~/.plebnet.cfg")
TIME_IN_HOUR = 60.0 * 60.0
TIME_IN_DAY = TIME_IN_HOUR * 24.0

MAX_DAYS = 5


def execute(cmd=sys.argv[1:]):
    parser = ArgumentParser(description="Plebnet")

    subparsers = parser.add_subparsers(dest="command")
    add_parser_check(subparsers)
    add_parser_setup(subparsers)
    add_parser_testing(subparsers)

    args = parser.parse_args(cmd)
    args.func(args)


def add_parser_check(subparsers):
    parser_list = subparsers.add_parser("check", help="Check plebnet")
    parser_list.set_defaults(func=check)


def add_parser_setup(subparsers):
    parser_list = subparsers.add_parser("setup", help="Setup plebnet")
    parser_list.set_defaults(func=setup)

# temp test function
def add_parser_testing(subparsers):
    parser_list = subparsers.add_parser("test", help="Test new function")
    parser_list.set_defaults(func=test)
def test(args):
    print("Testing IRC")



def setup(args):
    print("Setting up PlebNet")
    cloudomatecontroller.generate_config()
    config = PlebNetConfig()
    config.set('expiration_date', time.time() + 30 * TIME_IN_DAY)
    config.save()

    dna = DNA()
    dna.read_dictionary()
    dna.write_dictionary()
    create_wallet()

    t = threading.Thread(target=ircbot.create())
    t.start()

def create_wallet():
    """
    Create an electrum wallet if it does not exist
    :return: 
    """
    if not os.path.isfile(WALLET_FILE):
        print("Creating wallet")
        config = electrum.SimpleConfig()
        storage = WalletStorage(config.get_wallet_path())
        passphrase = config.get('passphrase', '')
        seed = Mnemonic('en').make_seed()
        k = keystore.from_seed(seed, passphrase)
        k.update_password(None, None)
        storage.put('keystore', k.dump())
        storage.put('wallet_type', 'standard')
        storage.put('use_encryption', False)
        storage.write()
        wallet = ElectrumWallet(storage)
        wallet.synchronize()
        print("Your wallet generation seed is:\n\"%s\"" % seed)
        print("Please keep it in a safe place; if you lose it, you will not be able to restore your wallet.")
        wallet.storage.write()
        print("Wallet saved in '%s'" % wallet.storage.path)
    else:
        print("Wallet already present")


def check(args):
    """
    Check whether conditions for buying new server are met and proceed if so
    :param args: 
    :return: 
    """
    print("Checking")
    config = PlebNetConfig()

    dna = DNA()
    dna.read_dictionary()

    if not tribler_running():
        print("Tribler not running")
        success = start_tribler()
        print(success)
        # Now give tribler time to startup
        return success
    # TEMP TO SEE EXITNODE PERFORMANCE, tunnel_helper should merge with market or other way around
    if not os.path.isfile(os.path.join(TRIBLER_HOME, 'twistd2.pid')):
        env = os.environ.copy()
        env['PYTHONPATH'] = TRIBLER_HOME
        try:
            subprocess.call(['twistd', '--pidfile=twistd2.pid', 'tunnel_helper', '-x', '-M'], cwd=TRIBLER_HOME, env=env)
            return True
        except CalledProcessError:
            return False
    # TEMP TO SEE EXITNODE PERFORMANCE

    print("test: %s" % config.get('chosen_provider'))
    if not config.get('chosen_provider'):
        print("test: %s" % config.get('chosen_provider'))
        print ("Choosing new provider")
        update_choice(config, dna)
        config.save()

    if config.time_since_offer() > TIME_IN_HOUR:
        print("Calculating new offer")
        update_offer(config, dna)
        config.save()

    if config.get('chosen_provider'):
        print("market")
        (provider, option, _) = config.get('chosen_provider')
        print('balance: %s' % marketapi.get_btc_balance() )
        if marketapi.get_btc_balance() >= calculate_price(provider, option):
            print("Purchase server")
            transaction_hash, provider = purchase_choice(config)
            if transaction_hash:
                config.get('transactions').append(transaction_hash)
                # evolve yourself positively if you are successfull
                own_provider = get_own_provider(dna)
                evolve(own_provider, dna, True)
            else:
                # evolve provider negatively if not succesfull
                evolve(provider, dna, False)
        config.save()
        return
    print("instal?")
    install_available_servers(config, dna)
    config.save()


def tribler_running():
    """
    Check if tribler is running.
    :return: True if twistd.pid exists in /root/tribler
    """
    return os.path.isfile(os.path.join(TRIBLER_HOME, 'twistd.pid'))


def start_tribler():
    """
    Start tribler
    :return: 
    """
    env = os.environ.copy()
    env['PYTHONPATH'] = TRIBLER_HOME
    try:
        subprocess.call(['twistd', 'plebnet', '-p', '8085', '--exitnode'], cwd=TRIBLER_HOME, env=env)
        print('market: ' + str(marketapi.is_market_running()))

        return True
    except CalledProcessError:
        return False


def update_offer(config, dna):
    if not config.get('chosen_provider'):
        return
    (provider, option, _) = config.get('chosen_provider')
    btc_price = calculate_price(provider, option) * 1.15
    place_offer(btc_price, config)


def calculate_price(provider, option):
    print('provider: %s option: %s' % (provider, option))
    # vpsoptions = options(cloudomate_providers['vps'][provider])
    vpsoption = options(cloudomate_providers['vps'][provider])[option]
    print('chosen_option: %s' % str(vpsoption))
    gateway = cloudomate_providers['vps'][provider].get_gateway()
    btc_price = gateway.estimate_price(
        cloudomate.wallet.get_price(vpsoption.price, 'USD')) + cloudomate.wallet.get_network_fee()
    return btc_price


def place_offer(chosen_est_price, config):
    """
    Sell all available MC for the chosen estimated price on the Tribler market.
    :param config: config
    :param chosen_est_price: Target amount of BTC to receive
    :return: success of offer placement
    """
    available_mc = marketapi.get_mc_balance()
    if available_mc == 0:
        print("No MC available")
        return False
    config.bump_offer_date()
    config.set('last_offer', {'BTC': chosen_est_price, 'MC': available_mc})
    price_per_unit = chosen_est_price / float(available_mc)
    return marketapi.put_ask(price=price_per_unit, price_type='BTC', quantity=available_mc, quantity_type='MC',
                             timeout=TIME_IN_HOUR)


def update_choice(config, dna):
    all_providers = dna.vps
    print ("test_update choice: %s" % all_providers)
    excluded_providers = config.get('excluded_providers')
    available_providers = list(set(all_providers.keys()) - set(excluded_providers))
    providers = {k: all_providers[k] for k in all_providers if k in available_providers}
    print("Providers: %s" % providers)
    print('provider_values: %s' % providers.values())
    if providers >= 1 and sum(providers.values()) > 0:
        providers = DNA.normalize_excluded(providers)
        choice = (provider, option, price) = pick_provider(providers)
        config.set('chosen_provider', choice)
        print("First provider: %s" % provider)


def pick_provider(providers):
    provider = DNA.choose_provider(providers)
    print("pick: %s" % provider)
    gateway = cloudomate_providers['vps'][provider].get_gateway()
    option, price, currency = pick_option(provider)
    btc_price = gateway.estimate_price(
        cloudomate.wallet.get_price(price, currency)) + cloudomate.wallet.get_network_fee()
    return provider, option, btc_price


def pick_option(provider):
    """
    Pick most favorable option at a provider. For now pick cheapest option
    :param provider: 
    :return: (option, price, currency)
    """
    vpsoptions = options(cloudomate_providers['vps'][provider])
    cheapestoption = 0
    for item in range(len(vpsoptions)):
        if vpsoptions[item].price < vpsoptions[cheapestoption].price:
            cheapestoption = item

    print("test_vpsoptions: %s" % str(vpsoptions[cheapestoption]))

    return cheapestoption, vpsoptions[cheapestoption].price, 'USD'  # vpsoptions[cheapestoption].currency


def purchase_choice(config):
    """
    Purchase the cheapest provider in chosen_providers. If buying is successful this provider is moved to bought. In any
    case the provider is removed from choices.
    :param config: config
    :return: success
    """

    (provider, option, _) = config.get('chosen_provider')
    # cloudomate.cmdline._purchase_vps(provider, option, )
    user_options = UserOptions()
    user_options.read_settings()


    provider_instance = cloudomate_providers['vps'][provider](user_options)
    wallet = Wallet()
    c = cloudomate_providers['vps'][provider]

    configurations = c.get_options()
    option = configurations[option]
    print('option: ' + str(option))
    transaction_hash = provider_instance.purchase(wallet, option)

    # transaction_hash = cloudomatecontroller.purchase(cloudomate_providers['vps'][provider], option, wallet=Wallet())
    if transaction_hash:
        config.get('bought').append((provider, transaction_hash))
        config.set('chosen_provider', None)
    else:
        print("Insufficient funds")
        return None, provider
    if provider not in config.get('excluded_providers'):
        config.get('excluded_providers').append(provider)
    return transaction_hash, provider


def get_own_provider(dna):
    return dna.dictionary['Self']


def evolve(provider, dna, success):
    if success:
        dna.positive_evolve(provider)
    else:
        dna.negative_evolve(provider)


def install_available_servers(config, dna):
    bought = config.get('bought')

    for provider, transaction_hash in bought:
        print("Checking whether %s is activated" % provider)

        try:
            ip = cloudomatecontroller.get_ip(cloudomate_providers[provider])
        except BaseException as e:
            print(e)
            print("%s not ready yet" % provider)
            return

        print("Installling child on %s " % provider)
        if is_valid_ip(ip):
            user_options = UserOptions()
            user_options.read_settings()
            rootpw = user_options.get('rootpw')
            cloudomate_providers[provider].br = cloudomate_providers[provider]._create_browser()
            cloudomatecontroller.setrootpw(cloudomate_providers[provider], rootpw)
            parentname = '{0}-{1}'.format(user_options.get('firstname'), user_options.get('lastname'))
            dna.create_child_dna(provider, parentname, transaction_hash)
            # Save config before entering possibly long lasting process
            config.save()
            success = install_server(ip, rootpw)
            send_child_creation_mail(ip, rootpw, success, config, user_options, transaction_hash)
            # Reload config in case install takes a long time
            config.load()
            config.get('installed').append({provider: success})
            if [provider, transaction_hash] in bought:
                bought.remove([provider, transaction_hash])
            config.save()


def test_mail():
    user_options = UserOptions()
    user_options.read_settings()
    send_mail("Hello world.", user_options.get('user', 'firstname') + ' ' + user_options.get('user', 'lastname'))


def send_child_creation_mail(ip, rootpw, success, config, user_options, transaction_hash):
    mail_message = 'IP: %s\n' % ip
    mail_message += 'Root password: %s\n' % rootpw
    mail_message += 'Success: %s\n' % success
    mail_message += 'Transaction_hash: %s\n' % transaction_hash
    mail_dna = DNA()
    mail_dna.read_dictionary()
    mail_message += '\nDNA\n%s\n' % json.dumps(mail_dna.dictionary)
    mail_message += '\nConfig\n%s\n' % json.dumps(config.config)
    send_mail(mail_message, user_options.get('firstname') + ' ' + user_options.get('lastname'))


def is_valid_ip(ip):
    return re.match('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip)


def install_server(ip, rootpw):
    file_path = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.join(file_path, '/root/PlebNet/scripts/create-child.sh')
    command = '%s %s %s' % (script_path, ip.strip(), rootpw.strip())
    print("Running %s" % command)
    success = subprocess.call(command, shell=True)
    if success:
        print("Installation successful")
    else:
        print("Installation unsuccesful")
    return success


def send_mail(mail_message, name):
    sender = 'authentic8989+' + name + '@gmail.com'
    receivers = ['authentic8989+' + name + '@gmail.com']
    mail = """From:""" + name + """<""" + sender + """>
To: """ + name + """ <authentic8989+""" + name + """@gmail.com'>
Subject: New child spawned

"""
    mail += mail_message

    try:
        print("Sending mail: %s" + mail)
        smtp = smtplib.SMTP('gmail-smtp-in.l.google.com:25')
	smtp.helo()
	smtp.set_debuglevel(1)
        #smtp.starttls()
        smtp.sendmail(sender, receivers, mail)
        print "Successfully sent email"
    except smtplib.SMTPException as e:
        print "Error: unable to send email \n\n%s"% repr(e)


if __name__ == '__main__':
    execute()
