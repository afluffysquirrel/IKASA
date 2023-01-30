from random import randint

from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import date
from flask_sqlalchemy import SQLAlchemy

def generate_user_id():
    min_ = 100000
    max_ = 999999
    rand = randint(min_, max_)
    
    while SQLAlchemy().session().query(User).filter(id == rand).limit(1).first() is not None:
        rand = randint(min_, max_)

    return rand

def generate_ticket_id():
    min_ = 100000
    max_ = 999999
    rand = "T" + str(randint(min_, max_))
    
    while SQLAlchemy().session().query(Ticket).filter(id == rand).limit(1).first() is not None:
        rand = "T" + str(randint(min_, max_))

    return rand

def generate_article_id():
    min_ = 100000
    max_ = 999999
    rand = "A" + str(randint(min_, max_))
    
    while SQLAlchemy().session().query(Article).filter(id == rand).limit(1).first() is not None:
        rand = "A" + str(randint(min_, max_))

    return rand

def generate_task_id():
    min_ = 100000
    max_ = 999999
    rand = "TSK" + str(randint(min_, max_))
    
    while SQLAlchemy().session().query(Ticket).filter(id == rand).limit(1).first() is not None:
        rand = "TSK" + str(randint(min_, max_))

    return rand

class User(db.Model, UserMixin):
    id = db.Column(db.Integer,  default=generate_user_id, unique=True, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    admin_flag = db.Column(db.Boolean)
    approved_flag = db.Column(db.Boolean)
    articles = db.relationship('Article')
    tasks = db.relationship('Task')

    def __init__(self, email, password, first_name, last_name):
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.admin_flag = False
        self.approved_flag = False

class Ticket(db.Model):
    id = db.Column(db.String,  default=generate_ticket_id, unique=True, primary_key=True)
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
    id = db.Column(db.String,  default=generate_article_id, unique=True, primary_key=True)
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
    task_id = db.Column(db.String, db.ForeignKey('task.id'))
    ticket_ref = db.Column(db.String, db.ForeignKey('ticket.reference'))
    similarity = db.Column(db.Float)

    def __init__(self, article_id, ref_id, similarity, type = None):
        if type is None:
            raise Exception("Suggestion type not defined")
        if type == 'ticket':
            self.article_id = article_id
            self.ticket_ref = ref_id
            self.similarity = similarity
        if type == 'task':
            self.article_id = article_id
            self.task_id = ref_id
            self.similarity = similarity

class Attachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.String, db.ForeignKey('article.id'))
    task_id = db.Column(db.String, db.ForeignKey('task.id'))
    file_name = db.Column(db.String(512))

    def __init__(self, ref_id, file_name, type = None):
        if type is None:
            raise Exception("Attachment type not defined")
        if type == 'article':
            self.article_id = ref_id
            self.file_name = file_name
        if type == 'task':
            self.task_id = ref_id
            self.file_name = file_name

class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    look_up = db.Column(db.String(512))
    value = db.Column(db.String(512))

    def __init__(self, look_up, value):
        self.look_up = look_up
        self.value = value

class WriteBack(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    ticket_ref = db.Column(db.String, db.ForeignKey('ticket.reference'))

    def __init__(self, ticket_ref):
        self.ticket_ref = ticket_ref

#TODO Create db model for tasks
class Task(db.Model):
    id = db.Column(db.String,  default=generate_task_id, unique=True, primary_key=True)
    short_description = db.Column(db.String(128))
    long_description = db.Column(db.String(4096))
    creation_date = db.Column(db.Date())
    last_updated_date = db.Column(db.Date())
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    priority = db.Column(db.Integer)
    attachments = db.relationship('Attachment')
    suggestions = db.relationship('Suggestion')

    #TODO create task_category model
    #category = db.Column(db.Integer, db.ForeignKey('task_category.id'))

    def __init__(self, reference, created_by, short_description, long_description):
        self.reference = reference
        self.created_by = created_by
        self.short_description = short_description
        self.long_description = long_description

