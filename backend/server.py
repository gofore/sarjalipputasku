import flask_restful
from app import app
from views.routes import routes, RouteList, RouteView, RouteImageView, RouteSummaryList
from views.upload import upload, UploadView
from views.sessions import sessions, SessionView
from views.mytickets import mytickets, MyTicketsList
from views.slack import slack_blueprint, SlackAuthorizedView, SlackIntegrationView

api = flask_restful.Api(app)
api_root = '/api/v1'
api.add_resource(RouteList, api_root + '/routes')
api.add_resource(RouteView, api_root + '/routes/<string:id>')
api.add_resource(RouteImageView, api_root + '/qr/<string:id>.png')
api.add_resource(RouteSummaryList, api_root + '/routesummary')
api.add_resource(UploadView, api_root + '/upload')
api.add_resource(SessionView, api_root + '/login')
api.add_resource(MyTicketsList, api_root + '/mytickets')
api.add_resource(SlackAuthorizedView, api_root + '/slack/activate')
api.add_resource(SlackIntegrationView, api_root + '/slack/action')

app.register_blueprint(routes)
app.register_blueprint(upload)
app.register_blueprint(sessions)
app.register_blueprint(mytickets)
app.register_blueprint(slack_blueprint, url_prefix=api_root)


@app.route('/')
def index():
    return app.send_static_file('index.html')
