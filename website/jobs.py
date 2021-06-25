import requests
from requests.auth import HTTPBasicAuth

def extract_tickets():
    from .models import Config
    from .models import Ticket

    rest_api_ticketing_tool = Config.query.filter(Config.look_up == "rest_api_ticketing_tool").first()
    rest_api_user = Config.query.filter(Config.look_up == "rest_api_user").first()
    rest_api_pass = Config.query.filter(Config.look_up == "rest_api_pass").first()
    rest_api_url = Config.query.filter(Config.look_up == "rest_api_url").first()

    if rest_api_ticketing_tool.value is not None:
        if rest_api_ticketing_tool.value == "ServiceNow":
            print("Job: Extracting tickets from ServiceNow")
            url = rest_api_url.value + "/api/now/table/incident?sysparm_query=sys_updated_on%3Ejavascript%3Ags.beginningOfLast1500Minutes()&sysparm_limit=10"
            response = requests.get(url,auth=HTTPBasicAuth(rest_api_user.value, rest_api_pass.value))
            print("Response: " + str(response.status_code))
    else:
        print("Error: Missing extract credentials")
        