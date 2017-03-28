from flask_restful import reqparse, Resource
from flask import abort, g, Blueprint

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import HTMLConverter

import base64
import werkzeug
import tempfile
import struct
import uuid
import re
import arrow
from bs4 import BeautifulSoup
import StringIO
import os

from app import mongo
from common import auth
upload = Blueprint('upload', __name__)


class UploadView(Resource):
    def base64_encode(self, qrcode):
        try:
            with open(qrcode, "rb") as image_file:
                return base64.b64encode(image_file.read())
        except:
            return ''

    def get_pages(self, fname):
        try:
            with open(fname, 'rb') as fd:
                return [self.get_html_soup(page) for page in PDFPage.get_pages(fd)]
        except:
            return None

    def get_html_soup(self, page):
        outfp = StringIO.StringIO()
        rsrcmgr = PDFResourceManager(caching=False)
        device = HTMLConverter(rsrcmgr, outfp)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
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
        return ticket_id.groups()[0].strip()

    def get_route(self, soup):
        route = re.search("\d+ / \d+(.+) - (.*)Aikuinen", soup.text)
        if not route:
            abort(422)
        return sorted(route.groups())

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
        def is_square(fn):
            with open(fn, 'rb') as fd:
                head = fd.read(24)
                width, height = struct.unpack('>ii', head[16:24])
                if int(width) == int(height):
                    return True

        parser = reqparse.RequestParser()
        parser.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files')
        args = parser.parse_args()
        if 'file' not in args:
            abort(422)

        tmp_dir = tempfile.mkdtemp()
        tmp_src_file = tmp_dir + '/in.pdf'
        with open(tmp_src_file, 'wb') as fd:
            fd.write(args['file'].read())

        qr_codes = []
        pdf_files = []

        try:
            # Danger Zone, parsing PDF files is dirty and this one definately ain't
            # the prettiest creature alive. Cleanse yourself with strong liqueur
            # afterwards.
            os.popen('pdfimages -png ' + tmp_src_file + ' ' + tmp_dir + '/out')
            ims = os.popen("ls " + tmp_dir + "/out*.png").read().split()
            qr_codes = [fn for fn in ims if is_square(fn)]
            os.popen("pdfseparate " + tmp_src_file + ' ' + tmp_dir + "/pdfout-%d.pdf")
            pdfs = os.popen("ls " + tmp_dir + "/pdfout-*.pdf").read().split()
            pdf_files = [fn for fn in pdfs]
        except:
            print("XXX: No poppler installed, unable to produce 2D barcodes")

        if len(qr_codes) != len(pdf_files) != len(pages):
            return {"message": "Invalid ticket file"}, 400

        tickets = []
        for qr_code, pdf_file in iter(zip(qr_codes, pdf_files)):
            pages = self.get_pages(pdf_file)
            if not pages:
                return {"message": "Could not parse the uploaded file, is this actually the PDF file with tickets?"}, 422
            page = pages[0]
            ticket_count = mongo.db.tickets.find({"order_id": self.get_order_id(page)}).count()
            if ticket_count:
                return {"message": "Ticket already uploaded"}, 400
            route = self.get_route(page)
            ticket_type, expires = self.get_ticket_type_and_expiration(page)
            qr_base64 = self.base64_encode(qr_code)
            pdf_base64 = self.base64_encode(pdf_file)
            tickets.append({
                'ticket_id': uuid.uuid4().hex,
                'src': route[0].upper(),
                'dest': route[1].upper(),
                'qr': 'data:image/png;base64,' + qr_base64,
                'pdf': 'data:application/pdf;base64,' + pdf_base64,
                'order_id': self.get_order_id(page),
                'price': self.get_price(page) / len(pages),
                'ticket_type': ticket_type,
                'ticket_id': self.get_ticket_id(page),
                'expiration_date': arrow.get(expires, 'DD.MM.YYYY').to('Europe/Helsinki').ceil('day').datetime,
                'ticket_uploaded': arrow.utcnow().to('Europe/Helsinki').datetime,
                'ticket_uploaded_by': g.current_user,
                'reserved': None,
                'used': None
            })
        mongo.db.tickets.insert_many(tickets)
