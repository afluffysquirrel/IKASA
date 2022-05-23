from abc import ABC, abstractmethod
from requests.auth import HTTPBasicAuth
from requests.structures import CaseInsensitiveDict
import requests

''' Abstract Ticket tool parent class '''

class AbsTicketTool(ABC):
    
    @abstractmethod
    def extract(self, rest_api_url, rest_api_user, rest_api_pass):
        """ Returns list of object type Ticket retrieved via API """
        pass

    @abstractmethod
    def writeBackLink(self, rest_api_url, rest_api_user, rest_api_pass, host_url, ticket_ref):
        """ Takes string input of a ticket ref for the ticket to be updated, returns response object from API """
        pass


''' Concrete implementations of abstract parent class '''

class ServiceNow(AbsTicketTool):

    def extract(self, rest_api_url, rest_api_user, rest_api_pass):
        from .db_models import Ticket
        url = rest_api_url.value + "/api/now/v1/table/incident?sysparm_limit=100&sysparm_query=ORDERBYDESCsys_created_on"
        tickets = []
        try:
            response = requests.get(url,auth=HTTPBasicAuth(rest_api_user.value, rest_api_pass.value))
            if str(response.status_code) == "200": 
                jsonResponse = response.json()
                for result in jsonResponse['result']:
                    # If ticket not extracted then load into DB from API JSON response
                    query = Ticket.query.filter(Ticket.reference == result['number']).first()
                    if query == None:
                        new_ticket = Ticket(
                            result['number'], #reference
                            result['sys_created_by'], #created_by
                            result['short_description'], #short_desc
                            result['description']) #long_desc
                        tickets.append(new_ticket)
            else:
                raise Exception("Ticket extract: response " + str(response.status_code))
        except:
            raise Exception("ServiceNow ticket extract failed")
        return tickets

    def writeBackLink(self, rest_api_url, rest_api_user, rest_api_pass, host_url, ticket_ref):
        from .db_models import Ticket
        url = rest_api_url.value + "/api/now/v1/table/incident?sysparm_limit=1&sysparm_query=number=" + ticket_ref
        try:
            response = requests.get(url,auth=HTTPBasicAuth(rest_api_user.value, rest_api_pass.value))
            if str(response.status_code) == "200": 
                jsonResponse = response.json()
                result = jsonResponse['result'][0]
                url = rest_api_url.value + "/api/now/table/incident/" + result['sys_id'] + "?sysparm_limit=1"
                ticket = Ticket.query.filter(Ticket.reference == ticket_ref).first()
                ticket_url = host_url.value + "/tickets/" + ticket.id
                update_text = 'Supporting documentation found, click [code]<a target=\'_blank\' href=\'' + ticket_url + '\'>here</a>[/code] to access it.'
                headers = CaseInsensitiveDict()
                headers["Accept"] = "application/json"
                headers["Content-Type"] = "application/json"
                data = "{\"work_notes\": \"" + update_text + "\"}"
                resp = requests.patch(url, headers=headers, data=data, auth=HTTPBasicAuth(rest_api_user.value, rest_api_pass.value))
                return(resp)
            else:
                raise Exception("Writeback response " + str(response.status_code))
        except:
            raise Exception("ServiceNow ticket writeback failed")