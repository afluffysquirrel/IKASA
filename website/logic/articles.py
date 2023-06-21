from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from ..db_models import Article, Attachment, User, Suggestion
from .. import db
from sqlalchemy import and_, or_, not_, func
import math
from bs4 import BeautifulSoup
from werkzeug.utils import secure_filename
import os
from flask import current_app as app
from datetime import date

articlesBluePrint = Blueprint('articles', __name__)
items_per_page = 20
upload_extensions = ['.jpg', '.png', '.gif', '.pdf', '.doc', '.docx', '.xlsx', '.xlsm', '.ppt', '.pptx', '.txt', '.zip']

with app.app_context():
        upload_path = os.path.dirname(app.instance_path) + '/uploads'

# Articles
@articlesBluePrint.route('/', methods=['GET'])
@login_required
def articles():
    # If search return all in one page
    if request.args.get('search') != None and request.args.get('search') != "":
        look_for = request.args.get('search').replace(' ', '%').lower()
        look_for = '%{0}%'.format(look_for)
        articles = Article.query.filter(
            or_(
                Article.title.like(look_for),
                Article.id.like(look_for)
            )
        )
        return render_template("articles.html", user=current_user, articles=articles, pages=1, search=request.args.get('search'))
    else:
        # If not search
        pages = int(math.ceil(Article.query.count() / items_per_page))

        # Return specific page
        if request.args.get('page') != None:
            page_number = int(request.args.get('page'))
            row_start = (page_number-1) * items_per_page
            articles = Article.query.offset(row_start).limit(items_per_page)
            return render_template("articles.html", user=current_user, articles=articles, pages=pages, page_number=page_number,  search=request.args.get('search'))
            
        #Return page 1
        else:
            articles = Article.query.limit(items_per_page)
            return render_template("articles.html", user=current_user, articles=articles, pages=pages, search=request.args.get('search'))

@articlesBluePrint.route('/<id>', methods=['GET'])
@login_required
def article(id):
    if request.args.get('search') != None and request.args.get('search') != "":
        return redirect(url_for('articles.articles', search=request.args.get('search')))

    article = Article.query.filter(Article.id == id).first()

    if article == None:
        flash('Article does not exist', category='error')
        return redirect(url_for('articles.articles'))
    else:
        # TODO fix DB model to remove requirement for two lines below with proper relationships
        creator = User.query.filter(User.id == article.created_by)
        attachments = Attachment.query.filter(Attachment.article_id == id)
        return render_template("article.html", user=current_user, article=article, creator=creator[0], attachments=attachments)

# TODO test malicious code input in title and other fields
@articlesBluePrint.route('/add', methods=['POST'])
@login_required
def add_article():
    title = request.form.get('title')
    body = request.form.get('editor')
    tags = request.form.get('tags')

    if title == "" or title == None or body == "" or body == None or tags == "" or tags == None:
        flash('Articles must contain a title, description and at least one tag', category='error')
        return redirect(url_for('articles.articles'))

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
                new_attachment = Attachment(id, str(id)+"_"+filename, 'article')
                db.session.add(new_attachment)
                db.session.commit()
    
    flash('Article created', category='success')
    return redirect(url_for('articles.article', id=id))

@articlesBluePrint.route('/delete/<id>', methods=['POST'])
@login_required
def delete_article(id):
    articles = Article.query.filter(Article.id == id)
    if articles.count() > 0:
        if articles[0].created_by == current_user.id or current_user.admin_flag == True:
            db.session.query(Article).filter(Article.id==id).delete()
            db.session.query(Suggestion).filter(Suggestion.article_id==id).delete()
            db.session.commit()
            flash('Article deleted', category='success')
            return redirect(url_for('articles.articles'))
        else:
            flash('You cannot edit or delete other users articles', category='error')
            return redirect(url_for('articles.article', id=id))
    else:
        flash('Couldnt delete article, did not exist', category='error')
        return redirect(url_for('articles.article', id=id))

#TODO on article update re-calculate suggestions
@articlesBluePrint.route('/edit/<id>', methods=['POST'])
@login_required
def edit_article(id):
    articles = Article.query.filter(Article.id == id)
    if articles[0].created_by == current_user.id or current_user.admin_flag == True:
        title = request.form.get('title')
        body = request.form.get('editor')
        tags = request.form.get('tags')

        if title == "" or title == None or body == "" or body == None or tags == "" or tags == None:
            flash('Articles must contain a title, description and at least one tag', category='error')
            return redirect(url_for('articles.article', id=id))

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
                    new_attachment = Attachment(id, str(id)+"_"+filename, 'article')
                    db.session.add(new_attachment)

        db.session.commit()

        flash('Article updated', category='success')
        return redirect(url_for('articles.article', id=id))
    else:
        flash('You cannot edit or delete other users articles', category='error')
        return redirect(url_for('articles.article', id=id))
