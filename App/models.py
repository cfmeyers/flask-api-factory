from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def get_or_create(db, model, **kwargs):
    instance = db.session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        return instance

#####################################################
class Things(db.Model):

    __tablename__ = "things"

    id        = db.Column(db.Integer, primary_key=True)
    name      = db.Column(db.String)
    timeStamp = db.Column(db.DateTime)


    def __init__(self, name):
        """"""
        self.name = name.lower()
        self.timeStamp = datetime.utcnow()

#####################################################
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), unique = True)
    api_key = db.Column(db.String(120))

    def check_api_key(self, key):
        return self.api_key == key

    def is_authenticated(self):
        """Should return True unless the object represents a user that should not be allowed to authenticate for some reason. """
        return True

    def is_active(self):
        """should return True for users unless they are inactive (e.g. they've been banned)"""
        return True

    def is_anonymous(self):
        """should return True only for fake users that are not supposed to log in to the system."""
        return False

    def get_id(self):
        """should return a unique identifier for user, in unicode format. """
        return unicode(self.id)

    def __init__(self, name, api_key):
        """"""
        self.name = name
        self.api_key = int(api_key)


