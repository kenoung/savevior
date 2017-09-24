import os
from flask import Flask, render_template, session, jsonify
from functools import wraps
from flask import g, request, redirect, url_for

from citi_api import get_login_url, get_access_refresh_token, get_accounts, get_transactions, get_profile
from fitbit_api import get_fitbit_auth_url, exchange_for_credentials_fitbit, get_activity_time_series, \
    compute_casuality, get_fitbit_json
from forecasting import weekly, yearly, monthly
from sleep_api import exchange_for_credentials

app = Flask(__name__)

# Helper functions

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not logged_in():
            return jsonify({'error': 'you are not logged in'}), 401
        return f(*args, **kwargs)
    return decorated_function


def logged_in():
    return session.get('access_token') and session.get('refresh_token')

# Views


@app.route('/login', methods=['GET'])
def login():
    code = request.args.get('code')
    state = request.args.get('state')
    access_token, refresh_token = get_access_refresh_token(code, state)
    session['access_token'] = access_token
    session['refresh_token'] = refresh_token
    return redirect(url_for('main'))


@app.route('/sleep_auth', methods=['GET'])
def sleep_auth():
    if request.args.get('error'):
        return 'why you reject me?'
    code = request.args.get('code')
    credentials = exchange_for_credentials(code)
    session['credentials'] = credentials
    return redirect(url_for('main'))


@app.route('/', methods=['GET'])
def main():
    if not logged_in():
        login_url = get_login_url()
        return render_template('LandingPage.html', login_url=login_url)
    else:
        if not session.get('profile'):
            session['profile'] = get_profile(session['access_token'])

        # session['accounts'] = get_accounts(session.get('access_token'))
        first_name = 'James' # placeholder
        if session.get('profile'):
            first_name = session['profile']['customerParticulars']['names'][0]['firstName']

        fitbit_login = None
        if not session.get('fitbit'):
            fitbit_login = get_fitbit_auth_url()

        if not session.get('weather_casuality'):
            session['weather_casuality'] = 0.9

        return render_template('index.html', first_name=first_name, fitbit_login=fitbit_login)


@app.route('/api/week', methods=['GET'])
def week():
    return weekly()


@app.route('/api/month', methods=['GET'])
def month():
    return monthly()


@app.route('/api/year', methods=['GET'])
def year():
    return yearly()



@app.route('/api/accounts', methods=['GET'])
@login_required
def accounts():
    if not session.get('accounts'):
        session['accounts'] = get_accounts(session.get('access_token'))
    return jsonify(session['accounts'])


@app.route('/api/transactions/<string:account_id>')
@login_required
def transactions(account_id):
    if not session.get(account_id):
        session[account_id] = get_transactions(account_id, session['access_token'])
    return jsonify(session[account_id])


@app.route('/fitbit_auth')
@login_required
def fitbit_auth():
    code = request.args.get('code')
    access_token = exchange_for_credentials_fitbit(code)
    session['fitbit'] = access_token
    session['fitbit_casuality'] = compute_casuality()
    return redirect(url_for('main'))


@app.route('/api/fitbit_time_series')
@login_required
def fitbit_time_series():
    if not session.get('fitbit'):
        return 'not logged into fitbit', 401

    return jsonify(get_activity_time_series(session['fitbit']))


@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('main'))


@app.route('/api/fitbit_data')
def fitbit_data():
    return get_fitbit_json()


@app.route('/fitbit')
@login_required
def fitbit():
    return render_template('fitbit.html')

if __name__ == '__main__':
    app.secret_key = os.environ['INSIGHTS_SECRET']
    app.run(ssl_context=('/Users/datatron/.certificates/server.crt', '/Users/datatron/.certificates/server.key'), port=3000)
