from flask import Flask

app = Flask(__name__, static_url_path='')
app.config.setdefault('MONGO_DBNAME', "test")