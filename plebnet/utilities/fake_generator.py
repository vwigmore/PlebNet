# -*- coding: utf-8 -*-

"""
This file is used to create random (but valid) agent configuration files,
which used for acquiring new VPS.

The only method to call is the generate_child_account(), which returns a random configured account
"""

# Total imports
import ConfigParser
import codecs
import random
import unicodedata

# Partial imports
from appdirs import user_config_dir
from faker.factory import Factory
from cloudomate.util.settings import os  # TODO: Waarom niet de normale os?
from cloudomate.util.settings import Settings as userOptions  # TODO: cloudomate import --> cloudomate_controller

# Local imports
from plebnet.utilities import logger
from plebnet.agent.config import PlebNetConfig

# File parameters


def generate_child_account():
    filename = _child_file()
    if os.path.exists(filename):
        logger.error(("child_config already present at %s" % filename), "generate_child_account()")
        config = userOptions()
        config.read_settings(filename=filename)
        return config
    locale = random.choice(['cs_CZ', 'de_DE', 'dk_DK', 'es_ES', 'et_EE', 'hr_HR', 'it_IT'])
    fake = Factory().create(locale)
    cp = ConfigParser.ConfigParser()
    _generate_address(cp, fake)
    _generate_server(cp, fake)
    _generate_user(cp, fake)
    _remove_unicode(cp)
    with codecs.open(filename, 'w', 'utf8') as config_file:
        cp.write(config_file)
    return cp


def _child_file():
    # TODO deze naar plebnet verplaatsen
    return os.path.join(user_config_dir(), 'child_config' + str(PlebNetConfig().get('child_index')) + '.cfg')


def _remove_unicode(cp):
    for section in cp.sections():
        for option in cp.options(section):
            item = cp.get(section, option)
            if isinstance(item, unicode):
                cp.set(section, option, unicodedata.normalize('NFKD', item).encode('ascii', 'ignore'))


def _generate_user(cp, fake):
    cp.add_section('user')
    firstname = fake.first_name()
    lastname = fake.last_name()
    full_name = firstname + '_' + lastname
    full_name = full_name.replace(' ', '_')
    cp.set('user', 'email', 'authentic8989+' + full_name + '@gmail.com')
    cp.set('user', 'firstname', firstname)
    cp.set('user', 'lastname', lastname)
    cp.set('user', 'companyname', fake.company())
    cp.set('user', 'phonenumber', fake.numerify('##########'))
    cp.set('user', 'password', fake.password(length=10, special_chars=False))


def _generate_address(cp, fake):
    cp.add_section('address')
    cp.set('address', 'address', fake.street_address())
    cp.set('address', 'city', fake.city())
    cp.set('address', 'state', fake.state())
    cp.set('address', 'countrycode', fake.country_code())
    cp.set('address', 'zipcode', fake.postcode())


def _generate_server(cp, fake):
    cp.add_section('server')
    cp.set('server', 'root_password', fake.password(length=10, special_chars=False))
    cp.set('server', 'ns1', 'ns1')
    cp.set('server', 'ns2', 'ns2')
    cp.set('server', 'hostname', fake.word())
