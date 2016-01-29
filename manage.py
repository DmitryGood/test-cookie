# manage.py

from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, g
from model_usersession import Base, User, Specification, Category, Gpl_line, Gpl
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from config import WorkConfig
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
    db.session.add(User(name='admin@test.com', role=User.USER_ROLE_ADMIN))
    db.session.commit()
    print "--- Create user 'admin@test.com'"

# Private method Load gpl to DB
def loadGPLToDatabase(session, name, filename, tag):
    '''
    :param session : open session in the database
    :param gpl: GPL file name
    :param filename: file to load words from
    :return: Dictionary {voc: <>, words: <>, added: <>, dup: <duplications found>
    '''
    gpl = Gpl(name, filename, tag)
    session.add(gpl)
    session.commit()

    factory = GplFactory(filename)
    return factory.load_gpl_to_db(session, gpl=gpl)

@manager.command
def populate_db():

    name = 'Russia GPL, 19-01-2016'
    filename = 'data/Report.xlsx'
    tag = 'base-gpl'
    loadGPLToDatabase(db.session, name, filename, tag)
    print "--- Load GPL from '%s' to database with TAG: '%s'"%(filename, tag)
    return

@manager.command
def create_data():
    print "----- Re-create database data"
    drop_db()
    create_db()
    create_admin()
    populate_db()

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
