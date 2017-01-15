class BaseConfig(object):
    DEBUG = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "secret key, change me"
    MONGO_DBNAME = "test"
