from flask_restful import reqparse, Resource
from flask import abort, g, Blueprint

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
    def base64_encode_qrcode(self, qrcode):
        try:
            with open(qrcode, "rb") as image_file:
                return base64.b64encode(image_file.read())
        except:
            return ''

    def get_pages(self, fname):
        with file(fname, 'rb') as fd:
            return [self.get_html_soup(page) for page in PDFPage.get_pages(fd)]

    def get_html_soup(self, page):
        outfp = StringIO.StringIO()
        rsrcmgr = PDFResourceManager(caching=False)
        device = HTMLConverter(rsrcmgr, outfp)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        print(page)
        interpreter.process_page(page)
        html_doc = outfp.getvalue()
        soup = BeautifulSoup(html_doc, 'html.parser')
        device.close()
        outfp.close()
        return soup

    def get_order_id(self, soup):
        order_id = re.search("Tilausnumero:\W+(\d+)", soup.text)
        if not order_id:
            abort(422)
        return order_id.groups()[0]

    def get_ticket_id(self, soup):
        ticket_id = re.search("- (.+) -", soup.text)
        if not ticket_id:
            abort(422)
        return ticket_id.groups()[0]

    def get_route(self, soup):
        route = re.search("\d+ / \d+(.+) - (.*)Aikuinen", soup.text)
        if not route:
            abort(422)
        return route.groups()

    def get_price(self, soup):
        prices = re.search("10%(\d+,\d\d)\d+,\d\d(\d+,\d\d)", soup.text).groups()
        if not prices:
            abort(422)
        price_without_tax, price_with_tax = prices
        return float(price_without_tax.replace(",", "."))

    def get_ticket_type_and_expiration(self, soup):
        match = re.search("\d\d\.\d\d\.\d\d\d\d(.+)(\d\d\.\d\d\.\d\d\d\d)", soup.text).groups()
        if not match:
            abort(422)
        return match

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

        pages = self.get_pages(tmp_src_file)
        if not pages:
            abort(422)

        first_page = pages[0]
        ticket_count = mongo.db.tickets.find({"order_id": self.get_order_id(first_page)}).count()

        qr_codes = iter([])
        if ticket_count:
            raise InvalidUsage("Ticket already uploaded", status_code=400)
        try:
            os.popen('pdfimages -png ' + tmp_src_file + ' ' + tmp_dir + '/out')
            ims = os.popen("ls " + tmp_dir + "/out*").read().split()
            qr_codes = iter(ims[1:len(ims):2])
        except:
            print("XXX: No poppler installed, unable to produce 2D barcodes")

        tickets = []
        for page in pages:
            route = self.get_route(page)
            ticket_type, expires = self.get_ticket_type_and_expiration(page)
            hell_zone = timezone('Europe/Helsinki')
            end_of_day = datetime.timedelta(hours=23, minutes=59, seconds=59)
            qr_base64 = self.base64_encode_qrcode(qr_codes.next())
            tickets.append({
                'src': route[0],
                'dest': route[1],
                'price': self.get_price(page) / len(pages),
                'qr': 'data:image/png;base64,' + qr_base64,
                'order_id': self.get_order_id(page),
                'ticket_type': ticket_type,
                'ticket_id': self.get_ticket_id(page),
                'expiration_date': hell_zone.localize(datetime.datetime.strptime(expires, '%d.%m.%Y') + end_of_day),
                'uploaded': hell_zone.localize(datetime.datetime.now()),
                'uploaded_by': g.current_user,
                'reserved': None,
                'used': None
            })

        for ticket in tickets:
            mongo.db.tickets.insert(ticket)
