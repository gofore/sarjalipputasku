from flask_restful import Resource, marshal, fields
from flask import Blueprint
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

try:
    import ldap
except: pass

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

        if app.config['DUMMY_AUTHENTICATION']:
            return self.token_with_email('test@example.org')

        if app.config.get('LDAP_URL'):
            con = ldap.initialize(app.config['LDAP_URL'])
            con.start_tls_s()
            try:
                con.simple_bind_s(form.email.data, form.password.data)
            except ldap.INVALID_CREDENTIALS:
                return {
                    'message': 'Unauthorized',
                    'status': 401
                }, 401

            return self.token_with_email(self.email.data)

        return {
            'message': 'Authentication disabled',
            'status': 401
        }, 401

    def token_with_email(self, email):
        s = Serializer(app.config['SECRET_KEY'], expires_in=3600)
        token = s.dumps({'user': email}).decode('utf-8')
        return marshal({
            'token': token,
            'user': email
        }, token_fields)
