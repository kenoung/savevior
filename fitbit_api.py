import os
import urllib

import pandas as pd
import requests
from statsmodels.tsa.stattools import grangercausalitytests

AUTHORIZE_ENDPOINT = "https://www.fitbit.com"

CLIENT_ID = os.environ['FITBIT_ID']
CLIENT_SECRET = os.environ['FITBIT_SECRET']
REDIRECT_URI = 'https://127.0.0.1:3000/fitbit_auth'

# generated placeholder data
placeholder_insights = pd.read_csv('insights.csv', header=None, names=['ds', 'y'])
placeholder_activity = pd.read_csv('/Users/datatron/Downloads/fitbit.csv', header=0, names=['ds', 'activity_time'])


def get_fitbit_json():
    placeholder_activity.columns = ['date', 'value']
    placeholder_activity['date'] = pd.to_datetime(placeholder_activity['date'])
    return placeholder_activity.to_json(orient='records', date_format='iso', double_precision=2)


def compute_casuality(data=placeholder_insights, data2=placeholder_activity):
    merged = pd.merge(data,data2, on=['ds','ds'])
    m = merged[['y','activity_time']].as_matrix()
    result = grangercausalitytests(m, maxlag=5)
    return result[2][0]['lrtest'][1]


def get_fitbit_auth_url():
    data = {}
    data["scope"] = "activity weight"
    data["response_type"] = "code"
    data["client_id"] = CLIENT_ID
    data["expires_in"] = 604800

    return "{}/oauth2/authorize?".format(AUTHORIZE_ENDPOINT) +  urllib.parse.urlencode(data)


def exchange_for_credentials_fitbit(code):
    headers = {
        "Authorization": 'Basic MjI4TVJZOmRhNWJlM2M1NGM5YWQ0MDY4ZjBmMmUwZDNkN2NlYTQy',
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "clientId": CLIENT_ID
    }

    resp = requests.post('https://api.fitbit.com/oauth2/token', headers=headers, data=data)
    return resp.json()['access_token']


def get_activity_time_series(code):
    endpoint = 'https://api.fitbit.com/1/user/-/{resource_path}/date/{date}/{period}.json'
    resp = requests.get(
        endpoint.format(
            resource_path='activities/minutesFairlyActive',
            date='today',
            period='1y'
        ), headers={'Authorization': 'Bearer {}'.format(code)})
    return resp.json()["activities-minutesFairlyActive"]

