from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from ..db_models import Task
from sqlalchemy import and_, or_, not_, func
import math

tasksBluePrint = Blueprint('tasks', __name__)
items_per_page = 20

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
