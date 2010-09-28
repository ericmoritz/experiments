from restish import resource
from restish.resource import _metaResource

from simplerestish import http
from simplerestish import formatters
import webob.exc
from functools import wraps

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

def make_handler(http_method):
    # This creates a new method for a Entry sub-class so that it'll call
    # Entry.{http_method}

    def methodHandler(self, request):
        # Get the super proxy
        proxy = super(self.__class__, self)

        # Get the appropriate handler for the HTTP method
        func = getattr(proxy, http_method)

        # Call the handler with the request
        return func(request)
    return methodHandler

class _metaEntry(_metaResource):
    def __new__(cls, name, bases, clsargs):
        """This is some magic that applies the resource.GET|PUT|DELETE|POST
        decorators on Entry's GET|PUT|DELETE|POST methods if the appropriate
        read|write|delete|append method existst in the child class.  It's
        really ugly and probably doesn't allow Entry sub-classes to be
        subclassed themselves"""

        # Detect if one of the bases is a Entry class
        parents = [b for b in bases if isinstance(b, _metaEntry)]

        # If a Entry parent was detected, decorate the appropriate
        # Entry methods if the appropriate read/write/delete or append
        # method was found
        if len(parents) > 0:
            method_map = {
                'read': 'GET',
                'write': 'PUT',
                'delete': 'DELETE',
                'append': 'POST',
                }
            for cls_method, http_method in method_map.items():
                if cls_method in clsargs:
                    wrapper = getattr(resource, http_method)()
                    methodHandler = make_handler(http_method)
                    clsargs[http_method] = wrapper(methodHandler)

        return _metaResource.__new__(cls, name, bases, clsargs)


class Entry(resource.Resource, BodyReadWrite):

    __metaclass__ = _metaEntry

    def __init__(self, entry_id):
        self.entry_id = entry_id
                
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

    def PUT(self, request):
        try:
            doc = self.request_entity(request)
        except NotImplementedError, e:
            return http.unsupported_media([], '')
        
        result = self.write(request, doc)
        
        return result 

    def DELETE(self, request):
        return self.delete(request)

    def POST(self, request):
        try:
            doc = self.request_entity(request)
        except NotImplementedError, e:
            return http.unsupported_media([], '')
        
        result = self.append(request, doc)
        
        return result 

def install(entry_cls):
    pass
