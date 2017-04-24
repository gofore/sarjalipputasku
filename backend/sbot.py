from slackbot.bot import Bot
from slackbot.bot import respond_to, default_reply
import re
import json
import requests

from app import app
from views.sessions import SessionView


BASE_URL = app.config.get('BASE_URL', 'http://localhost:5000')


def identified_user():
    def deco(f):
        def wrapper(*args, **kwargs):
            message = args[0]
            user_info = message._client.users.get(message.body["user"])
            if user_info.get('is_ultra_restricted', True):
                message.reply("Sorry, I only work with team members")
                return
            email = user_info.get('profile', {}).get('email')
            f(email, *args, **kwargs)
        return wrapper
    return deco


@respond_to('login', re.IGNORECASE)
@identified_user()
def login(email, message):
    s = SessionView()
    token = s.token_with_email(email)['token']
    message.reply("Here's your link to log in %s" % BASE_URL + '/#/tlogin?token=' + token)


@respond_to('tickets', re.IGNORECASE)
@identified_user()
def tickets(email, message):
    s = SessionView()
    token = s.token_with_email(email)['token']
    resp = requests.get(BASE_URL + '/api/v1/routesummary',
                        headers={'Authorization': 'Bearer %s' % token})
    if resp.status_code != 200:
        message.reply("Error in ticket search")
        return
    message.reply('\n'.join(['%s-%s (%s kpl)' % (x['src'], x['dest'], x['count']) for x in resp.json()]))


@respond_to(r'ticket (\S+) (\S+)\W*(EKO|EKSTRA|)', re.IGNORECASE)
@identified_user()
def ticket(email, message, src, dest, type=None):
    email = message._client.users.get(message.body["user"]).get('profile', {}).get('email')
    s = SessionView()
    token = s.token_with_email(email)['token']

    url = BASE_URL + '/api/v1/routes?src=%s&dest=%s' % (src, dest)
    if type:
        url = url + '&type=%s' % type

    resp = requests.get(url, headers={'Authorization': 'Bearer %s' % token})
    if resp.status_code != 200:
        message.reply("Error in ticket search")
        return
    if not resp.json().get('tickets'):
        message.reply("No tickets available. Login to upload new tickets (hint: say \"login\")")
        return
    ticket = resp.json().get('tickets')[0]
    attachments = [
    {
        'fallback': 'Your ticket is available! If using text mode client view your tickets here %s' % BASE_URL + '/#/tlogin?token=' + token,
        'image_url': BASE_URL + '/api/v1/qr/%s.png' % ticket['id'],
        'text': 'Ticket: %s - %s' % (src, dest),
        "fields": [{
            "title": "Ticket ID",
            "value": ticket['vr_id'],
            "short": True
        }, {
            "title": "Price (VAT0%)",
            "value": ticket['price'],
            "short": True,
        }, {
            "title": "Order ID",
            "value": ticket['order_id'],
            "short": True
        }, {
            "title": "Ticket class",
            "value": ticket['ticket_type'],
            "short": True
        }, {
            "title": "User",
            "value": email,
            "short": True
        }],
        'color': '#59afe1',
    }, {
        "title": "Reserve ticket to be used by you or release it back to ticket pool?",
        'callback_id': ticket['id'],
        "actions": [{"name": "ticket", "text": "Reserve", "type": "button", "value": "reserve", "style": "primary"},
                    {"name": "ticket", "text": "Release", "type": "button", "value": "release",
                     "confirm": {"title": "Are you sure?",
                                 "text": "Released ticket will be returned to pool of available tickets",
                                 "ok_text": "Yes",
                                 "dismiss_text": "No"}}]
    }]
    message.send_webapi('', json.dumps(attachments))

@identified_user()
@default_reply
def my_default_hanlder(message):
    message.reply('''Beep! Ask me following\n
\t- "tickets" - to list available tickets
\t- "ticket tampere helsinki (EKO|EKSTRA)" - to query tickets for a route (e.g. tampere & helsinki), optionally pass EKO or EKSTRA to query specific ticket class
\t- "login" - to get a direct login link into Sarjalipputasku web interface
''')


def main():
    bot = Bot()
    bot.run()

if __name__ == "__main__":
    main()
