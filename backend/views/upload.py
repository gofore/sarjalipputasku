from flask_restful import reqparse, Resource
from flask import abort, Blueprint

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import HTMLConverter

import base64
import datetime
import werkzeug
import tempfile
import re
from pytz import timezone
from bs4 import BeautifulSoup
import StringIO
import os

from app import mongo
from common import InvalidUsage, auth
upload = Blueprint('upload', __name__)


class UploadView(Resource):
    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files')
        args = parser.parse_args()
        if 'file' not in args:
            abort(422)

        # Danger Zone, parsing PDF files is dirty and this one definately ain't
        # the prettiest creature alive. Cleanse yourself with strong liqueur
        # afterwards.

        tmp_dir = tempfile.mkdtemp()
        tmp_src_file = tmp_dir + '/in.pdf'
        with file(tmp_src_file, 'wb') as fd:
            fd.write(args['file'].read())
        qr_codes = []
        unique_ticket_order = None
        with file(tmp_src_file, 'rb') as fd:
            for page in PDFPage.get_pages(fd):
                outfp = StringIO.StringIO()
                rsrcmgr = PDFResourceManager(caching=False)
                device = HTMLConverter(rsrcmgr, outfp)
                interpreter = PDFPageInterpreter(rsrcmgr, device)
                interpreter.process_page(page)
                html_doc = outfp.getvalue()
                soup = BeautifulSoup(html_doc, 'html.parser')

                route = re.search("\d+ / \d+(.+) - (.*)Aikuinen", soup.text)
                if not route:
                    abort(422)
                route = route.groups()

                order_id = re.search("Tilausnumero:\W+(\d+)", soup.text)
                if not order_id:
                    abort(422)
                order_id = order_id.groups()[0]

                ticket_id = re.search("- (.+) -", soup.text)
                if not ticket_id:
                    abort(422)

                ticket_id = ticket_id.groups()[0]
                print("tmp_dir: " + tmp_dir)
                if not unique_ticket_order:
                    ticket_count = mongo.db.tickets.find({"order_id": order_id}).count()
                    if ticket_count:
                        raise InvalidUsage("Ticket already uploaded", status_code=400)
                    try:
                        os.popen('pdfimages -png ' + tmp_src_file + ' ' + tmp_dir + '/out')
                        ims = os.popen("ls " + tmp_dir + "/out*").read().split()
                        qr_codes = iter(ims[1:len(ims):2])
                    except:
                        print("XXX: No poppler installed, unable to produce 2D barcodes")
                    unique_ticket_order = True

                ticket_type, expires = re.search("\d\d\.\d\d\.\d\d\d\d(.+)(\d\d\.\d\d\.\d\d\d\d)", soup.text).groups()
                print(route, ticket_id, ticket_type, expires)
                hell_zone = timezone('Europe/Helsinki')
                end_of_day = datetime.timedelta(hours=23, minutes=59, seconds=59)

                qr_base64 = ''
                try:
                    with open(qr_codes.next(), "rb") as image_file:
                        qr_base64 = base64.b64encode(image_file.read())
                except:
                    pass
                mongo.db.tickets.insert({
                    'src': route[0],
                    'dest': route[1],
                    'qr': 'data:image/png;base64,' + qr_base64,
                    'order_id': order_id,
                    'ticket_type': ticket_type,
                    'ticket_id': ticket_id,
                    'expiration_date': hell_zone.localize(datetime.datetime.strptime(expires, '%d.%m.%Y') + end_of_day),
                    'reserved': None,
                    'used': None
                })
                device.close()
                outfp.close()
