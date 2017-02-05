from flask import Flask
from flask_pymongo import PyMongo
import os
app = Flask(__name__, static_url_path='')
app.config.setdefault('MONGO_DBNAME', "test")
app.config.from_object('config.BaseConfig')

CONF_FROM_ENV = 'SARJALIPPUTASKU_CONFIGFILE'
if os.environ.get(CONF_FROM_ENV):
    app.config.from_envvar(CONF_FROM_ENV)

mongo = PyMongo(app)
