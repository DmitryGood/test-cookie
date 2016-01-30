__author__ = 'slash'

from serverTest.flask_APIdefinition import app, db
from serverTest.model_usersession import Base, UserSession

sess= db.session.query(UserSession).all()

for s in sess:
    print "Session: ", s.name, s.cookie, s.created, s.userdata

