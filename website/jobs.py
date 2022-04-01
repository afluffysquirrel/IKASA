import requests
import pandas as pd
import scipy.spatial

from collections import OrderedDict
from requests.auth import HTTPBasicAuth
from requests.structures import CaseInsensitiveDict
from sentence_transformers import SentenceTransformer
from datetime import datetime


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
    sensitivity = 0.3

    from . import db
    from .models import Article, Suggestion, WriteBack

    # Read last 100 tickets from DB
    tickets = pd.read_sql_query("select * from Ticket order by created_on desc limit 100;", con = db.session.connection())
    
    #Read all articles from DB
    articles = pd.read_sql_table(table_name = Article.__table__.name, con = db.session.connection(), index_col="id")

    # Pre-format data for the model
    articles["tags"] = articles["tags"].str.replace(",","")
    articles = articles.applymap(lambda s:s.lower() if type(s) == str else s)
    tickets = tickets.applymap(lambda s:s.lower() if type(s) == str else s)
    
    # Collect data used by model into 'soup'
    tickets['soup'] = tickets['short_description'] + " " + tickets['long_description']
    articles['soup'] = articles['title'] + " " + articles['tags']
    #articles['soup'] = articles['title'] + " " + articles['body'] + " " + articles['tags']

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

                    print(ticket_ref + " " + article_id + " " + str(query) + " " + str(round((1-distance),2)))
                    
                    # Checking suggestion doesnt already exist
                    query = Suggestion.query.filter(Suggestion.article_id==article_id, Suggestion.ticket_ref==ticket_ref).first()

                    if query == None:
                        # Adding suggestion to DB
                        new_suggestion = Suggestion(article_id, ticket_ref, round((1-distance),2))
                        db.session.add(new_suggestion)
                        db.session.commit()
                        suggestionFlag = True
        
        # If suggestions calculated check db to see if write back done previously
        # In event no writeback has been previously done use rest API to add comment 
        if(suggestionFlag == True):
            query = WriteBack.query.filter(WriteBack.ticket_ref==ticket_ref).first()
            if query == None:
                write_back_API(ticket_ref)

    console_log('Suggestions calculated', '')


def extract_tickets():
    from .models import Config
    from .models import Ticket

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

        # ServiceNow API ticket extract logic to DB
        if rest_api_ticketing_tool.value == "ServiceNow":

            console_log('Extracting tickets from ServiceNow...', '')
            url = rest_api_url.value + "/api/now/v1/table/incident?sysparm_limit=100&sysparm_query=ORDERBYDESCsys_created_on"
            
            try:
                response = requests.get(url,auth=HTTPBasicAuth(rest_api_user.value, rest_api_pass.value))
                if str(response.status_code) == "200": 

                    jsonResponse = response.json()

                    from . import db
                    s = db.session()

                    for result in jsonResponse['result']:
                        # If ticket not extracted then load into DB from API JSON response
                        query = Ticket.query.filter(Ticket.reference == result['number']).first()
                        if query == None:
                            new_ticket = Ticket(
                                result['number'], 
                                result['sys_created_by'],
                                result['short_description'],
                                result['description'])
                            s.add(new_ticket)
                            s.commit()

                    console_log('Extract succesfull', '')

                else:
                    console_log("Response - " + str(response.status_code), 'error')
                
            except:
                console_log("Extracting tickets 'Check URL'", 'error')
        
        # if rest_api_ticketing_tool.value == "some_ticketing_tool"

    else:
        #print("Error: Missing extract credentials")
        console_log("Missing extract credentials", 'error')


def write_back_API(ticket_ref):

    from .models import Config
    from .models import Ticket

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

        # ServiceNow API ticket extract logic to DB
        if rest_api_ticketing_tool.value == "ServiceNow":

            url = rest_api_url.value + "/api/now/v1/table/incident?sysparm_limit=1&sysparm_query=number=" + ticket_ref

            try:
                response = requests.get(url,auth=HTTPBasicAuth(rest_api_user.value, rest_api_pass.value))
                if str(response.status_code) == "200": 

                    jsonResponse = response.json()

                    for result in jsonResponse['result']:

                        url = rest_api_url.value + "/api/now/table/incident/" + result['sys_id'] + "?sysparm_limit=1"

                        ticket = Ticket.query.filter(Ticket.reference == ticket_ref).first()

                        ticket_url = host_url.value + "/tickets/" + ticket.id
                        update_text = 'Supporting documentation found, click [code]<a target=\'_blank\' href=\'' + ticket_url + '\'>here</a>[/code] to access it.'

                        headers = CaseInsensitiveDict()
                        headers["Accept"] = "application/json"
                        headers["Content-Type"] = "application/json"

                        data = "{\"work_notes\": \"" + update_text + "\"}"

                        resp = requests.patch(url, headers=headers, data=data, auth=HTTPBasicAuth(rest_api_user.value, rest_api_pass.value))
                 
                else:
                    console_log("Response - " + str(response.status_code), 'error')

            except:
                console_log("Write back failed", 'error')