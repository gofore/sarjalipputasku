from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__, static_url_path='')
app.config.setdefault('MONGO_DBNAME', "test")
app.config.from_object('config.BaseConfig')
app.config.from_envvar('SARJALIPPUTASKU_CONFIGFILE')

mongo = PyMongo(app)
