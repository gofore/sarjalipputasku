from app import app, mongo


def get_api_token():
    with app.app_context():
        token = mongo.db.conf.find_one({'token': {'$exists': 1}}).get('token')
        return token

API_TOKEN = get_api_token()
