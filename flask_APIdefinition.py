# project/__init__.py

import re
import datetime
import hashlib
import os
from flask import Flask, g, request, redirect, url_for, make_response, Request, Response, render_template, render_template_string
from flask_sqlalchemy import SQLAlchemy
from config import WorkConfig
#from werkzeug import secure_filename
from flask import send_from_directory
from flask import request, jsonify, json


from model_usersession import Base, UserSession   # database types
from sqlalchemy.orm.exc import NoResultFound


# config
app = Flask(__name__, static_folder=WorkConfig.STATIC_FOLDER, template_folder=WorkConfig.TEMPLATE_FOLDER)
db = SQLAlchemy(app)


# Static files
@app.route('/')
def index():
    print "------->>>>>>> We are in GET request"
    user_cookie = request.cookies
    username = user_cookie.get('username')
    print "GET: Username cookie: ", username
    if (username):
        return render_template('hi_page.html', username = username)
    #
    print "App static folder: ", app.static_folder
    return app.send_static_file('index.html'), 200

@app.route('/<path:path>', methods=['GET'])
def static_site(path):
    return app.send_static_file(path), 200

''' ------------ API stuff begins
'''
## -------- tools -----
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

## --------- end -------


@app.route('/api/function', methods=['POST'])
def function():
    print "------->>>>>>> We are here"
    user_cookie = request.cookies
    username = user_cookie.get('username')
    print "POST: Username cookie: ", username
    if (username):
        return "Hi, my dear, " + username
    #param = json.loads(request.form['data'])
    #print "pram: ", param
    name= request.form['name']
    ip=request.remote_addr
    print 'name: ', name, ip
    session = UserSession(name,ip)
    db.session.add(session)
    db.session.commit()
    print "Prepare result: ", session.cookie
    cookie = session.cookie
    #return jsonify({'cookie' : cookie, 'name': name}), 200
    response = redirect('/', 302)
    now=datetime.datetime.now()
    delta=datetime.timedelta(minutes=2)
    expire_date = now + delta
    print "Time: %s, expires in: %s, the date: %s"%(now, delta, expire_date)
    response.set_cookie('username', name, expires=expire_date)

    return response

@app.route('/api/remove_cookie')
def remove_cookie():
    name = request.cookies.get('username')
    print "Found user: ", name
    response = redirect('/', 302)
    response.set_cookie('username', 'removed', -1, -1)
    return response


## -------------- Server start
if __name__ == '__main__':
    #import logging
    #logging.basicConfig(filename='flask-error.log',level=logging.DEBUG)
    print "App static folder: ", app.static_folder
    print "Database: ", app.config['SQLALCHEMY_DATABASE_URI']
    app.run()

