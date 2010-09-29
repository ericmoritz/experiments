import webob
from webobentity.formatters import DEFAULT_FORMATTERS
from webob import exc
from webob.request import NoDefault

class UnknownFormat(Exception):
    def __init__(self, content_type):
        self.content_type = content_type
        super(UnknownFormat, self).__init__("Unknown Format: %s"\
                                                % content_type)

class RequestMixIn(object):
    formatters = DEFAULT_FORMATTERS

    def _data__get(self):
        assert self.content_type in self.formatters,\
            "Can't read content type: %s" % (self.content_type, )
            
        try:
            formatter = self.formatters[self.content_type]
        except KeyError:
            raise UnknownFormat(self.content_type)

        return formatter.loads(self.unicode_body)
        

    def _data__set(self, doc):
        assert self.content_type in self.formatters,\
            "Can't format content type: %s" % (self.content_type, )
            
        try:
            formatter = self.formatters[self.content_type]
        except KeyError:
            raise UnknownFormat(self.content_type)

        self.unicode_body = formatter.dumps(doc)
    
    data = property(_data__get, _data__set)


    def _unicode_body__get(self):
        """
        Get/set the unicode value of the body (using the charset of the Content-Type)
        """
        if not self.charset or self.charset == NoDefault:
            raise AttributeError(
                "You cannot access Response.unicode_body unless charset is set")

        body = self.body
        return body.decode(self.charset, self.unicode_errors)

    def _unicode_body__set(self, value):
        if not self.charset or self.charset is NoDefault:
            raise AttributeError(
                "You cannot access Response.unicode_body unless charset is set")
        if not isinstance(value, unicode):
            raise TypeError(
                "You can only set Response.unicode_body to a unicode string (not %s)" % type(value))
        self.body = value.encode(self.charset)

    def _unicode_body__del(self):
        del self.body

    unicode_body = property(_unicode_body__get, _unicode_body__set, _unicode_body__del, doc=_unicode_body__get.__doc__)
    ubody = property(_unicode_body__get, _unicode_body__set, _unicode_body__del, doc="Alias for unicode_body")


class ResponseMixIn(object):
    formatters = DEFAULT_FORMATTERS

    def _data__get(self):
        try:
            formatter = self.formatters[self.content_type]
        except KeyError:
            raise UnknownFormat(self.content_type)

        return formatter.loads(self.unicode_body)

    def _data__set(self, doc):
        # if we have no request, attempt to use the provided content_type
        if self.request is None:
            content_type = self.content_type
        # otherwise guess the appropriate content_type based on the 
        # Accept header
        else:
            # Get the first match for the supported formatters.
            # future implementations could use a quality value
            offers = self.formatters.keys()
            offers.append(None)

            content_type = self.request.accept.first_match(offers)

        try:
            formatter = self.formatters[content_type]
        except KeyError, e:
            raise exc.HTTPNotAcceptable(content_type)

        self.content_type = content_type
        self.unicode_body = formatter.dumps(doc)
        
    data = property(_data__get, _data__set)


# Create sub-classes of the webob Request and Response objects
class Request(RequestMixIn, webob.Request):
    pass

class Response(ResponseMixIn, webob.Response):
    pass
