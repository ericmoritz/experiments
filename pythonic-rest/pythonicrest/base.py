from webobentity import Request, Response, UnknownFormat
from webob import exc


class PythonicREST(object):
    def __init__(self, resource_factory, allow=["GET"]):
        self.resource_factory = resource_factory
        self._allow = allow

    def key(self, req):
        """Extend this if you want to use something other than the path
        as the key"""
        return req.path

    def render_response(self, response, environ, start_response):
        """Extend this if you want to render the response is some special
        way"""
        return response(environ, start_response)

    def allow(self, req, resource, key):
        """Extend this if you want to modify the Allow header based on
        the request"""
        return self._allow + ["HEAD", "OPTION"]

    def _data(self, req, resource, key):
        if req.method in ("GET", "HEAD"):
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

    def response(self, req, resource, key):
        """Extend this if you want to manipulate the response object before
        it is rendered.  For instance, you can add a Last-Modified header, 
        a custom ETag, etc"""
        response = Response(request=req)
        
        data = None

        try:
            allowed = self.allow(req, resource, key)

            # Check the allow() value
            if req.method not in allowed:
                raise exc.HTTPMethodNotAllowed(allow=allowed)
        
            # Try to get the response, and handle the standard exceptions
            # KeyError = Not Found, ValueError = Bad Request
            try:
                data = self._data(req, resource, key)
            except KeyError, e:
                raise exc.HTTPNotFound(unicode(e))
            except ValueError, e:
                raise exc.HTTPBadRequest(unicode(e))
        except exc.WSGIHTTPException, e:
            return e

        if data is not None and not isinstance(data, Response):
                response.data = data

        return response

    def __call__(self, environ, start_response):
        resource = self.resource_factory(environ)
        
        # Pull in the Request
        req = Request(environ)

        # Get the key from the request
        key = self.key(req)
        
        # Generate the response
        response = self.response(req, resource, key)

        # Render the response
        return self.render_response(response, environ, start_response)
        
