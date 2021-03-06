from flask_restful import marshal_with, fields, Resource
from flask import Blueprint, abort, request, send_file, g
from datetime import datetime
from bson.code import Code
from bson.objectid import ObjectId
import pymongo
import arrow
from common import InvalidUsage, auth
from app import mongo
import base64
import io

ticket_fields = {
    'id': fields.String(attribute='_id'),
    'src': fields.String,
    'dest': fields.String,
    'expiration_date': fields.DateTime(dt_format='iso8601'),
    'price': fields.Float,
    'qr': fields.String,
    'pdf': fields.String,
    'order_id': fields.String,
    'ticket_type': fields.String,
    'reserved': fields.DateTime(dt_format='iso8601'),
    'used': fields.DateTime(dt_format='iso8601'),
    'vr_id': fields.String(attribute='ticket_id'),
}

route_fields = {
    'tickets': fields.List(fields.Nested(ticket_fields))
}

route_summary_fields = {
    'src': fields.String,
    'dest': fields.String,
    'ticket_type': fields.String,
    'count': fields.Integer
}

routes = Blueprint('routes', __name__)


class RouteSummaryList(Resource):
    @auth.login_required
    @marshal_with(route_summary_fields)
    def get(self):
        reducer = Code("""function(obj, prev){prev.count++;}""")
        return mongo.db.tickets.group(key={"src": 1, "dest": 1, "ticket_type": 1}, condition={"reserved": None}, initial={"count": 0},
                                      reduce=reducer)


class RouteList(Resource):
    @auth.login_required
    @marshal_with(route_fields)
    def get(self):
        src = request.args.get('src')
        dest = request.args.get('dest')
        ticket_type = request.args.get('type')
        if not src or not dest:
            return

        if ticket_type:
            ticket_type = ticket_type.upper()

        now = datetime.now()
        query = {
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
            ]}

        ticket_types = {'EKO': '2.lk', 'EKSTRA': '1.lk'}
        if ticket_type and ticket_type in list(ticket_types.keys()):
            query['ticket_type'] = {'$regex': ticket_types[ticket_type]}
        available_tickets = mongo.db.tickets.find_one(query, sort=[('expiration_date', pymongo.ASCENDING)])
        return {'tickets': available_tickets}


def update_ticket(id, data, current_user=None):
    reserved_arg = data.get('reserved')
    used_arg = data.get('used')
    if reserved_arg is None and used_arg is None:
        raise InvalidUsage("reserved or used parameter missing")

    ticket = mongo.db.tickets.find_one({
        "_id": ObjectId(id),
    })
    if not ticket:
        abort(409)

    if reserved_arg is not None:
        if reserved_arg and ticket.get('reserved') is not None:
            abort(409)
        if ticket.get('used') is not None:
            abort(409)
        reserved_state = arrow.utcnow().to('Europe/Helsinki').datetime if reserved_arg else None
    else:
        reserved_state = ticket.get('reserved')

    if used_arg is not None:
        if used_arg and ticket.get('used') is not None:
            abort(409)
        used_state = arrow.utcnow().to('Europe/Helsinki').datetime if used_arg else None
    else:
        used_state = ticket.get('used')

    update_fields = {
        "used": used_state,
        "reserved": reserved_state,
    }
    if current_user is None:
        current_user = g.current_user

    update_fields["updated_by"] = current_user

    result = mongo.db.tickets.update_one({
        "_id": ObjectId(id)
    }, {
        '$set': update_fields,
    })
    if result.matched_count < 1:
        abort(400)
    return 204


class RouteView(Resource):
    @auth.login_required
    def put(self, id):
        data = request.get_json(force=True)
        return update_ticket(id, data, g.current_user)


class RouteImageView(Resource):
    def get(self, id):
        ticket = mongo.db.tickets.find_one({
            "_id": ObjectId(id),
        })
        if not ticket:
            abort(404)
        img_bin = io.BytesIO()
        cbytes = ticket['qr'].split("data:image/png;base64,")[1]
        ebytes = base64.decodebytes(bytes(cbytes, 'utf-8'))
        img_bin.write(ebytes)
        img_bin.seek(0)
        return send_file(img_bin, attachment_filename="qr.png")
