from flask_restful import marshal_with, fields, Resource
from flask import Blueprint, request, abort, Response
from datetime import datetime
import pymongo

from common import InvalidUsage
from app import mongo


ticket = {
    'id': fields.String(attribute='_id'),
    'src': fields.String,
    'dest': fields.String,
    'expiration_date': fields.DateTime(dt_format='iso8601'),
}

route_fields = {
    'tickets': fields.List(fields.Nested(ticket))
}

routes = Blueprint('routes', __name__)


class RouteList(Resource):
    @marshal_with(route_fields)
    def get(self):
        src = request.args.get('src')
        dest = request.args.get('dest')
        if not src or not dest:
            raise InvalidUsage("src or dest parameter missing")

        now = datetime.now()
        available_tickets = mongo.db.tickets.find_one({
            '$or': [
            {
                'src': src.upper(),
                'dest': dest.upper(),
                'reserved': None,
                'used': None,
                'expiration_date': {'$gt': now}
            },
            {
                'src': dest.upper(),
                'dest': src.upper(),
                'reserved': None,
                'used': None,
                'expiration_date': {'$gt': now}
            }
        ]}, sort=
            [('expiration_date', pymongo.ASCENDING)]
        )
        return {'tickets': available_tickets}
