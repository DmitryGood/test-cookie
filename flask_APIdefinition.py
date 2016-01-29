# project/__init__.py

import re
import datetime
import hashlib
import os
from flask import Flask, g, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from config import WorkConfig
from werkzeug import secure_filename
from flask import send_from_directory
from flask import request, jsonify, json
from SpecFactory import SpecFactory


from model_usersession import Base, User, Category, Specification, Gpl_line, Gpl   # database types
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import or_
#from project.textTokenizer import Tokenizer


# config
app = Flask(__name__, static_folder=WorkConfig.STATIC_FOLDER)
#if ('TESTING' in globals()):
#    app.config.from_object(TestConfig)
#else:
#app.config.from_object(WorkConfig)
db = SQLAlchemy(app)

# Additional import
#from flask.ext.httpauth import HTTPBasicAuth
#auth = HTTPBasicAuth()

# static routes
#print "App static folder: ", app.static_folder


@app.route('/')
def index():
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




@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file and allowed_file(file.filename):
        # get user's credentials and save him
        ip_addr = request.remote_addr
        user = User(None, User.USER_ROLE_USER,{'ip': ip_addr})
        db.session.add(user)
        db.session.commit()
        # add to filename user's cookies
        filename = secure_filename(user.cookie + '_'+file.filename)             # new secure filename with cookie string
        dest_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # save specification to disk
        file.save(dest_filename)
        # calculate the hash

        print "Internal path on server: ", filename, app.config['UPLOAD_FOLDER']
        # Log upload
        log = open(os.path.join(app.config['UPLOAD_FOLDER'], '_uploads.log'), 'a+')
        log.write("%s : upload file: %s, from user: %s, IP: %s\n"%(
            datetime.datetime.now(),
            filename,
            user.id,
            ip_addr
        ))

        # Load specification to database
        try:
            spec_factory = SpecFactory(dest_filename)
            print "specification factory created"
            hash = spec_factory.uploadSpecToDatabase(db.session,user)
            print "Spec hash: '%s', redirecting"%hash
            return redirect('#/specification/' + hash)
        except Exception as e:
            print "Exceptions happens: ", e
            return redirect('/'), 404           # Add exception handler - redirect to bug report page. /#/bugreport/ par:{filename :}
    return redirect('/'), 404


@app.route('/api/upload', methods=['POST'])
def api_upload_file():
    file = request.files['file']
    try:                                # Try to get name from request
        param = request.form['data']
        jsonObject = json.loads(param)
        name = jsonObject['name']
    except:                             # set name to none if can't
        name = None
    if file and allowed_file(file.filename):
        print ('--------->>>>>> Upload file through API call:')
        # get user's credentials and save him
        ip_addr = request.remote_addr
        user = User(None, User.USER_ROLE_USER,{'ip': ip_addr})
        db.session.add(user)
        db.session.commit()
        # add to filename user's cookies
        filename = secure_filename(user.cookie + '_'+file.filename)             # new secure filename with cookie string
        dest_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # save specification to disk
        file.save(dest_filename)
        # calculate the hash

        print "Internal path on server: ", filename, app.config['UPLOAD_FOLDER']
        # Log upload
        log = open(os.path.join(app.config['UPLOAD_FOLDER'], '_uploads.log'), 'a+')
        log.write("%s : upload file: %s, from user: %s, IP: %s\n"%(
            datetime.datetime.now(),
            filename,
            user.id,
            ip_addr
        ))

        # Load specification to database
        try:
            print "Spec name: ", name
            spec_factory = SpecFactory(dest_filename, specName=name)
            print "specification factory created"
            hash = spec_factory.uploadSpecToDatabase(db.session,user)
            print "Spec hash: '%s', return success"%hash
            #return redirect('#/specification/' + hash)
            return jsonify({'result' : True, 'hash' : hash}), 200
        except Exception as e:
            print "Exceptions happens: ", e
            #return redirect('/'), 404           # Add exception handler - redirect to bug report page. /#/bugreport/ par:{filename :}
            return jsonify({'result' : False, 'message' : 'Upload failed'}), 404
    return jsonify({'result' : False, 'message' : 'File not allowed'}), 404
    #return redirect('/'), 404

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

#@app.route('/api/specification', methods=['PUT'])
#def send_spec_to_server():
#    json_data = request.json

@app.route('/api/specification/<hash>', methods=['GET'])
def get_specification(hash):
    print "Got parameter: ", hash
    result = SpecFactory.calculateSpecResources(db.session, hash)
    return jsonify({'result': True, 'data': result}), 200


@app.route('/api/register', methods=['POST'])
def register():
    json_data = request.json
    user = User(
        name=json_data['name']

    )
    print ("new user: ", user)
    result={}
    try:
        db.session.add(user)
        db.session.commit()
        result['result'] = True
    except:
        result['result'] = False
        result['message'] = 'this user is already registered'
    db.session.close()
    return jsonify(result)



@app.route('/api/login', methods=['POST'])
def login():
    json_data = request.json
    try:
        user = db.session.query(User).filter(User.email == json_data['email']).one()
    except NoResultFound:
        print "Login API: NoResultFound exception while DB access"
        return jsonify({'result': False})
    except:
        print "Login API: unknown exception while DB access"
        return jsonify({'result': False})

    if user and user.checkPassword(json_data['password']):
        status = True
        resp = app.make_response(jsonify({'result': status, "userLogin" : user.email, "userToken" : user.get_token_string()}))
        resp.set_cookie('userLogin',value=user.email)
        resp.set_cookie('userToken', value=user.get_token_string())
        resp.set_cookie('userRole', value=str(user.role))
        print ("Server: REST API login: ", user.email, status)
    else:
        status = False
        resp = app.make_response(jsonify({'result': status, }))
    return resp


#@app.route('/logout', methods=['GET', 'POST'])
@app.route('/api/logout', methods=['POST'])
def logout():
    resp = app.make_response(jsonify({'result': 'success'}))
    resp.set_cookie('userLogin', '', expires=0)
    resp.set_cookie('userToken', '', expires =0)
    resp.set_cookie('userRole', '', expires =0)
    print ("Logging Response: ", resp)
    return resp


## -------------- Server start
if __name__ == '__main__':
    #import logging
    #logging.basicConfig(filename='flask-error.log',level=logging.DEBUG)
    print "App static folder: ", app.static_folder
    print "Database: ", app.config['SQLALCHEMY_DATABASE_URI']
    app.run()

