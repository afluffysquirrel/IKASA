from . import create_database, db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    articles = db.relationship('Article')

    def __init__(self, email, password, first_name, last_name):
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    body = db.Column(db.String(4096))
    tags = db.Column(db.String(128))
    attachments = db.Column(db.String(512))
    creation_date = db.Column(db.DateTime())
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    last_updated_date = db.Column(db.DateTime())
    #last_updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, created_by):
        self.title = title
        self.body = body
        self.created_by = created_by
        self.creation_date = datetime.now()

class Suggestion(db.Model): 
    id = db.Column(db.Integer, primary_key=True)