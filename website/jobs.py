import pandas as pd
import scipy.spatial
from .ticket_tool_models import ServiceNow
from sentence_transformers import SentenceTransformer
from datetime import datetime
from sqlalchemy import and_, or_, not_, func

def console_log(message, log_type):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    string = '[' + current_time + '] Scheduled Job : '
    if log_type == 'error':
        string += 'Error - '
    string += message
    print(string)

def calculate_suggestions():
    console_log('Calculating suggestions...', '')

    # Setting pre-trained model
    embedder = SentenceTransformer('all-MiniLM-L12-v2')

    #Setting nearest neighbour
    closest_n = 5

    # Setting minimum similarity score to generate suggestion
    # TODO make this toggleable from front end (admin)
    sensitivity = 0.3

    from . import db
    from .db_models import Article, Suggestion, WriteBack

    # Read last 999 tickets from DB
    tickets = pd.read_sql_query("select * from Ticket order by created_on desc limit 999;", con = db.session.connection())

    # Read last 999 tasks from DB
    tasks = pd.read_sql_query("select * from Task order by creation_date desc limit 999;", con = db.session.connection())
    
    #Read all articles from DB
    articles = pd.read_sql_table(table_name = Article.__table__.name, con = db.session.connection(), index_col="id")

    # Pre-format data for the model
    articles["tags"] = articles["tags"].str.replace(",","")
    articles = articles.applymap(lambda s:s.lower() if type(s) == str else s)
    articles['soup'] = articles['title'] + " " + articles['tags']

    tickets = tickets.applymap(lambda s:s.lower() if type(s) == str else s)
    tickets['soup'] = tickets['short_description'] + " " + tickets['long_description']

    tasks = tasks.applymap(lambda s:s.lower() if type(s) == str else s)
    tasks['soup'] = tasks['short_description'] + " " + tasks['long_description']
    
    corpus = []
    articleIDs = []

    for index, row in articles.iterrows():

        # Remove duplicates from article - Removed as retaining sentence structure generates more accurate suggestions
        # row['soup'] = ' '.join(OrderedDict((w,w) for w in row['soup'].split()).keys())

        # Remove special chars from article
        row['soup'] = row['soup'].replace('\W', '')

        corpus.append(row['soup'])
        articleIDs.append(str(index))

    corpus_embeddings = embedder.encode(corpus)
    
    for index, row in tickets.iterrows():

        # Used for SR API write back, if any suggestions are generated this becomes true
        suggestionFlag = False
        ticket_ref = ""

        # Remove duplicates from ticket - Removed as retaining sentence structure generates more accurate suggestions
        # row['soup'] = ' '.join(OrderedDict((w,w) for w in row['soup'].split()).keys())

        # Remove special chars from ticket
        row['soup'] = row['soup'].replace('\W', '')

        queries = [row['soup']]
        query_embeddings = embedder.encode(queries)
        
        # Calculating cosine similarity (Match Strength)
        for query, query_embedding in zip(queries, query_embeddings):
            distances = scipy.spatial.distance.cdist([query_embedding], corpus_embeddings, "cosine")[0]

            results = zip(range(len(distances)), distances)
            results = sorted(results, key=lambda x: x[1])

            for idx, distance in results[0:closest_n]:
                if((1-distance) >= sensitivity):
                    ticket_ref = row['reference'].upper()
                    #query = corpus[idx].strip()
                    article_id = articleIDs[idx]
                    
                    # Checking suggestion doesnt already exist
                    
                    query = Suggestion.query.filter(and_(Suggestion.article_id==article_id, Suggestion.ticket_ref==ticket_ref, Suggestion.task_id==None)).first()

                    if query == None:
                        # Adding suggestion to DB
                        new_suggestion = Suggestion(article_id, ticket_ref, round((1-distance),2), 'ticket')
                        db.session.add(new_suggestion)
                        db.session.commit()
                        suggestionFlag = True
        
        # If suggestions calculated check db to see if write back done previously
        # In event no writeback has been previously done use rest API to add comment 
        if(suggestionFlag == True):
            # query = WriteBack.query.filter(WriteBack.ticket_ref==ticket_ref).first()
            if query == None:
                # write_back_API(ticket_ref)
                # TODO enable write back again 
                None
    
    
    for index, row in tasks.iterrows():

        # Used for SR API write back, if any suggestions are generated this becomes true
        suggestionFlag = False
        task_id = ""

        # Remove duplicates from ticket - Removed as retaining sentence structure generates more accurate suggestions
        # row['soup'] = ' '.join(OrderedDict((w,w) for w in row['soup'].split()).keys())

        # Remove special chars from ticket
        row['soup'] = row['soup'].replace('\W', '')

        queries = [row['soup']]
        query_embeddings = embedder.encode(queries)
        
        # Calculating cosine similarity (Match Strength)
        for query, query_embedding in zip(queries, query_embeddings):
            distances = scipy.spatial.distance.cdist([query_embedding], corpus_embeddings, "cosine")[0]

            results = zip(range(len(distances)), distances)
            results = sorted(results, key=lambda x: x[1])

            for idx, distance in results[0:closest_n]:
                if((1-distance) >= sensitivity):
                    task_id = row['id'].upper()
                    article_id = articleIDs[idx]
                    
                    # Checking suggestion doesnt already exist
                    query = Suggestion.query.filter(and_(Suggestion.article_id==article_id, Suggestion.task_id==task_id, Suggestion.ticket_ref==None)).first()
                    
                    if query == None:
                        # Adding suggestion to DB
                        new_suggestion = Suggestion(article_id, task_id, round((1-distance),2), 'task')
                        db.session.add(new_suggestion)
                        db.session.commit()
                        suggestionFlag = True
        
        # If suggestions calculated check db to see if write back done previously
        # In event no writeback has been previously done use rest API to add comment 
        if(suggestionFlag == True):
            # query = WriteBack.query.filter(WriteBack.ticket_ref==ticket_ref).first()
            if query == None:
                # write_back_API(ticket_ref)
                # TODO enable write back again 
                None

    console_log('Suggestions calculated', '')


