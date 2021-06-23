from flask import Blueprint, render_template, request, flash, jsonify, abort, send_from_directory
from flask.helpers import url_for
from flask_login import login_required, current_user
from werkzeug.utils import redirect
from bs4 import BeautifulSoup
from .models import Article, User
from . import db
from werkzeug.utils import secure_filename
from datetime import date
#import json
import os

upload_extensions = ['.jpg', '.png', '.gif', '.pdf', '.doc', '.docx', '.xlsx', '.xlsm', '.ppt', '.pptx', '.txt']
upload_path = 'uploads'

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
    creator = User.query.filter(User.id == articles[0].created_by)
    return render_template("article.html", user=current_user, articles=articles, creator=creator[0])

@views.route('/articles/add', methods=['POST'])
@login_required
def add_article():
    title = request.form.get('title')
    body = request.form.get('editor')
    tags = request.form.get('tags')

    # Sanitizing input
    soup = BeautifulSoup(body)
    for script_elt in soup.findAll('script'):
        script_elt.extract()
    body = str(soup)

    new_article = Article(title, body, tags, current_user.id)
    db.session.add(new_article)
    db.session.commit()
    id = new_article.id

    uploaded_file = request.files['files']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in upload_extensions:
            #abort(400)
            flash('Upload file filetype not accepted, must be: .jpg, .png, .gif, .pdf, .doc, .docx, .xlsx, .xlsm, .ppt, .pptx, .txt', category='error')
        else: 
            uploaded_file.save(os.path.join(upload_path, str(id)+"_"+filename))
            new_article.attachments = str(id)+"_"+filename
            db.session.commit()
    
    flash('Article created', category='success')
    return redirect(url_for('views.article', id=id))

@views.route('/articles/delete/<id>', methods=['POST'])
@login_required
def delete_article(id):
    articles = Article.query.filter(Article.id == id)
    if articles[0].created_by == current_user.id:
        db.session.query(Article).filter(Article.id==id).delete()
        db.session.commit()
        flash('Article deleted', category='success')
        return redirect(url_for('views.articles'))
    else:
        flash('You cannot edit or delete other users articles', category='error')
        return redirect(url_for('views.article', id=id))

@views.route('/articles/edit/<id>', methods=['POST'])
@login_required
def edit_article(id):
    articles = Article.query.filter(Article.id == id)
    if articles[0].created_by == current_user.id:
        title = request.form.get('title')
        body = request.form.get('editor')
        tags = request.form.get('tags')

        # Sanitizing input
        soup = BeautifulSoup(body)
        for script_elt in soup.findAll('script'):
            script_elt.extract()
        body = str(soup)

        article = articles[0]
        article.title = title
        article.body = body
        article.tags = tags
        article.last_updated_date = date.today()
        
        uploaded_file = request.files['files']
        filename = secure_filename(uploaded_file.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in upload_extensions:
                #abort(400)
                flash('Upload file filetype not accepted, must be: .jpg, .png, .gif, .pdf, .doc, .docx, .xlsx, .xlsm, .ppt, .pptx, .txt', category='error')
            else: 
                uploaded_file.save(os.path.join(upload_path, str(id)+"_"+filename))
                article.attachments = str(id)+"_"+filename

        db.session.commit()

        flash('Article updated', category='success')
        return redirect(url_for('views.article', id=id))
    else:
        flash('You cannot edit or delete other users articles', category='error')
        return redirect(url_for('views.article', id=id))


# View uploads
@views.route('/uploads/<path:filename>', methods=['GET'])
@login_required
def upload(filename):
    return send_from_directory("../" + upload_path, filename)


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