"""
Usage:
    try:
        import json
    except ImportError, ie:
        from django.utils import simplejson as json

    from webapp import jsonhandler

    ...
    jsonstr = json.dumps(my_data_struct, default=jsonhandler.polymorphic_handler)
"""


#a list of tuples: (type, func)
REGISTRY = [ ]

def polymorphic_handler(obj):
    found = False
    val = None
    for ri in REGISTRY:
        typ, func = ri
        if isinstance(obj, typ):
            found = True
            val = func(obj)
            break

    if found:
        return val
    raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj))


# Practical example: add support for datetime serialization
from datetime import datetime, date
import isodate

REGISTRY.append( (datetime, lambda o: isodate.datetime_isoformat(o)) )
REGISTRY.append( (date, lambda o: isodate.date_isoformat(o)) )

# add Decimal support
import decimal
REGISTRY.append( (decimal.Decimal, lambda o: str(o)) )



