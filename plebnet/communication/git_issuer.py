import requests
import sys
import traceback
import json

from plebnet.utilities import logger
from plebnet.settings import plebnet_settings


def send(title, trace_back=' ', labels=['bug']):
    settings = plebnet_settings.get_instance()
    if not settings.github_active(): return

    username = settings.github_username()
    password = settings.github_password()
    repo_owner = settings.github_owner()
    repo_name = settings.github_repo()

    full_link, gist_link = create_gist(username, password)

    body = \
        "An error occurred at a plebbot agent\n\r" \
        "\n\r" \
        "The plebnet nick is %s \r\n"\
        "More info can be added here later on\n\r" \
        "\n\r" \
        "\n\r" \
        "The trackback of the error:\n\r" \
        "\n\r" \
        "%s\n\r" \
        "\n\r" \
        "The log file can be found [here](%s)\n\r" \
        "\n\r" \
        "More details regarding this post can be found [here](%s)\n\r" \
        "\n\r" \
        "\n\r" \
        "Good luck fixing this!"

    body = body % (settings.irc_nick, trace_back, gist_link, full_link)

    create_issue(username, password, repo_owner, repo_name, title, body, labels)


def create_issue(username, password, repo_owner, repo_name, title, body, labels):
    try:
        # Our url to create issues via POST
        url = 'https://api.github.com/repos/%s/%s/issues' % (repo_owner, repo_name)
        # Create an authenticated session to create the issue
        session = requests.Session()
        session.auth = (username, password)
        # Create our issue
        issue = {'title': title, 'body': body, 'labels': labels}
        # Add the issue to our repository
        r = session.post(url, json.dumps(issue))
        if r.status_code == 201:
            logger.success('Successfully created Issue "%s"' % title)
        else:
            logger.warning('Could not create Issue "%s"' % title)
            logger.log(r.content, 'Response:')
    except:
        logger.error(sys.exc_info()[0], "git_issuer send")
        logger.error(traceback.format_exc())


def create_gist(username, password):
    try:
        # the log files
        filename = plebnet_settings.get_instance().logger_file()
        content = open(filename, 'r').read()
        # Our url to create issues via POST
        url = 'https://api.github.com/gists'
        # Create an authenticated session to create the issue
        session = requests.Session()
        session.auth = (username, password)
        # Create our issue
        gist = {
            "description": "the description for this gist",
            "public": True,
            "files": {
                "logfile.txt": {
                    "content": content
                }
            }
        }

        r = session.post(url, json.dumps(gist))
        if r.status_code == 201:
            logger.success('Successfully created gist')
        else:
            logger.warning('Could not create gist')
            logger.log(r.content, 'Response:')
        return r.json()['url'], r.json()['html_url']

    except:
        logger.error(sys.exc_info()[0], "git_issuer gist")
        logger.error(traceback.format_exc())
