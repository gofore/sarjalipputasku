from flask_restful import marshal_with, fields, Resource
from flask import Blueprint, request

from app import mongo


ticket = {
    'src': fields.String,
    'dest': fields.String,
    'expiration_date': fields.DateTime,
}

route_fields = {
    'tickets': fields.List(fields.Nested(ticket))
}

routes = Blueprint('routes', __name__)


class RouteList(Resource):
    @marshal_with(route_fields)
    def get(self):
        available_tickets = mongo.db.tickets.find_one({
            'src': request.args.get('src'),
            'dest': request.args.get('dest'),
            'reserved': None,
            'used': None
        })
        return {'tickets': available_tickets}
