from flask import Blueprint, render_template
from flask_login import login_required, current_user
from ..db_models import Article, Ticket, Suggestion
from .. import db
from sqlalchemy import and_, or_, not_, func

homeBluePrint = Blueprint('home', __name__)

@homeBluePrint.route('/', methods=['GET'])
@login_required
def home():
    article_count = Article.query.count()
    ticket_count = Ticket.query.count()
    suggestion_count = Suggestion.query.count()

    weak_count = Suggestion.query.filter(and_(Suggestion.similarity >= 0.3, Suggestion.similarity < 0.45)).count()
    mod_count = Suggestion.query.filter(and_(Suggestion.similarity >= 0.45, Suggestion.similarity < 0.6)).count()
    strong_count = Suggestion.query.filter(and_(Suggestion.similarity >= 0.6, Suggestion.similarity < 1.0)).count()
    tick_suggest_count = db.session.query(Suggestion.ticket_ref).distinct().count()
    avg_match_strength = Suggestion.query.with_entities(func.avg(Suggestion.similarity)).scalar()
    
    info_message = "Application status is good, please continue to add and update knowledge articles."

    if(tick_suggest_count > 0):
        if(((ticket_count - tick_suggest_count) / tick_suggest_count) > 2):
            info_message = "Your ratio of tickets with suggestions to those without is low! Try adding more knowledge articles to boost this."
        elif(avg_match_strength < 0.45):
            info_message = str(avg_match_strength) + " Your average match strength is low, try adding more detail into ticket and article titles, descriptions and tags."

    return render_template("home.html", user=current_user, article_count=article_count, ticket_count=ticket_count, suggestion_count=suggestion_count, weak_count=weak_count, mod_count=mod_count, strong_count=strong_count, tick_suggest_count=tick_suggest_count, info_message=info_message)
