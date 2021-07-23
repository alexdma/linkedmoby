'''
Created on 9 lug 2021

@author: alexdma@apache.org
'''
from functools import wraps

from flask import Blueprint, request
from mobygames import callMoby
import requests
from requests.auth import HTTPBasicAuth


__all__ = ['blueprint']

blueprint = Blueprint('vghub', __name__)


def login_required(f):

    @wraps(f)
    def wrapped_view(**kwargs):
        au = request.authorization
        auth = check_auth(au.username, au.password)
        if not (au and auth):
            return ('Unauthorized', 401, {
                'WWW-Authenticate': 'Basic realm="Login Required"'
            })

        return f(**kwargs, auth=auth)

    return wrapped_view


@blueprint.route('/ld')
@login_required
def ld(auth):
    response = requests.get('https://api.mobygames.com/v1/games', auth=auth)
    return response.json()


def check_auth(user, passwd):
    return HTTPBasicAuth(user, '')
