import urllib
from urlson import helpers
import urlparse

def parse_qs(src):
    """This custom parse_qs will only create
a list value if there are multiple keys in the querystring"""
    coded_dict = {}
    for key, value in urlparse.parse_qsl(src):
        # If the current key is in the dict
        if key in coded_dict:
            if type(coded_dict[key]) is list:
                coded_dict[key].append(value)
            else:
                coded_dict[key] = [coded_dict[key], value]
        else:
            coded_dict[key] = value
    return coded_dict

def loads(src):
    coded_dict = parse_qs(src)
    return helpers.DotExpandedDict(coded_dict)


def dumps(doc):
    return urllib.urlencode(list(helpers.flatten_lists(doc)))
