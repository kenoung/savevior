import base64
import os
import urllib
import uuid

import requests

CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
STATE = 12412
CITI_URL = 'https://sandbox.apihub.citi.com/gcb/api'
REDIRECT_URI = "https://127.0.0.1:3000/login"

# url endpoints
ACCOUNT_SUMMARY = '/v1/accounts'
TRANSACTIONS = '/v1/accounts/{account_id}/transactions'

def _call(token, endpoint):
    url = CITI_URL + endpoint
    print(url)
    unique_id = 'c0d8c1a9-88cf-49d1-a495-c2da4ab10be0' # uuid.uuid4().bytes
    headers = {"Authorization": "Bearer {}".format(token),
               "uuid": str(unique_id),
               "Accept": "application/json",
               "client_id": CLIENT_ID}
    print(headers)
    r = requests.get(url, headers=headers)
    print(r.status_code)
    return r.json()


def get_login_url():
    data = {}
    data["response_type"] = "code"
    data["client_id"] = CLIENT_ID
    data["scope"] = "accounts_details_transactions customers_profiles bill_payments"
    data["countryCode"] = "SG"
    data["businessCode"] = "GCB"
    data["locale"] = "en_US"
    data["state"] = STATE
    data["redirect_uri"] = REDIRECT_URI
    return "https://sandbox.apihub.citi.com/gcb/api/authCode/oauth2/authorize?" + urllib.parse.urlencode(data)


def get_access_refresh_token(auth_code, state):
    endpoint = '/authCode/oauth2/token/sg/gcb'
    auth = get_auth()
    headers = {
        "Authorization": auth,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI
    }

    print(headers)
    print(data)
    resp = requests.post(CITI_URL + endpoint, headers=headers, data=data)
    resp_json = resp.json()
    access_token = resp_json['access_token']
    refresh_token = resp_json['refresh_token']
    return access_token, refresh_token


def get_auth():
    key = base64.b64encode(str.encode('{}:{}'.format(CLIENT_ID, CLIENT_SECRET)))
    return 'Basic ' + key.decode()


def get_accounts(token):
    result = _call(token, ACCOUNT_SUMMARY)
    if result.get('httpCode'):
        return
    return result


def get_transactions(account_id, token):
    endpoint = TRANSACTIONS.format(account_id=account_id)
    result = _call(token, endpoint)
    if result.get('httpCode'):
        return
    return result

