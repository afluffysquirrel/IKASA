import requests
from requests.auth import HTTPBasicAuth
import json
import pandas as pd

from sentence_transformers import SentenceTransformer
import scipy.spatial
from collections import OrderedDict


def calculate_suggestions():
    print("Job: Calculating suggestions...")

    embedder = SentenceTransformer('paraphrase-mpnet-base-v2')
    closest_n = 5

    from . import db
    from .models import Config, Ticket, Article, Suggestion

    tickets = pd.read_sql_table(table_name = Ticket.__table__.name, con= db.session.connection(), index_col="id")
    articles = pd.read_sql_table(table_name = Article.__table__.name, con= db.session.connection(), index_col="id")

    articles["tags"] = articles["tags"].str.replace(",","")
    articles = articles.applymap(lambda s:s.lower() if type(s) == str else s)
    tickets = tickets.applymap(lambda s:s.lower() if type(s) == str else s)
    
    tickets['soup'] = tickets['short_description'] + " " + tickets['long_description']
    articles['soup'] = articles['title'] + " "  + articles['tags']

    corpus = []

    for index, row in articles.iterrows():

        # Remove duplicates
        row['soup'] = ' '.join(OrderedDict((w,w) for w in row['soup'].split()).keys())

        # Remove special chars
        row['soup'] = row['soup'].replace('\W', '')

        corpus.append(str(index) + ": " + row['soup'])

    corpus_embeddings = embedder.encode(corpus)

    for index, row in tickets.iterrows():

        # Remove duplicates
        row['soup'] = ' '.join(OrderedDict((w,w) for w in row['soup'].split()).keys())

        # Remove special chars
        row['soup'] = row['soup'].replace('\W', '')

        queries = [row['soup']]
        query_embeddings = embedder.encode(queries)

        for query, query_embedding in zip(queries, query_embeddings):
            distances = scipy.spatial.distance.cdist([query_embedding], corpus_embeddings, "cosine")[0]

            results = zip(range(len(distances)), distances)
            results = sorted(results, key=lambda x: x[1])

            for idx, distance in results[0:closest_n]:
                if((1-distance) >= 0.5):
                    ticket_id = row['reference'].upper()
                    query = corpus[idx].strip()
                    article_id = query.split(':')[0]

                    #print(ticket_id + " " + query + " " + str(round((1-distance),2)))
                    
                    query = Suggestion.query.filter(Suggestion.article_id==article_id, Suggestion.ticket_id==ticket_id).first()

                    if query == None:
                        new_suggestion = Suggestion(article_id, ticket_id, round((1-distance),2))
                        db.session.add(new_suggestion)
                        db.session.commit()

    print("Job: Suggestions calculated")


def extract_tickets():
    from .models import Config
    from .models import Ticket

    rest_api_ticketing_tool = Config.query.filter(Config.look_up == "rest_api_ticketing_tool").first()
    rest_api_user = Config.query.filter(Config.look_up == "rest_api_user").first()
    rest_api_pass = Config.query.filter(Config.look_up == "rest_api_pass").first()
    rest_api_url = Config.query.filter(Config.look_up == "rest_api_url").first()

    #Connection validation
    if rest_api_ticketing_tool.value is not None and rest_api_ticketing_tool.value != "" \
    and rest_api_user.value is not None and rest_api_user.value != "" \
    and rest_api_pass.value is not None and rest_api_pass.value != "" \
    and rest_api_url.value is not None and rest_api_url.value != "":

        # ServiceNow API ticket extract logic to DB
        if rest_api_ticketing_tool.value == "ServiceNow":

            print("Job: Extracting tickets from ServiceNow...")
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

                    #print(result['task_effective_number'] + " : " + result['short_description'])
                    # number
                    # sys_created_on
                    # sys_created_by
                    # short_description
                    # description

                    print("Job: Extract succesfull!")

                else:
                    print("Error: response - " + str(response.status_code))
                
            except:
                print("Error: Extracting tickets 'Check URL'")
        
        # if rest_api_ticketing_tool.value == "some_ticketing_tool"

        calculate_suggestions()

    else:
        print("Error: Missing extract credentials")