import requests
from requests.auth import HTTPBasicAuth
import json

def extract_tickets():
    from .models import Config
    from .models import Ticket

    rest_api_ticketing_tool = Config.query.filter(Config.look_up == "rest_api_ticketing_tool").first()
    rest_api_user = Config.query.filter(Config.look_up == "rest_api_user").first()
    rest_api_pass = Config.query.filter(Config.look_up == "rest_api_pass").first()
    rest_api_url = Config.query.filter(Config.look_up == "rest_api_url").first()

    if rest_api_ticketing_tool.value is not None:

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

    else:
        print("Error: Missing extract credentials")
        