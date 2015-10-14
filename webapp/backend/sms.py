from django.conf import settings
from datetime import datetime
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
import dateutil.tz
import json
import urllib
import requests

class Messaging(object):

    def send(self, frm, to, message, frm_alias=None, usagetype=None):
        if usagetype is None:
            usagetype = self.usagetype
        
        request_date = str(datetime.now().replace(microsecond=0, tzinfo=self.LOCAL_TIMEZONE).isoformat('T'))
        request_body= {
            "from": frm,
            "from_alias": frm_alias,
            "to": to,
            "content_type": "text/plain",
            "body": message,
            "date": request_date,
            "usagetype": usagetype,
        }

        request_data = json.dumps(request_body)
        response = requests.post(
            self.url.get("messaging"), data=request_data, 
            auth=HTTPBasicAuth(self.user, self.pswd), headers=self.headers)

        return response


    def __init__(self):
        super(Messaging, self).__init__()

        self.user = settings.XDN_MESSAGING_API_USER
        self.pswd = settings.XDN_MESSAGING_API_PSWD
        self.usagetype = settings.XDN_MESSAGING_API_USAGETYPE

        self.url = {}
        self.url['messaging'] = settings.XDN_MESSAGING_API_URL
        self.LOCAL_TIMEZONE = dateutil.tz.tzlocal()

        self.headers = { 
            "Content-Type" : settings.XDN_MESSAGING_API_CONTENT_TYPE 
        }
