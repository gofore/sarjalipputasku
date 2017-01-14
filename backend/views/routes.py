from flask_restful import marshal_with, fields, Resource
from flask import Blueprint, request, abort, Response
from datetime import datetime
from bson.objectid import ObjectId
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

class RouteView(Resource):
    def get(self, id):
        return "Only PUT here!"

    def put(self, id):
        data = request.get_json(force=True)
        reserved_arg = data.get('reserved')
        used_arg = data.get('used')
        if reserved_arg is None and used_arg is None:
            abort(400)
        ticket = mongo.db.tickets.find_one({
            "_id": ObjectId(id),
        })
        if not ticket:
            abort(204)

        if reserved_arg is not None:
            if reserved_arg and ticket.get('reserved') is not None:
                abort(409)
            if ticket.get('used') is not None:
                abort(409)
            reserved_state = datetime.now() if reserved_arg else None
        else:
            reserved_state = ticket.get('reserved')

        if used_arg is not None:
            if used_arg and ticket.get('used') is not None:
                abort(409)
            used_state = datetime.now() if used_arg else None
        else:
            used_state = ticket.get('used')

        result = mongo.db.tickets.update_one(
            {"_id": ObjectId(id)},
            {
                '$set': {
                    "used": used_state,
                    "reserved": reserved_state,
                },
            })
        print result.matched_count
        if result.matched_count < 1:
            abort(400)
        return (204)
