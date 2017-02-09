class BaseConfig(object):
    DEBUG = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "secret key, change me"
    MONGO_DBNAME = "test"
    BASE_URL = 'http://localhost:5000'
    DUMMY_AUTHENTICATION = False
    SLACKBOT_API_TOKEN = ''
