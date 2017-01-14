import flask_restful

from app import app
from views.routes import routes, RouteList, RouteView
from views.upload import upload, UploadView

api = flask_restful.Api(app)
api_root = '/api/v1'
api.add_resource(RouteList, api_root + '/routes')
api.add_resource(RouteView, api_root + '/routes/<string:id>')
api.add_resource(UploadView, api_root + '/upload')

app.register_blueprint(routes)
app.register_blueprint(upload)
