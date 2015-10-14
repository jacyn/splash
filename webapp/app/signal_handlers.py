from django.conf import settings
from time import gmtime, strftime

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.mail import send_mail

from backend.sms import Messaging

import logging
logger = logging.getLogger(__name__)

import sys

def notify_via_sms(sender, frm, to, message, frm_alias, **kwargs):
    
    messaging = Messaging()
    response = messaging.send(frm, to, message, frm_alias)

    success = 1
    errors = None
    if response.status_code != 202:
        success = 0
        errors = dict()

        for name in [ 'x-devnet-apiclient-authenticated', 'x-client-error', 'x-client-error-detail', 'x-server-error', 'x-server-error-detail', ]:
            if response.headers.get(name):
                errors[name] = response.headers.get(name, None)

    response = dict(
        msisdn=to,
        sender=frm,
        sender_alias=frm_alias,
        success=success,
        errors=errors,
        status_code=response.status_code,
    )    

    return response

