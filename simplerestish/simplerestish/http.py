from restish.http import *

# Add these to the standard http restish function
def updated(location, headers, body):
    # There is no updated response code, so we use 200 Ok with a location
    headers.append(('Location', location))
    return ok(headers, body)

def deleted(headers, body):
    # There is no response code for deleted
    return ok(headers, body)

def unsupported_media(headers, body):
    return Response("415 Unsupported Media Type", headers, body)
