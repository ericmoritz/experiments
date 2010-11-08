from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.decorators.cache import cache_control
from django.core.cache import cache

import urllib
import json as simplejson

@cache_control(max_age=30*60)
def index(request):
    fml_endpoint = 'http://graph.facebook.com/search?q="so%20starving&type=post'
    fb_response = urllib.urlopen(fml_endpoint,).read()
    fb_data = simplejson.loads(fb_response)["data"]
    return render_to_response("index.html", {"data": fb_data})

