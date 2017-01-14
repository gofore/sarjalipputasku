from flask_restful import reqparse, Resource
from flask import request, abort, Blueprint
from flask_pymongo import PyMongo

from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice, TagExtractor
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.image import ImageWriter

import datetime
import werkzeug
import re
from pytz import timezone
from bs4 import BeautifulSoup
import StringIO

from app import mongo

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

        # Danger Zone, parsing PDF files is dirty and this one definately ain't
        # the prettiest creature alive. Cleanse yourself with strong liqueur
        # afterwards.
        unique_ticket_order = None
        for page in PDFPage.get_pages(args['file']):
            outfp = StringIO.StringIO()
            rsrcmgr = PDFResourceManager(caching=False)
            device = HTMLConverter(rsrcmgr, outfp, imagewriter=ImageWriter('out'))
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            interpreter.process_page(page)
            html_doc = outfp.getvalue()
            soup = BeautifulSoup(html_doc, 'html.parser')
            spans = soup.find_all('span')

            route = re.search("\d+ / \d+(.+) - (.*)Aikuinen", spans[7].text)
            if not route:
                abort(422)
            route = route.groups()

            order_id = re.search("Tilausnumero:\W+(\d+)", spans[27].text)
            if not order_id:
                abort(422)
            order_id = order_id.groups()[0]

            ticket_id = re.search("- (.+) -", spans[15].text)
            if not ticket_id:
                abort(422)

            ticket_id = ticket_id.groups()[0]
            if not unique_ticket_order:
                ticket_count = mongo.db.tickets.find({"order_id": order_id}).count()
                if ticket_count:
                    abort(422)
                unique_ticket_order = True

            ticket_type, expires = re.search("\d\d\.\d\d\.\d\d\d\d(.+)(\d\d\.\d\d\.\d\d\d\d)", spans[16].text).groups()
            print(route, ticket_id, ticket_type, expires)
            hell_zone = timezone('Europe/Helsinki')
            end_of_day = datetime.timedelta(hours=23, minutes=59, seconds=59)
            mongo.db.tickets.insert({
                'src': route[0],
                'dest': route[1],
                'qr': None,
                'order_id': order_id,
                'ticket_type': ticket_type,
                'ticket_id': ticket_id,
                'expiration_date': hell_zone.localize(datetime.datetime.strptime(expires, '%d.%m.%Y') + end_of_day),
                'reserved': None,
                'used': None
            })
            device.close()
            outfp.close()
