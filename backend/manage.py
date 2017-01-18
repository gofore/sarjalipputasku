from server import app
from flask_script import Manager, Server, Shell

manager = Manager(app)

manager.add_command("runserver", Server())

if __name__ == '__main__':
    manager.run()
