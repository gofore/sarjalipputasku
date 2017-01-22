from server import app
from models import db

from flask_script import Manager, Server

manager = Manager(app)
manager.add_command("runserver", Server())


@manager.command
def init_db():
    db.create_all()


if __name__ == '__main__':
    manager.run()
