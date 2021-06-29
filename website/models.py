import re
from . import create_database, db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import date

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    admin_flag = db.Column(db.Boolean)
    articles = db.relationship('Article')

    def __init__(self, email, password, first_name, last_name):
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.admin_flag = False

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(32))
    created_on = db.Column(db.Date())
    created_by = db.Column(db.String(128))
    short_description = db.Column(db.String(256))
    long_description = db.Column(db.String(4096))
    suggestions = db.relationship('Suggestion')

    def __init__(self, reference, created_by, short_description, long_description):
        self.reference = reference
        self.created_by = created_by
        self.short_description = short_description
        self.long_description = long_description

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    body = db.Column(db.String(4096))
    tags = db.Column(db.String(128))
    #attachments = db.Column(db.String(512))
    creation_date = db.Column(db.Date())
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    last_updated_date = db.Column(db.Date())
    attachments = db.relationship('Attachment')
    suggestions = db.relationship('Suggestion')
    #last_updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, tags, created_by):
        self.title = title
        self.body = body
        self.tags = tags
        self.created_by = created_by
        self.creation_date = date.today()
        self.last_updated_date = date.today()

class Suggestion(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
    ticket_id = db.Column(db.String, db.ForeignKey('ticket.reference'))
    similarity = db.Column(db.Float)

    def __init__(self, article_id, ticket_id, similarity):
        self.article_id = article_id
        self.ticket_id = ticket_id
        self.similarity = similarity

class Attachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
    file_name = db.Column(db.String(512))

    def __init__(self, article_id, file_name):
        self.article_id = article_id
        self.file_name = file_name

class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    look_up = db.Column(db.String(512))
    value = db.Column(db.String(512))

    def __init__(self, look_up, value):
        self.look_up = look_up
        self.value = value