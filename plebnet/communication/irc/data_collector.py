"""

hier wordt alle data verzameld voor communication


"""

import requests

from requests.exceptions import ConnectionError

from plebnet.agent import config


def get_server(): return "this method is not implemented"


def get_expiration(): return config.PlebNetConfig()['expiration_date']




