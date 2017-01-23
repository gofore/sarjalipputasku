from app import db


class Ticket(db.Model):
    __tablename__ = 'tickets'

    id = db.Column(db.String(32), primary_key=True)
    src = db.Column(db.Text)
    dest = db.Column(db.Text)
    price = db.Column(db.Numeric)
    qr = db.Column(db.Text)
    order_id = db.Column(db.Text)
    ticket_type = db.Column(db.Text)
    ticket_id = db.Column(db.Text)
    expiration_date = db.Column(db.DateTime)
    uploaded = db.Column(db.DateTime)
    uploaded_by = db.Column(db.Text)
    updated_by = db.Column(db.Text)
    reserved = db.Column(db.DateTime)
    used = db.Column(db.DateTime)
