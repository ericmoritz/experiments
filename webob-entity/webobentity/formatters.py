DEFAULT_FORMATTERS = {}

# Formatters need to support loads/dumps

"""
This defines some formatters as well as default formatters

The Formatter interface is as follows:

class Formatter(object):
    def loads(self, body):
        assert type(body) is unicode

        raise NotImplementError()

    def dumps(self, body):
        raise NotImplementError()

"""
import logging
log = logging.getLogger(__name__)
    
try:
    import json

    class SafeJSON(object):
        extensions = ["json"]
        def loads(self, body):
            # Make sure the body is unicode.  It's not my job to know the
            # encoding.
            assert type(body) is unicode
            return json.loads(body)

        def dumps(self, doc):
            # This should always produce dictionary with unicode chars.
            # If the doc has values that are not utf-8, this will blow up.
            # Again, it's not my job to know the encoding.
            return json.dumps(doc, default=unicode)

    DEFAULT_FORMATTERS['application/json'] = SafeJSON()

except ImportError:
    pass

try:
    from webobentity import urlson

    class URLSON(object):
        extensions = [] # There's no extension

        def loads(self, qs):
            # Make sure the body is unicode.  It's not my job to know the
            # encoding.
            assert type(qs) is unicode
            return urlson.loads(qs)

        def dumps(self, doc):
            # This returns a tuple to because urlson always dumps ASCII that
            # is percent encoded utf-8.
            return urlson.dumps(doc)

    DEFAULT_FORMATTERS['application/x-www-form-urlencoded'] = URLSON()
except ImportError:
    pass

def extension_type(extension, formatters=DEFAULT_FORMATTERS):
    "Search the formatters by extension"
    for k, v in DEFAULT_FORMATTERS.items():
        if extension in v.extensions:
            return k
