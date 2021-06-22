from flask import Blueprint, render_template, request, flash, jsonify
from flask.helpers import url_for
from flask_login import login_required, current_user
from werkzeug.utils import redirect
from .models import Article
from . import db
#import json

views = Blueprint('views', __name__)

# Home
@views.route('/', methods=['GET', 'POST'])
def root():
    return redirect(url_for('views.home'))

@views.route('/home', methods=['GET'])
@login_required
def home():
    return render_template("home.html", user=current_user)


# Articles
@views.route('/articles', methods=['GET'])
@login_required
def articles():
    articles = Article.query.all()  
    return render_template("articles.html", user=current_user, articles=articles)

@views.route('/articles/<id>', methods=['GET'])
@login_required
def article(id):
    articles = Article.query.filter(Article.id == id)
    return render_template("article.html", user=current_user, articles=articles)

@views.route('/articles/add', methods=['POST'])
@login_required
def add_article():
    title = request.form.get('title')
    body = request.form.get('description')
    tags = request.form.get('tags')
    new_article = Article(title, body, tags, current_user.id)
    db.session.add(new_article)
    db.session.commit()
    id = new_article.id
    return redirect(url_for('views.article', id=id))

@views.route('/articles/delete/<id>', methods=['POST'])
@login_required
def delete_article(id):
    db.session.query(Article).filter(Article.id==id).delete()
    db.session.commit()
    flash('Article deleted', category='success')
    return redirect(url_for('views.articles'))


# Tickets
@views.route('/tickets', methods=['GET'])
@login_required
def tickets():
    return render_template("tickets.html", user=current_user)

@views.route('/tickets/<id>', methods=['GET'])
@login_required
def ticket(id):
    return render_template("tickets.html", user=current_user)


# Account
@views.route('/user', methods=['GET'])
@login_required
def user():
    return render_template("account.html", user=current_user)