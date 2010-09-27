from restish import resource
from simplerestish import http
from simplerestish import formatters
import webob.exc

class BodyReadWrite(object):
    formatters = {
        'application/json': formatters.JSONFormatter()
        }

    def request_entity(self, request):
        # Make sure the request entity is an allowed formattor
        ct = request.content_type
        charset = request.charset or "utf-8"

        if ct not in self.formatters.keys():
            raise NotImplementedError()

        ubody = request.body.decode(charset)
        doc = self.formatters[ct].loads(ubody)
        return doc

    def response_entity(self, request, doc):
        offers = self.formatters.keys()

        # Makes the accept.first_match return None if nothing is found
        offers.append(None)
        
        # Find the first match for the offers
        mimetype = request.accept.first_match(offers)

        if mimetype is None:
            raise NotImplementedError()

        return mimetype, self.formatters[mimetype].dumps(doc)


class EntryInterface(object):

    # Entry methods
    def read(self, request):
        raise NotImplementedError()

    def write(self, request):
        raise NotImplementedError()

    def delete(self, request):
        raise NotImplementedError()

    # Collection methods
    def list(self, request):
        raise NotImplementedError()

    def append(self, request, doc):
        raise NotImplementedError()



class Entry(resource.Resource, BodyReadWrite, EntryInterface):
    def __init__(self, entry_id):
        self.entry_id = entry_id

    @resource.GET()
    def GET(self, request):
        doc = self.read(request)
        if doc is not None:
            try:
                mimetype, body = self.response_entity(request, doc)
                return http.ok([('Content-Type', mimetype),], body)
            except NotImplementedError, e:
                return http.not_acceptable([],'')
        else:
            return http.not_found()

    @resource.PUT()
    def PUT(self, request):
        try:
            doc = self.request_entity(request)
        except NotImplementedError, e:
            return http.unsupported_media([], '')
        
        result = self.write(request, doc)
        
        return result 

    @resource.DELETE()
    def DELETE(self, request):
        return self.delete(request)

    @resource.POST()
    def POST(self, request):
        try:
            doc = self.request_entity(request)
        except NotImplementedError, e:
            return http.unsupported_media([], '')
        
        result = self.append(request, doc)
        
        return result 

