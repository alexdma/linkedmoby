'''
Created on 9 lug 2021

@author: alexdma@apache.org
'''
from functools import wraps

from flask import Blueprint, request
from mobygames import callMoby, extractor as extr
import requests
from requests.auth import HTTPBasicAuth
from rdflib import Graph

__all__ = ['blueprint']

blueprint = Blueprint('vghub', __name__)


def login_required(f):

    @wraps(f)
    def wrapped_view(**kwargs):
        au = request.authorization
        try:
            auth = check_auth(au.username, au.password)
        except AttributeError:
            auth = None
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


@blueprint.route('/game/<int:moby_id>')
@login_required
def game(moby_id, auth):
    response = requests.get('https://api.mobygames.com/v1/games/' + str(moby_id), auth=auth)
    g = Graph()
    extr.game(response.json(), g)
    return g.serialize(format='json-ld'), 200, {'Content-Type': 'application/json'}


def check_auth(user, passwd):
    return HTTPBasicAuth(user, '')
