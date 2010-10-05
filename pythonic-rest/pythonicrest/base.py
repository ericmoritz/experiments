from webobentity import Request, Response, UnknownFormat
from webob import exc

class PythonicREST(object):
    def __init__(self, resource_factory):
        self.resource_factory = resource_factory

    def key(self, req):
        return req.path

    def render_response(self, response, environ, start_response):
        return response(environ, start_response)

    def _data(self, req, resource, key):
        if req.method == "GET":
            return resource[key]
        elif req.method == "PUT":
            exists = key in resource

            try:
                resource[key] = req.data
            except UnknownFormat, e:
                # Raise an UnsupportedMediaType if we don't know how to 
                # deserialize the request body
                raise exc.HTTPUnsupportedMediaType(unicode(e))
            
            if exists:
                raise exc.HTTPNoContent()
            else:
                raise exc.HTTPCreated()
                
        elif req.method == "DELETE":
            del resource[key]

    def __call__(self, environ, start_response):
        resource = self.resource_factory(environ)

        req = Request(environ)
        response = Response(request=req)
        
        # This is a method call so that people can extend it if they want
        key = self.key(req)
        data = None

        try:
            # Try to get the response, and handle the standard exceptions
            # KeyError = Not Found, ValueError = Bad Request
            try:
                data = self._data(req, resource, key)
            except KeyError, e:
                raise exc.HTTPNotFound(unicode(e))
            except ValueError, e:
                raise exc.HTTPBadRequest(unicode(e))
        except exc.HTTPException, e:
            response = e

        if data is not None:
            response.data = data


        # This is a method call so that people can extend it if they want
        return self.render_response(response, environ, start_response)
        
