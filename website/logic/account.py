from flask import Blueprint, render_template, request, flash, redirect, url_for
import json
from flask_login import login_required, current_user
from ..db_models import User
from .. import db
from werkzeug.security import generate_password_hash

accountBluePrint = Blueprint('account', __name__)

@accountBluePrint.route('/', methods=['GET', 'POST'])
@login_required
def user():
    if request.method == 'GET':
        return render_template("account.html", user=current_user)
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter(User.email==email, User.id != current_user.id).first()

        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7 and len(password1) != 0:
            flash('Password must be at least 7 characters.', category='error')
        else:
            current_user.email = email
            current_user.first_name = first_name
            current_user.last_name = last_name

            if len(password1) > 0:
                current_user.password = generate_password_hash(password1, method='sha256')
            
            db.session.commit()
            flash('Account details updated!', category='success')
            
        return redirect(url_for('account.user'))

@accountBluePrint.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('query')
    results = User.query.filter(User.email.contains(query)).limit(10).all()

    list = []
    for result in results:
        list.append({'id':result.id, 'email':result.email})

    return json.dumps(list)