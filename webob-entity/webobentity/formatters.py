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
    
try:
    import json


    class SafeJSON(object):
        def loads(self, body):
            # Make sure the body is unicode.  It's not my job to know the
            # encoding.
            assert type(body) is unicode
            return json.loads(body)

        def dumps(self, doc):
            # This may fail if something in the doc is a string that's not
            # utf-8. Make sure all strings are unicode
            # default allows 
            return json.dumps(doc, default=unicode).decode("utf-8")

    DEFAULT_FORMATTERS['application/json'] = SafeJSON()

except ImportError:
    pass
