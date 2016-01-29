__author__ = 'slash'
import unittest
import hashlib

from flask import Flask
from sqlalchemy import create_engine, and_, not_, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound


#from project.models import User

from serverTest.model_usersession import Base, UserSession
from serverTest.config import TestConfig

app = Flask(__name__)
app.config.from_object(TestConfig)
app.config['TESTING'] = True


class MyTest(unittest.TestCase):


    # ---------------------------------------------------------
    # ------------------- Helper procedures--------------------
    # ---------------------------------------------------------
    def populate_db(self):

        return


# ---------------------------------------------------------


    def create_app(self):
        return app

    def setUp(self):

        # Create the engine. This starts a fresh database
        self.engine = create_engine('sqlite://')
        # Fills the database with the tables needed.
        # If you use declarative, then the metadata for your tables can be found using Base.metadata
        Base.metadata.create_all(self.engine)
        # Create a session to this database
        Base.metadata.bind = self.engine
        self.db=Base
        self.session = sessionmaker(bind=self.engine)()
        print " ----------- Starting new tests -------"
        print " --------------------------------------"

    def tearDown(self):

        self.session.close()
        #self.db.drop()


    def test_basic_insert_UserSession(self):
        ses = UserSession('user', '10.0.0.1')
        self.session.add(ses)
        self.session.commit()

        token = ses.cookie;
        self.assertTrue(token != None)

