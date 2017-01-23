from flask import g, Blueprint
from flask_restful import Resource, marshal_with
from routes import route_fields

from common import auth
from models import Ticket

mytickets = Blueprint('mytickets', __name__)


class MyTicketsList(Resource):
    @auth.login_required
    @marshal_with(route_fields)
    def get(self):
        tickets = Ticket.query.filter_by(updated_by=g.current_user).filter(Ticket.reserved.isnot(None))
        return {'tickets': tickets}
