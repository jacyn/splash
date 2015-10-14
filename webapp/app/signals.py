from django.dispatch.dispatcher import Signal
from app import signal_handlers
import sys


#import logging
#logger = logging.getLogger(__name__)

notification_via_sms = Signal(providing_args=["frm", "to", "message", "frm_alias"])
notification_via_sms.connect(signal_handlers.notify_via_sms)
