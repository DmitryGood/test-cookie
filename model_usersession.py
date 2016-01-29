__author__ = 'slash'
from sqlalchemy import Column, String, Integer, ForeignKey, PickleType, Float, Boolean, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
import pickle
import datetime
import hashlib
from exceptions import ValueError
from flask import Flask
from config import BaseConfig


Base = declarative_base()

class UserSession(Base):
    __tablename__ = 'usersession'
    ''' the table to store user

    '''
    id = Column(Integer, primary_key=True, autoincrement=True)
    cookie = Column(String, nullable=False)
    name = Column(String)
    created = Column(DateTime, nullable=False)
    userdata = Column(PickleType)

    def __init__(self, name=None, userdata=None):
        self.name = name
        self.userdata = userdata
        self.created = datetime.datetime.now()
        # create cookie for user as hash of his first entrance time
        self.cookie = hashlib.sha1(str(self.created)).hexdigest() # create cookie for user as hash of his first entrance time
        return

    def getCookie(self):
        return self.cookie

