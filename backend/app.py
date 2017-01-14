from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__, static_url_path='')
app.config.setdefault('MONGO_DBNAME', "test")

mongo = PyMongo(app)
