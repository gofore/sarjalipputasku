from flask_restful import reqparse, Resource
from flask import abort, g, Blueprint

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import HTMLConverter

import base64
import werkzeug
import tempfile
import struct
import logging
import re
import arrow
from bs4 import BeautifulSoup
import io
import os

from app import mongo
from common import auth
upload = Blueprint('upload', __name__)


def get_price(soup):
    prices = re.search("10%(\d+,\d\d)\d+,\d\d(\d+,\d\d)", soup.text).groups()
    if not prices:
        abort(422)
    price_without_tax, price_with_tax = prices
    return float(price_without_tax.replace(",", "."))


def get_html_soup(page):
    outfp = io.BytesIO()
    rsrcmgr = PDFResourceManager(caching=False)
    device = HTMLConverter(rsrcmgr, outfp)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    interpreter.process_page(page)
    html_doc = outfp.getvalue()
    soup = BeautifulSoup(html_doc, 'html.parser')
    device.close()
    outfp.close()
    return soup

def get_ticket_count_from_order(soup):
    count = re.search('Lippu: \d+ / (\d+)', soup.text)
    if not count:
        abort(422)
    return int(count.groups()[0])

def get_order_id(soup):
    order_id = re.search("Tilausnumero:\W+(\d+)", soup.text)
    if not order_id:
        abort(422)
    return order_id.groups()[0]


def get_route(soup):
    route = re.search("\d+ / \d+(.+) - (.*)Aikuinen", soup.text)
    if not route:
        abort(422)
    return sorted(route.groups())


def get_ticket_id(soup):
    ticket_id = re.search("- (.+=)", soup.text)
    if not ticket_id:
        abort(422)
    return ticket_id.groups()[0].strip()


def get_pages(fname):
    try:
        with open(fname, 'rb') as fd:
            r = [get_html_soup(page) for page in PDFPage.get_pages(fd)]
            return r
    except Exception as e:
        logging.warning(e)
        return None


def base64_encode(qrcode):
    try:
        with open(qrcode, "rb") as image_file:
            return base64.b64encode(image_file.read())
    except Exception as e:
        logging.warning(e)
        return ''


def get_ticket_type_and_expiration(soup):
    match = re.search("\d\d\.\d\d\.\d\d\d\d(.+)(\d\d\.\d\d\.\d\d\d\d)", soup.text).groups()
    if not match:
        abort(422)
    return match


class UploadView(Resource):
    @auth.login_required
    def post(self):
        def is_square(fn):
            with open(fn, 'rb') as handle:
                head = handle.read(24)
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
            os.popen('pdfimages -png ' + tmp_src_file + ' ' + tmp_dir + '/out').read()
            ims = os.popen("ls " + tmp_dir + "/out*.png").read().split()
            qr_codes = [fn for fn in ims if is_square(fn)]
            os.popen("pdfseparate " + tmp_src_file + ' ' + tmp_dir + "/pdfout-%d.pdf").read()
            pdfs = os.popen("ls " + tmp_dir + "/pdfout-*.pdf").read().split()
            pdf_files = [fn for fn in pdfs]
        except Exception:
            logging.warning("XXX: No poppler installed, unable to produce 2D barcodes")

        if len(qr_codes) != len(pdf_files):
            return {"message": "Invalid ticket file"}, 400

        tickets = []
        for qr_code, pdf_file in iter(zip(qr_codes, pdf_files)):
            pages = get_pages(pdf_file)
            if not pages:
                return {"message": "Could not parse the uploaded file, is this actually the PDF file with tickets?"}, 422
            page = pages[0]
            ticket_count = mongo.db.tickets.find({"order_id": get_order_id(page)}).count()
            if ticket_count:
                return {"message": "Ticket already uploaded"}, 400
            ticket_count_for_order = get_ticket_count_from_order(page)

            route = get_route(page)
            ticket_type, expires = get_ticket_type_and_expiration(page)
            qr_base64 = base64_encode(qr_code)
            pdf_base64 = base64_encode(pdf_file)
            tickets.append({
                'src': route[0].upper(),
                'dest': route[1].upper(),
                'qr': 'data:image/png;base64,' + str(qr_base64, 'utf-8'),
                'pdf': 'data:application/pdf;base64,' + str(pdf_base64, 'utf-8'),
                'order_id': get_order_id(page),
                'price': get_price(page) / ticket_count_for_order,
                'ticket_type': ticket_type,
                'ticket_id': get_ticket_id(page),
                'expiration_date': arrow.get(expires, 'DD.MM.YYYY').to('Europe/Helsinki').ceil('day').datetime,
                'ticket_uploaded': arrow.utcnow().to('Europe/Helsinki').datetime,
                'ticket_uploaded_by': g.current_user,
                'reserved': None,
                'used': None
            })
        mongo.db.tickets.insert_many(tickets)
