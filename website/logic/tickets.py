from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from ..db_models import Article, Ticket, Suggestion
from .. import db
from sqlalchemy import and_, or_, not_, func
import math

ticketsBluePrint = Blueprint('tickets', __name__)
items_per_page = 20

@ticketsBluePrint.route('/', methods=['GET'])
@login_required
def tickets():
    # If search return all in one page
    if request.args.get('search') != None and request.args.get('search') != "":
        look_for = request.args.get('search').replace(' ', '%').lower()
        look_for = '%{0}%'.format(look_for)
        tickets = Ticket.query.filter(
            or_(
                Ticket.short_description.like(look_for),
                Ticket.reference.like(look_for)
            )
        ).order_by(Ticket.reference.desc())
        return render_template("tickets.html", user=current_user, tickets=tickets, pages=1, search=request.args.get('search'))
    else:
        # If not search
        pages = int(math.ceil(Ticket.query.count() / items_per_page))

        # Return specific page
        if request.args.get('page') != None:
            page_number = int(request.args.get('page'))
            row_start = (page_number-1) * items_per_page
            tickets = Ticket.query.order_by(Ticket.reference.desc()).offset(row_start).limit(items_per_page)
            return render_template("tickets.html", user=current_user, tickets=tickets, pages=pages, page_number=page_number,  search=request.args.get('search'))
            
        #Return page 1
        else:
            tickets = Ticket.query.order_by(Ticket.reference.desc()).limit(items_per_page)
            return render_template("tickets.html", user=current_user, tickets=tickets, pages=pages, search=request.args.get('search'))

@ticketsBluePrint.route('/<id>', methods=['GET'])
@login_required
def ticket(id):

    if request.args.get('search') != None and request.args.get('search') != "":
            return redirect(url_for('tickets.tickets', search=request.args.get('search')))

    ticket = Ticket.query.filter(Ticket.id == id).first()

    if ticket == None:
        flash('Ticket does not exist', category='error')
        return redirect(url_for('tickets.tickets'))
    else:
        query = db.session.query(Article, Ticket, Suggestion) \
        .filter(Suggestion.article_id == Article.id, Suggestion.ticket_ref == Ticket.reference, Suggestion.ticket_ref == ticket.reference, Suggestion.task_id==None) \
        .order_by(Suggestion.similarity.desc()).all()

        return render_template("ticket.html", user=current_user, ticket=ticket, query=query)
