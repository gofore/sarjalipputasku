from flask import g
from flask_httpauth import HTTPTokenAuth
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app import app
import logging

auth = HTTPTokenAuth('Bearer')
auth.authenticate_header = lambda: "Authentication Required"


@auth.verify_token
def verify_token(token):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        token = s.loads(token)
        g.current_user = token['user']
    except Exception, e:
        logging.error(e)
        return False
    return True


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv
