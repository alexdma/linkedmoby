'''
Created on 9 lug 2021

@author: alexdma@apache.org
'''
from flask import Flask

from vghub.blueprint import blueprint as vghub

app = Flask(__name__)

# Register entity resolution app as root, but this might change
app.register_blueprint(vghub)


def register_extensions(app):
    """Register Flask extensions."""
    # CORS(app)
    return None


register_extensions(app)
app.run(host='0.0.0.0', debug=True)
