import webob
from webobentity.formatters import DEFAULT_FORMATTERS
from webob import exc
from webob.request import NoDefault
import os


class UnknownFormat(Exception):
    def __init__(self, content_type):
        self.content_type = content_type
        super(UnknownFormat, self).__init__("Unknown Format: %s"\
                                                % content_type)

class RequestUBodyProperty(property):
    def __init__(self):
        super(RequestUBodyProperty, self).__init__(self.fget, self.fset, self.fdel)

    def fget(self, obj):
        """
        Get/set the unicode value of the body (using the charset of the Content-Type)
        """
        if not obj.charset or obj.charset == NoDefault:
            raise AttributeError(
                "You cannot access Response.unicode_body unless charset is set")

        body = obj.body
        return body.decode(obj.charset, obj.unicode_errors)

    def fset(self, obj, value):
        if not obj.charset or obj.charset is NoDefault:
            raise AttributeError(
                "You cannot access Response.unicode_body unless charset is set")
        if not isinstance(value, unicode):
            raise TypeError(
                "You can only set Response.unicode_body to a unicode string (not %s)" % type(value))
        obj.body = value.encode(obj.charset)


class RequestDataProperty(property):
    def __init__(self, formatters=DEFAULT_FORMATTERS):
        self.formatters = formatters
        super(RequestDataProperty, self).__init__(self.fget, self.fset)
        
    def fget(self, obj):
        unicode_body = RequestUBodyProperty()

        assert obj.content_type in self.formatters,\
            "Can't read content type: %s" % (obj.content_type, )
            
        try:
            formatter = self.formatters[obj.content_type]
        except KeyError:
            raise UnknownFormat(obj.content_type)

        return formatter.loads(unicode_body.fget(obj))

    def fset(self, obj, doc):
        unicode_body = RequestUBodyProperty()

        assert obj.content_type in self.formatters,\
            "Can't format content type: %s" % (obj.content_type, )
            
        try:
            formatter = self.formatters[obj.content_type]
        except KeyError:
            raise UnknownFormat(obj.content_type)

        unicode_body.fset(obj, formatter.dumps(doc))

class ResponseDataProperty(property):
    def __init__(self, formatters=DEFAULT_FORMATTERS):
        self.formatters = formatters
        super(ResponseDataProperty, self).__init__(self.fget, self.fset)

    def fget(self, obj):
        try:
            formatter = self.formatters[obj.content_type]
        except KeyError:
            raise UnknownFormat(obj.content_type)

        return formatter.loads(obj.unicode_body)

    def fset(self, obj, doc):
        # if we have no request, attempt to use the provided content_type
        if obj.request is None:
            content_type = obj.content_type
        # otherwise guess the appropriate content_type based on the 
        # Accept header
        else:
            # Get the first match for the supported formatters.
            # future implementations could use a quality value
            offers = self.formatters.keys()
            offers.append(None)

            content_type = obj.request.accept.first_match(offers)

        try:
            formatter = self.formatters[content_type]
        except KeyError, e:
            raise exc.HTTPNotAcceptable(content_type)

        obj.content_type = content_type
        obj.unicode_body = formatter.dumps(doc)


class RequestMixIn(object):
    data = RequestDataProperty()
    ubody = unicode_body = RequestUBodyProperty()


class ResponseMixIn(object):
    data = ResponseDataProperty()


# Create sub-classes of the webob Request and Response objects
class Request(RequestMixIn, webob.Request):
    pass

class Response(ResponseMixIn, webob.Response):
    pass
