from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from ..db_models import User, Config
from .. import db

from ..jobs import extract_tickets, calculate_suggestions

adminBluePrint = Blueprint('admin', __name__)

@adminBluePrint.route('/', methods=['GET', 'POST'])
@login_required
def admin():
    ticketing_tool = Config.query.filter(Config.look_up == "rest_api_ticketing_tool").first()
    api_url = Config.query.filter(Config.look_up == "rest_api_url").first()
    api_user = Config.query.filter(Config.look_up == "rest_api_user").first()
    api_pass = Config.query.filter(Config.look_up == "rest_api_pass").first()
    host_url = Config.query.filter(Config.look_up == "host_url").first()

    if current_user.admin_flag == True:
        if request.method == 'GET':
            unapproved_users = User.query.filter(User.approved_flag == False)
            return render_template("admin.html", user=current_user, ticketing_tool=ticketing_tool.value, api_url=api_url.value, api_user=api_user.value, api_pass=api_pass.value, host_url=host_url.value, unapproved_users=unapproved_users)
        if request.method == 'POST':
            ticketing_tool.value = request.form.get('ticketing_tool')
            api_url.value = request.form.get('API_URL')
            api_user.value = request.form.get('API_USER')
            api_pass.value = request.form.get('API_PASS')
            host_url.value = request.form.get('HOST_URL')

            db.session.commit()

            flash('Config updated', category='success')
            return redirect(url_for('admin.admin'))
    else:
        flash('Access denied', category='error')
        return redirect(url_for('home.home'))

@adminBluePrint.route('/approve_user', methods=['POST']) # Change to POST at some point!
@login_required
def approve_user():
    if current_user.admin_flag == True:
        if request.args.get('id') != None and request.args.get('id') != "":
            user = User.query.filter(User.id == request.args.get('id')).first()
            if user != None:
                user.approved_flag = True
                db.session.commit()
                flash('User approved', category='success')
            return redirect(url_for('admin.admin'))
        else:
            flash('Error approving user', category='error')
            return redirect(url_for('admin.admin'))
    else:
        flash('Access denied', category='error')
        return redirect(url_for('home.home'))

@adminBluePrint.route('/decline_user', methods=['POST']) # Change to POST at some point!
@login_required
def decline_user():
    if current_user.admin_flag == True:
        if request.args.get('id') != None and request.args.get('id') != "":
            user = User.query.filter(User.id == request.args.get('id')).first()
            if user != None:
                User.query.filter(User.id == request.args.get('id')).delete()
                db.session.commit()
                flash('User declined', category='success')
            return redirect(url_for('admin.admin'))
        else:
            flash('Error declining user', category='error')
            return redirect(url_for('admin.admin'))
    else:
        flash('Access denied', category='error')
        return redirect(url_for('home.home'))

@adminBluePrint.route('/extract-tickets', methods=['GET'])
@login_required
def admin_extract_tickets():
    if current_user.admin_flag == True:
        extract_tickets()
        flash('Tickets extracted', category='success')
        return redirect(url_for('admin.admin'))
    else:
        flash('Access denied', category='error')
        return redirect(url_for('home.home'))

@adminBluePrint.route('/calculate-suggestions', methods=['GET'])
@login_required
def admin_calc_suggestions():
    if current_user.admin_flag == True:
        calculate_suggestions()
        flash('Suggestions calculated', category='success')
        return redirect(url_for('admin.admin'))
    else:
        flash('Access denied', category='error')
        return redirect(url_for('home'))