from flask_login import login_required, current_user
from ..db_models import Task, Suggestion, Article, Attachment
from sqlalchemy import and_, or_, not_, func
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .. import db
import math
from bs4 import BeautifulSoup
from werkzeug.utils import secure_filename
from flask import current_app as app
import os

tasksBluePrint = Blueprint('tasks', __name__)
items_per_page = 20
upload_extensions = ['.jpg', '.png', '.gif', '.pdf', '.doc', '.docx', '.xlsx', '.xlsm', '.ppt', '.pptx', '.txt', '.zip']

with app.app_context():
        upload_path = os.path.dirname(app.instance_path) + '/uploads'

@tasksBluePrint.route('/', methods=['GET'])
@login_required
def tasks():
    # If search return all in one page
    if request.args.get('search') != None and request.args.get('search') != "":
        look_for = request.args.get('search').replace(' ', '%').lower()
        look_for = '%{0}%'.format(look_for)
        tasks = Task.query.filter(
            or_(
                Task.short_description.like(look_for),
                Task.id.like(look_for)
            )
        ).order_by(Task.id.desc())
        return render_template("tasks.html", user=current_user, tasks=tasks, pages=1, search=request.args.get('search'))
    else:
        # If not search
        pages = int(math.ceil(Task.query.count() / items_per_page))

        # Return specific page
        if request.args.get('page') != None:
            page_number = int(request.args.get('page'))
            row_start = (page_number-1) * items_per_page
            tasks = Task.query.order_by(Task.id.desc()).offset(row_start).limit(items_per_page)
            return render_template("tasks.html", user=current_user, tasks=tasks, pages=pages, page_number=page_number,  search=request.args.get('search'))
            
        #Return page 1
        else:
            tasks = Task.query.order_by(Task.id.desc()).limit(items_per_page)
            return render_template("tasks.html", user=current_user, tasks=tasks, pages=pages, search=request.args.get('search'))

@tasksBluePrint.route('/<id>', methods=['GET'])
@login_required
def task(id):
    if request.args.get('search') != None and request.args.get('search') != "":
            return redirect(url_for('tasks.tasks', search=request.args.get('search')))

    task = Task.query.filter(Task.id == id).first()

    if task == None:
        flash('Task does not exist', category='error')
        return redirect(url_for('tasks.tasks'))
    else:
        query = db.session.query(Article, Task, Suggestion) \
        .filter(Suggestion.article_id == Article.id, Suggestion.task_id == Task.id, Suggestion.task_id == task.id) \
        .order_by(Suggestion.similarity.desc()).all()

        attachments = Attachment.query.filter(Attachment.task_id == id)

        return render_template("task.html", user=current_user, task=task, query=iter([]), attachments=attachments)
    
@tasksBluePrint.route('/delete/<id>', methods=['POST'])
@login_required
def delete_task(id):
    tasks = Task.query.filter(Task.id == id)
    if tasks.count() > 0:
        if tasks[0].created_by == current_user.id or current_user.admin_flag == True:
            db.session.query(Task).filter(Task.id==id).delete()
            db.session.query(Suggestion).filter(Suggestion.task_id==id).delete()
            db.session.commit()
            flash('Task deleted', category='success')
            return redirect(url_for('tasks.tasks'))
        else:
            flash('You cannot edit or delete other users tasks', category='error')
            return redirect(url_for('tasks.tasks', id=id))
    else:
        flash('Couldnt delete task, did not exist', category='error')
        return redirect(url_for('tasks.tasks', id=id))

    
@tasksBluePrint.route('/add', methods=['POST'])
@login_required
def add_task():
    title = request.form.get('title')
    body = request.form.get('editor')

    # TODO assigned to functionality and due date
    assigned_to = request.form.get('assigned')
    due_date = request.form.get('due')

    if title == "" or title == None:
        flash('Task must contain a title', category='error')
        return redirect(url_for('tasks.tasks'))

    # Sanitizing input
    soup = BeautifulSoup(body)
    for script_elt in soup.findAll('script'):
        script_elt.extract()
    body = str(soup)

    new_task = Task(title, body, current_user)
    db.session.add(new_task)
    db.session.commit()
    id = new_task.id

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
    
    flash('Task created', category='success')
    return redirect(url_for('tasks.tasks', id=id))
