'''
Created on 9 lug 2021

@author: alexdma@apache.org
'''
from flask import Blueprint
import vghub.relay


__all__ = ['blueprint']

blueprint = Blueprint('vghub', __name__)


from functools import wraps
from flask import request

def login_required(f):
    @wraps(f)
    def wrapped_view(**kwargs):
        auth = request.authorization
        if not (auth and check_auth(auth.username, auth.password)):
            return ('Unauthorized', 401, {
                'WWW-Authenticate': 'Basic realm="Login Required"'
            })

        return f(**kwargs)

    return wrapped_view

@blueprint.route('/ld')
@login_required
def ld():
    return f'Logged in as {request.authorization.username}.'

def check_auth(user, passwd):
    return user=='kingroland' and passwd=='12345'