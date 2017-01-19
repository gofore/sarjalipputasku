import sys
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice, TagExtractor
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.image import ImageWriter
import StringIO
from bs4 import BeautifulSoup
import re

def get_interp(outtype):
    outfp = StringIO.StringIO()
    rsrcmgr = PDFResourceManager(caching=False)
    device = None
    if outtype == 'text':
        device = TextConverter(rsrcmgr, outfp)
    elif outtype == 'xml':
        device = XMLConverter(rsrcmgr, outfp)
    elif outtype == 'html':
        device = HTMLConverter(rsrcmgr, outfp, imagewriter=ImageWriter('out'))
    elif outtype == 'tag':
        device = TagExtractor(rsrcmgr, outfp)

    return (PDFPageInterpreter(rsrcmgr, device), outfp, device)


def main(fname, outtype):
    fp = file(fname, 'rb')
    for page in PDFPage.get_pages(fp):
        interpreter, outfp, device = get_interp(outtype)
        interpreter.process_page(page)
        html_doc = outfp.getvalue()
        soup = BeautifulSoup(html_doc, 'html.parser')
        print soup
        spans = soup.find_all('span')
        order_id = re.search("Tilausnumero:\W+(\d+)", soup.text).groups()
        print order_id
        route = re.search("\d+ / \d+(.+) - (.*)Aikuinen", soup.text).groups()
        ticket_id = re.search("- (.+) -", soup.text).groups()
        ticket_type, expires = re.search("\d\d\.\d\d\.\d\d\d\d(.+)(\d\d\.\d\d\.\d\d\d\d)", soup.text).groups()
        print route, ticket_id, ticket_type, expires
        device.close()
    outfp.close()

main(sys.argv[1], sys.argv[2])
