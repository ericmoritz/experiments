
class JSONFormatter(object):
    def dumps(self, doc):
        import json
        return json.dumps(doc, default=unicode)
                                     
    def loads(self, body):
        import json
        assert type(body) is unicode
        return json.loads(body)



