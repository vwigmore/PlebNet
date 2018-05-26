import json
import requests

from plebnet.utilities import logger

# Authentication for user filing issue (must have read/write access to
# repository to add issue to)
USERNAME = 'plebbot'
PASSWORD = '1qazxsw2'

# The repository to add this issue to
REPO_OWNER = 'thijmensjf'
REPO_NAME = 'PlebNet'


def make_github_issue(title, body=None, labels=None):
    '''Create an issue on github.com using the given parameters.'''
    # Our url to create issues via POST
    url = 'https://api.github.com/repos/%s/%s/issues' % (REPO_OWNER, REPO_NAME)
    # Create an authenticated session to create the issue
    session = requests.Session()
    session.auth = (USERNAME, PASSWORD)
    # Create our issue
    issue = {'title': title,
             'body': body,
             'labels': labels}
    # Add the issue to our repository
    r = session.post(url, json.dumps(issue))
    if r.status_code == 201:
        logger.log('Successfully created Issue "%s"' % title)
    else:
        logger.warning('Could not create Issue "%s"' % title)
        logger.log('Response:', r.content)
