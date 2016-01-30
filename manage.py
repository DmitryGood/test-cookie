# manage.py

from flask_script import Manager
from model_usersession import Base, UserSession
from config import WorkConfig, TestConfig
from flask_APIdefinition import app, db



#app = Flask(__name__,  static_folder=WorkConfig.STATIC_FOLDER)
app.config.from_object(WorkConfig)


manager = Manager(app)

# ----------- Private methods

# -----------

@manager.command
def create_db():
    """Creates the db tables ."""
    Base.metadata.create_all(db.engine)
    print "--- Create database"



@manager.command
def drop_db():
    """Drops the db tables."""
    Base.metadata.drop_all(db.engine)
    print "--- Drop database"

@manager.command
def create_admin():
    """Creates the admin user."""

@manager.command
def run_debug():
    app.config.from_object(TestConfig)
    create_db()
    app.run(debug=True)

@manager.command
def run_public():
    app.run(host="0.0.0.0", debug=True)

@manager.command
def run_hand():
    print "App static folder: ", app.static_folder
    app.run()

@manager.command
def run_ssl():
    app.run(host="0.0.0.0", debug=True, ssl_context=app.config['SSL_CONTEXT'])

if __name__ == '__main__':
    print "App static folder: ", app.static_folder
    print "Database: ", app.config['SQLALCHEMY_DATABASE_URI']
    manager.run()
