import flask_restful

from app import app
from views.routes import routes, RouteList, RouteView, RouteImageView
from views.upload import upload, UploadView
from views.sessions import sessions, SessionView
from views.mytickets import mytickets, MyTicketsList

api = flask_restful.Api(app)
api_root = '/api/v1'
api.add_resource(RouteList, api_root + '/routes')
api.add_resource(RouteView, api_root + '/routes/<string:id>')
api.add_resource(RouteImageView, api_root + '/qr/<string:id>.png')
api.add_resource(UploadView, api_root + '/upload')
api.add_resource(SessionView, api_root + '/login')
api.add_resource(MyTicketsList, api_root + '/mytickets')

app.register_blueprint(routes)
app.register_blueprint(upload)
app.register_blueprint(sessions)
app.register_blueprint(mytickets)


@app.route('/')
def index():
    return app.send_static_file('index.html')
