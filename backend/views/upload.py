from flask_restful import reqparse, Resource
from flask import abort, Blueprint

import logging
import werkzeug

upload = Blueprint('upload', __name__)


class UploadView(Resource):
    def get(self):
        return "only POST here"

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files')

        args = parser.parse_args()
        if 'file' not in args:
            abort(422)

        try:
            print args['file']  # .read()
        except Exception as e:
            abort(422)
            logging.warn(e)
