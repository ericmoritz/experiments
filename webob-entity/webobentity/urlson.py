"""This provides a json like interface to Ian Bicking's
formencode.variabledecode module"""

from formencode import variabledecode
import urllib, urlparse

def flatten_multidict(qs):
    data = {}
    for k, v in urlparse.parse_qsl(qs):
        yield k, v[0]

def utf8_encode(val):
    """This only call encode on unicode objects. It passes anything
else through"""
    if type(val) is unicode:
        return val.encode("utf-8")
    else:
        return val

def dumps(data):
    dotted_dict = variabledecode.variable_encode(data)

    # Convert all the keys to utf-8 because urllib can't handle
    # unicode without puking on non-ascii chars
    utf8_dict = dict((utf8_encode(k), utf8_encode(v))\
                         for k,v in data.iteritems())

    # urllib always creates ASCII, it is its nature
    return urllib.urlencode(utf8_dict)

def loads(qs):
    dotted_dict = dict(flatten_multidict(qs))
    return variabledecode.variable_decode(dotted_dict)

