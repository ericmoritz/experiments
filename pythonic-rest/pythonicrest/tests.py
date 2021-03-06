from collections import MutableMapping
from pythonicrest import PythonicREST
import unittest
from webob import Request
import json


# This is our Blog resource.  We could theorically just use standard
# dictionary, but I want to illustrate how to build a custom pythonic Resource
class Blog(MutableMapping):
    def __init__(self, db):
        self.db = db

    def __getitem__(self, key):
        # KeyErrors equate to a HTTP 404
        return self.db[key]

    def __setitem__(self, key, value):
        if key == "/i-cant-find-this":
            raise KeyError(key)

        if "title" in value and "body" in value:
            self.db[key] = value
        else:
            raise ValueError("title and body are required.")

    def __delitem__(self, key):
        del self.db[key]

    def __contains__(self, key):
        return key in self.db

    def __iter__(self):
        return self.db.__iter__()

    def __len__(self):
        return self.db.__len__()

def blog_factory(environ):
    # It's up to the factory to determine what key to use to instantiate
    # the resource
    url = environ['PATH_INFO']

    # Our db is stuffed in the environ prior to the request
    # This is done by the unittest code and not the framework
    db = environ['db']

    # Our little example only has one blog so we're only using one DB
    # normally we would use the URL to instantiate a certain subset of 
    # the DB.  For instance if there was a Section resource
    return Blog(db)


class BlogDBBase(unittest.TestCase):
    def setUp(self):
        self.db = {}
        self.db['/simple-blog-post'] = {'title': u"This is a simple post",
                                        'body': u"This is the blog body"}
        self.app = PythonicREST(blog_factory,
                                allow=["GET", "PUT", "DELETE"])
        

class TestBlogGET(BlogDBBase):

    def test_valid(self):
        req = Request.blank("/simple-blog-post")
        req.environ['db'] = self.db
        req.accept = "application/json"

        response = req.get_response(self.app)

        self.assertEqual("200 OK", response.status)
        data = json.loads(response.body)

        expect = self.db['/simple-blog-post']
        result = data
        self.assertEqual(expect, result)


    def test_notfound(self):
        req = Request.blank("/not-found")
        req.environ['db'] = self.db
        req.accept = "application/json"

        response = req.get_response(self.app)

        expect = "404 Not Found"
        result = response.status
        

class TestBlogPUT(BlogDBBase):

    def test_create(self):
        req = Request.blank("/this-is-new")
        req.environ['db'] = self.db

        req.method = "PUT"
        req.content_type = "application/json"
        
        req.body = json.dumps({'title': u"This is a new entry",
                    'body': u"This is a new body"})
        resp = req.get_response(self.app)
        
        self.assertEqual("201 Created", resp.status)

    def test_update(self):
        req = Request.blank("/simple-blog-post")
        req.environ['db'] = self.db

        req.method = "PUT"
        req.content_type = "application/json"
        req.body = json.dumps({'title': u"I updated your title!",
                    'body': u"I updated you body!"})

        resp = req.get_response(self.app)
        
        self.assertEqual("204 No Content", resp.status)

    def test_notfound(self):
        # This is a special slug in my Blog resource that always throws
        # a KeyError
        req = Request.blank("/i-cant-find-this")
        req.environ['db'] = self.db

        req.method = "PUT"
        req.content_type = "application/json"
        req.body = json.dumps({'title': u"This is a new entry",
                    'body': u"This is a new body"})

        resp = req.get_response(self.app)
        
        self.assertEqual("404 Not Found", resp.status)

    def test_invalid(self):
        req = Request.blank("/simple-blog-post")
        req.environ['db'] = self.db

        req.method = "PUT"
        req.content_type = "application/json"

        # Try to send invalid data
        req.body = json.dumps({})

        resp = req.get_response(self.app)
        
        self.assertEqual("400 Bad Request", resp.status)


class TestBlogDELETE(BlogDBBase):

    def test_delete(self):
        req = Request.blank("/simple-blog-post")
        req.environ['db'] = self.db
        req.method = "DELETE"

        resp = req.get_response(self.app)
        self.assertEqual("200 OK", resp.status)

        resp = req.get_response(self.app)
        self.assertEqual("404 Not Found", resp.status)

    def test_not_found(self):
        req = Request.blank("/nowhere-man")
        req.environ['db'] = self.db
        req.method = "DELETE"

        resp = req.get_response(self.app)
        self.assertEqual("404 Not Found", resp.status)


class TestBlogPOST(BlogDBBase):
    def test_notallowed(self):
        req = Request.blank("/")
        req.method = "POST"
        req.environ['db'] = self.db

        req.body = json.dumps({'title': u"This is a new item...",
                               'body': u"This is a new body..."})

        resp = req.get_response(self.app)
        
        self.assertEqual("405 Method Not Allowed", resp.status)
        self.assertEqual(("GET", "PUT", "DELETE", "HEAD", "OPTION"),
                         resp.allow)

                       
class TestBlogHEAD(BlogDBBase):
    
    def test_valid(self):
        req = Request.blank("/simple-blog-post")
        req.method = "HEAD"
        req.accept = "application/json"
        req.environ['db'] = self.db

        response = req.get_response(self.app)

        self.assertEqual("200 OK", response.status)

    def test_notfound(self):
        req = Request.blank("/not-found")
        req.method = "HEAD"
        req.accept = "application/json"

        req.environ['db'] = self.db

        response = req.get_response(self.app)

        expect = "404 Not Found"
        result = response.status

                       
class TestBlogOPTION(BlogDBBase):
    
    def test_valid(self):
        req = Request.blank("/simple-blog-post")
        req.method = "OPTION"
        req.environ['db'] = self.db

        response = req.get_response(self.app)

        self.assertEqual("200 OK", response.status)
        self.assertEqual(("GET", "PUT", "DELETE", "HEAD", "OPTION"),
                         response.allow)

    def test_notfound(self):
        req = Request.blank("/not-found")
        req.method = "OPTION"

        req.environ['db'] = self.db

        response = req.get_response(self.app)

        expect = "404 Not Found"
        result = response.status

