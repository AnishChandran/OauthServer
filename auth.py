import os
from urllib.parse import urlencode

import requests
from bottle import route, redirect, request, response, template, run


@route('/auth/zoho')
def asana_auth():
    params = {
        'response_type': 'code',
        'redirect_uri': 'https://my-example-app.herokuapp.com/auth/handle_decision',
        'client_id': '1000.GGXNNVQJA8OC0759779T38C4AT3OGD',
        'scope' : 'ZohoSupport.tickets.READ',
        'state': request.query.state
    }
    url = 'https://accounts.zoho.com/oauth/v2/auth?' + urlencode(params)
    redirect(url)


@route('/auth/handle_decision')
def handle_decision():
    if 'error' in request.query_string:
        return request.query.error_description
    # get access token
    params = {
        'grant_type': 'authorization_code',
        'code': request.query.code,
        'client_id': '1000.GGXNNVQJA8OC0759779T38C4AT3OGD',
        'client_secret': 'd2966b8ed2e65ba05c3ce76220a63ef1cc74d21d61',
        'redirect_uri': 'https://my-example-app.herokuapp.com/auth/handle_decision'
    }
    url = 'https://accounts.zoho.com/oauth/v2/token'
    r = requests.post(url, data=params)
    if r.status_code != 200:
        error_msg = 'Failed to get access token with error {}'.format(r.status_code)
        return error_msg
    else:
        data = r.json()
        response.set_cookie('sheet', data['access_token'], max_age=data['expires_in'])
        response.set_cookie('clean_sheet', data['refresh_token'])
        redirect('https://vickycomp.zendesk.com/agent/tickets/{}'.format(request.query.state))


@route('/auth/user_token')
def get_cookies():
    access_token = request.get_cookie('sheet')
    refresh_token = request.get_cookie('clean_sheet')
    if access_token:
        token = access_token
    elif refresh_token:
        params = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': '1000.GGXNNVQJA8OC0759779T38C4AT3OGD',
            'client_secret': 'd2966b8ed2e65ba05c3ce76220a63ef1cc74d21d61',
            'redirect_uri': 'https://my-example-app.herokuapp.com/auth/handle_decision'
        }
        url = 'https://accounts.zoho.com/oauth/v2/token'
        r = requests.post(url, data=params)
        if r.status_code != 200:
            error_msg = 'Failed to get access token with error {}'.format(r.status_code)
            return error_msg
        else:
            data = r.json()
            response.set_cookie('sheet', data['access_token'], max_age=data['expires_in'])
            token = data['access_token']
    else:
        token = 'undefined'
    return template('auth', token=token)

run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))