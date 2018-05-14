import os
import re
import subprocess

from cloudomate.cmdline import providers
from cloudomate.util.settings import Settings as AccountSettings

from plebnet.controllers import cloudomate_controller
from plebnet.utilities import logger, system_vals


def install_available_servers(config, dna):
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
    return re.match('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip)


def _install_server(ip, rootpw):
    script_path = os.path.join(system_vals.PLEBNET_HOME, "/scripts/create-child.sh")
    logger.log('tot_path: %s' % script_path)
    command = '%s %s %s' % ("scripts/create-child.sh", ip.strip(), rootpw.strip())
    print("Running %s" % command)
    success = subprocess.call(command, shell=True, cwd=system_vals.PLEBNET_HOME)
    if success:
        logger.log("Installation successful")
    else:
        logger.log("Installation unsuccesful")
    return success
