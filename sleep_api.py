import os
from oauth2client.client import OAuth2WebServerFlow

from settings import SLEEP_AUTH

flow = OAuth2WebServerFlow(client_id=os.environ['CLIENT_ID'],
                           client_secret=os.environ['CLIENT_SECRET'],
                           scope='https://www.googleapis.com/auth/userinfo.email',
                           redirect_uri=SLEEP_AUTH)

def get_sleep_login_url():
    return flow.step1_get_authorize_url()

def exchange_for_credentials(code):
    return flow.step2_exchange(code)





