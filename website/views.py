from flask import Blueprint, render_template, request, flash, jsonify
from flask.helpers import url_for
from flask_login import login_required, current_user
from werkzeug.utils import redirect
#from .models import Note
from . import db
import json

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def root():
    '''
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')
    '''
    return redirect(url_for('views.home'))

@views.route('/home', methods=['GET'])
@login_required
def home():
    return render_template("home.html", user=current_user)

@views.route('/articles', methods=['GET'])
@login_required
def articles():
    return render_template("articles.html", user=current_user)

@views.route('/tickets', methods=['GET'])
@login_required
def tickets():
    return render_template("tickets.html", user=current_user)

@views.route('/user', methods=['GET'])
@login_required
def user():
    return render_template("account.html", user=current_user)