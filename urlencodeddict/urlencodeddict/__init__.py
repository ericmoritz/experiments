import urllib
from urlencodeddict import helpers
import urlparse


def loads(src):
    coded_dict = urlparse.parse_qs(src)
    
    return helpers.DotExpandedDict(coded_dict)


def dumps(doc):
    pass
