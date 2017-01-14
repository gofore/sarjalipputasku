from flask_restful import marshal_with, fields, Resource
from flask import Blueprint
route_fields = {
    'src': fields.String,
    'dest': fields.String,
    'tickets': fields.List(fields.String)
}

routes = Blueprint('routes', __name__)


class RouteList(Resource):
    @marshal_with(route_fields)
    def get(self):
        return [{'src': 'a', 'dest': 'b', 'tickets': ['a1', 'a2']}]
