from flask import g, Blueprint
from flask_restful import Resource, marshal_with
from views.routes import route_fields

from common import auth
from app import mongo

mytickets = Blueprint('mytickets', __name__)


class MyTicketsList(Resource):
    @auth.login_required
    @marshal_with(route_fields)
    def get(self):
        tickets = mongo.db.tickets.find({"updated_by": g.current_user, "reserved": {"$ne": None}})
        return {'tickets': [ticket for ticket in tickets]}
