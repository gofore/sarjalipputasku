import flask_restful
from flask import Flask

from views.routes import routes, RouteList
from views.upload import upload, UploadView
app = Flask(__name__, static_url_path='')
api = flask_restful.Api(app)
api_root = '/api/v1'
api.add_resource(RouteList, api_root + '/routes')
api.add_resource(UploadView, api_root + '/upload')

app.register_blueprint(routes)
app.register_blueprint(upload)
