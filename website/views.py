from flask import Blueprint, render_template, request, flash, send_from_directory
from flask.helpers import url_for
from flask_login import login_required, current_user
from werkzeug.utils import redirect
from bs4 import BeautifulSoup
from .models import Article, Attachment, User, Ticket, Suggestion
from . import db
from werkzeug.utils import secure_filename
from datetime import date
import math
import os

upload_extensions = ['.jpg', '.png', '.gif', '.pdf', '.doc', '.docx', '.xlsx', '.xlsm', '.ppt', '.pptx', '.txt']
upload_path = 'uploads'
items_per_page = 20

views = Blueprint('views', __name__)

# Home
@views.route('/', methods=['GET', 'POST'])
def root():
    return redirect(url_for('views.home'))

@views.route('/home', methods=['GET'])
@login_required
def home():
    article_count = Article.query.count()
    ticket_count = Ticket.query.count()
    suggestion_count = Suggestion.query.count()
    return render_template("home.html", user=current_user, article_count=article_count, ticket_count=ticket_count, suggestion_count=suggestion_count)


# Articles
@views.route('/articles', methods=['GET'])
@login_required
def articles():
    #articles = Article.query.all() 
    articles = Article.query.limit(items_per_page)
    pages = int(math.ceil(Article.query.count() / items_per_page))
    return render_template("articles.html", user=current_user, articles=articles, pages=pages)

@views.route('/articles/page/<page_number>', methods=['GET'])
@login_required
def articles_page_number(page_number):
    page_number = int(page_number)
    row_start = (page_number-1) * items_per_page
    articles = Article.query.offset(row_start).limit(items_per_page)
    pages = int(math.ceil(Article.query.count() / items_per_page))
    return render_template("articles.html", user=current_user, articles=articles, pages=pages, page_number=page_number)

@views.route('/articles/<id>', methods=['GET'])
@login_required
def article(id):
    article = Article.query.filter(Article.id == id).first()
    creator = User.query.filter(User.id == article.created_by)
    attachments = Attachment.query.filter(Attachment.article_id == id)
    return render_template("article.html", user=current_user, article=article, creator=creator[0], attachments=attachments)

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

    files = request.files.getlist("files")
    for uploaded_file in files:
        filename = secure_filename(uploaded_file.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in upload_extensions:
                #abort(400)
                flash('Upload file "' + uploaded_file.filename + '" filetype not accepted, must be: .jpg, .png, .gif, .pdf, .doc, .docx, .xlsx, .xlsm, .ppt, .pptx, .txt', category='error')
            else: 
                uploaded_file.save(os.path.join(upload_path, str(id)+"_"+filename))
                new_attachment = Attachment(id, str(id)+"_"+filename)
                db.session.add(new_attachment)
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
        
        files = request.files.getlist("files")
        for uploaded_file in files:
            filename = secure_filename(uploaded_file.filename)
            if filename != '':
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in upload_extensions:
                    #abort(400)
                    flash('Upload file "' + uploaded_file.filename + '" filetype not accepted, must be: .jpg, .png, .gif, .pdf, .doc, .docx, .xlsx, .xlsm, .ppt, .pptx, .txt', category='error')
                else: 
                    uploaded_file.save(os.path.join(upload_path, str(id)+"_"+filename))
                    new_attachment = Attachment(id, str(id)+"_"+filename)
                    db.session.add(new_attachment)

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
    tickets = Ticket.query.limit(items_per_page)
    pages = int(math.ceil(Ticket.query.count() / items_per_page))
    return render_template("tickets.html", user=current_user, tickets=tickets, pages=pages)

@views.route('/tickets/page/<page_number>', methods=['GET'])
@login_required
def tickets_page_number(page_number):
    page_number = int(page_number)
    row_start = (page_number-1) * items_per_page
    tickets = Ticket.query.offset(row_start).limit(items_per_page)
    pages = int(math.ceil(Ticket.query.count() / items_per_page))
    return render_template("tickets.html", user=current_user, tickets=tickets, pages=pages, page_number=page_number)

@views.route('/tickets/<id>', methods=['GET'])
@login_required
def ticket(id): 
    ticket = Ticket.query.filter(Ticket.id == id).first()
    return render_template("ticket.html", user=current_user, ticket=ticket)

# Account
@views.route('/user', methods=['GET'])
@login_required
def user():
    return render_template("account.html", user=current_user)