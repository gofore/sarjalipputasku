from flask_restful import marshal_with, fields, Resource
from flask import Blueprint, abort, request, g
from sqlalchemy import or_
import arrow

from models import db, Ticket
from common import InvalidUsage, auth

ticket = {
    'id': fields.String,
    'src': fields.String,
    'dest': fields.String,
    'expiration_date': fields.DateTime(dt_format='iso8601'),
    'price': fields.Float,
    'qr': fields.String,
    'order_id': fields.String,
    'reserved': fields.DateTime(dt_format='iso8601'),
    'used': fields.DateTime(dt_format='iso8601'),
    'vr_id': fields.String(attribute='ticket_id'),
}

route_fields = {
    'tickets': fields.List(fields.Nested(ticket))
}

routes = Blueprint('routes', __name__)


class RouteList(Resource):
    @auth.login_required
    @marshal_with(route_fields)
    def get(self):
        a = request.args.get('src').upper()
        b = request.args.get('dest').upper()
        if not a or not b:
            return
        if a == b:
            return
        tickets = Ticket.query .filter(or_(Ticket.src == a, Ticket.src ==
                                           b)).filter(or_(Ticket.dest == a,
                                                          Ticket.dest ==
                                                          b)).filter(Ticket.used.is_(None)).filter(Ticket.reserved.is_(None)).first()
        return {'tickets': tickets}


class RouteView(Resource):
    @auth.login_required
    def put(self, id):
        data = request.get_json(force=True)
        reserved_arg = data.get('reserved')
        used_arg = data.get('used')
        if reserved_arg is None and used_arg is None:
            raise InvalidUsage("reserved or used parameter missing")

        ticket = Ticket.query.filter_by(id=id).first_or_404()
        if not ticket:
            abort(404)

        if reserved_arg is not None:
            if reserved_arg and ticket.reserved is not None:
                abort(409)
            if ticket.used is not None:
                abort(409)
            reserved_state = arrow.utcnow().to('Europe/Helsinki').datetime if reserved_arg else None
        else:
            reserved_state = ticket.reserved

        if used_arg is not None:
            if used_arg and ticket.used is not None:
                abort(409)
            used_state = arrow.utcnow().to('Europe/Helsinki').datetime if used_arg else None
        else:
            used_state = ticket.used

        ticket.updated_by = g.current_user
        ticket.used = used_state
        ticket.reserved = reserved_state
        db.session.commit()

        return (204)
