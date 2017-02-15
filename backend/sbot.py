from slackbot.bot import Bot
from slackbot.bot import respond_to
import re
import json
from app import app
from views.sessions import SessionView
import requests

BASE_URL = app.config.get('BASE_URL', 'http://localhost:5000')


def identified_user():
    def deco(f):
        def wrapper(*args, **kwargs):
            message = args[0]
            email = message._client.users.get(message.body["user"]).get('profile', {}).get('email')
            f(email, *args, **kwargs)
        return wrapper
    return deco


@identified_user()
@respond_to('login', re.IGNORECASE)
def login(email, message):
    s = SessionView()
    token = s.token_with_email(email)['token']
    message.reply("Here's your link to log in %s" % BASE_URL + '/#/tlogin?token=' + token)


@identified_user()
@respond_to(r'tickets', re.IGNORECASE)
def tickets(email, message):
    s = SessionView()
    token = s.token_with_email(email)['token']
    resp = requests.get(BASE_URL + '/api/v1/routessummary',
                        headers={'Authorization': 'Bearer %s' % token})
    if resp.status_code != 200:
        message.reply("Error in ticket search")
        return

    message.reply('\n'.join(['%s-%s (%s kpl)' % (x['src'], x['dest'], x['count']) for x in resp.json()]))


@respond_to(r'ticket (\S+) (\S+)', re.IGNORECASE)
def ticket(message, src, dest):
    email = message._client.users.get(message.body["user"]).get('profile', {}).get('email')
    s = SessionView()
    token = s.token_with_email(email)['token']
    resp = requests.get(BASE_URL + '/api/v1/routes?src=%s&dest=%s' % (src, dest),
                        headers={'Authorization': 'Bearer %s' % token})
    if resp.status_code != 200:
        message.reply("Error in ticket search")
        return
    if not resp.json().get('tickets'):
        message.reply("No tickets available. Login to upload new tickets (hint: say \"login\")")
        return
    ticket = resp.json().get('tickets')[0]
    attachments = [
    {
        'fallback': 'Oldschool? Rock on, view your tickets here %s' % BASE_URL + '/#/tlogin?token=' + token,
        'image_url': 'http://i.imgur.com/Cpi7K5w.png', #BASE_URL + '/api/v1/qr/%s.png' % ticket['id'],
        'text': 'Ticket: %s - %s' % (src, dest),
        "fields": [{
            "title": "Ticket ID",
            "value": ticket['vr_id'],
            "short": True
        }, {
            "title": "Price",
            "value": ticket['price'],
            "short": True,
        }, {
            "title": "Order ID",
            "value": ticket['order_id'],
            "short": True
        }],
        'color': '#59afe1',
        "actions": [{"name": "ticket", "text": "Reserve", "type": "button", "value": "reserve"},
                    {"name": "ticket", "text": "Release", "type": "button", "value": "release"}]
    }]
    message.send_webapi('', json.dumps(attachments))


def main():
    bot = Bot()
    bot.run()

if __name__ == "__main__":
    main()
