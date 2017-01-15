from flask_restful import Resource, marshal, fields
from flask import Blueprint
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import ldap

from forms import LoginForm
from app import app

sessions = Blueprint('sessions', __name__)

token_fields = {
    'token': fields.String,
    'user': fields.String,
}


class SessionView(Resource):
    def post(self):
        form = LoginForm()
        if not form.validate_on_submit():
            return form.errors, 422

        con = ldap.initialize('ldap://gofdir3.intra.gofore.com')
        con.start_tls_s()
        try:
            con.simple_bind_s(form.email.data, form.password.data)
        except ldap.INVALID_CREDENTIALS:
            return {
                'message': 'Unauthorized',
                'status': 401
            }, 401
        s = Serializer(app.config['SECRET_KEY'], expires_in=3600)
        token = s.dumps({'user': form.email.data}).decode('utf-8')
        return marshal({
            'token': token,
            'user': form.email.data
        }, token_fields)