def extract_tickets():
    from .db_models import Config

    rest_api_ticketing_tool = Config.query.filter(Config.look_up == "rest_api_ticketing_tool").first()
    rest_api_user = Config.query.filter(Config.look_up == "rest_api_user").first()
    rest_api_pass = Config.query.filter(Config.look_up == "rest_api_pass").first()
    rest_api_url = Config.query.filter(Config.look_up == "rest_api_url").first()
    host_url = Config.query.filter(Config.look_up == "host_url").first()

    #Connection validation
    if rest_api_ticketing_tool.value is not None and rest_api_ticketing_tool.value != "" \
    and rest_api_user.value is not None and rest_api_user.value != "" \
    and rest_api_pass.value is not None and rest_api_pass.value != "" \
    and rest_api_url.value is not None and rest_api_url.value != "" \
    and  host_url.value is not None and host_url.value != "":

        ticketTool = None
        tickets = []

        if rest_api_ticketing_tool.value == "ServiceNow":
            ticketTool = ServiceNow()
        
        if ticketTool != None:
            tickets = ticketTool.extract(rest_api_url, rest_api_user, rest_api_pass)

            from . import db
            s = db.session()
            for ticket in tickets:
                s.add(ticket)
                s.commit()

    else:
        console_log("Missing extract credentials", 'error')


def write_back_API(ticket_ref):

    from .db_models import Config, WriteBack
    from . import db

    rest_api_ticketing_tool = Config.query.filter(Config.look_up == "rest_api_ticketing_tool").first()
    rest_api_user = Config.query.filter(Config.look_up == "rest_api_user").first()
    rest_api_pass = Config.query.filter(Config.look_up == "rest_api_pass").first()
    rest_api_url = Config.query.filter(Config.look_up == "rest_api_url").first()
    host_url = Config.query.filter(Config.look_up == "host_url").first()

    #Connection validation
    if rest_api_ticketing_tool.value is not None and rest_api_ticketing_tool.value != "" \
    and rest_api_user.value is not None and rest_api_user.value != "" \
    and rest_api_pass.value is not None and rest_api_pass.value != "" \
    and rest_api_url.value is not None and rest_api_url.value != "" \
    and  host_url.value is not None and host_url.value != "":

        ticketTool = None

        if rest_api_ticketing_tool.value == "ServiceNow":
            ticketTool = ServiceNow()
        
        if ticketTool != None:
            resp = ticketTool.writeBackLink(rest_api_url, rest_api_user, rest_api_pass, host_url, ticket_ref)

            if(resp.status_code == 200):
                            write_back = WriteBack(ticket_ref)
                            db.session.add(write_back)
                            db.session.commit()