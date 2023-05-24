from flask import Blueprint, request, flash, send_from_directory, redirect
from flask_login import login_required, current_user
from ..db_models import Article, Attachment
from .. import db
import os
from flask import current_app as app

uploadsBluePrint = Blueprint('uploads', __name__)
upload_extensions = ['.jpg', '.png', '.gif', '.pdf', '.doc', '.docx', '.xlsx', '.xlsm', '.ppt', '.pptx', '.txt', '.zip']
items_per_page = 20

with app.app_context():
        upload_path = os.path.dirname(app.instance_path) + '/uploads'

@uploadsBluePrint.route('/<arg>', methods=['GET', 'POST'])
@login_required
def upload(arg):
    if request.method == 'GET':
        return send_from_directory(upload_path, arg)
    if request.method == 'POST':
        # added hidden _method parameter as html doesnt support DELETE from forms
        #TODO delete function doesnt remove files on mac osx 
        if(request.form.get('_method') == 'DELETE'):
            attachments = Attachment.query.filter(Attachment.id == arg)
            if attachments.count() > 0:
                article_id = attachments[0].article_id
                articles = Article.query.filter(Article.id == article_id)
                if articles.count() > 0:
                    if articles[0].created_by == current_user.id or current_user.admin_flag == True:
                        os.remove(os.path.join(upload_path, attachments[0].file_name))
                        db.session.query(Attachment).filter(Attachment.id==arg).delete()
                        db.session.commit()
                        flash('Attachment deleted')
                    else:
                        flash('Delete failed - access denied', category='error')
                else:
                    flash('Error deleting attachment', category='error')
            else:
                flash('Error deleting attachment', category='error')
        else:
            flash('Delete method not specified', category='error')
        return redirect(request.referrer)