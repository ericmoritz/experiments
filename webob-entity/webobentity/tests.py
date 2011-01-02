import unittest
from datetime import datetime
from webobentity import *
from webob import exc
import webob
import json

class TestRequestDataProperty(unittest.TestCase):
    def test_set_json(self):
        data_prop = RequestDataProperty()
        req = webob.Request.blank("/")
        req.content_type = "application/json"
        data = {'test': 1}
        data_prop.fset(req, data)
        
        self.assertTrue(req.body, json.dumps(data))

    def test_get_json(self):
        data_prop = RequestDataProperty()
        req = webob.Request.blank("/")
        req.content_type = "application/json"
        data = {'test': 1}
        req.body = json.dumps(data)
        result = data_prop.fget(req)
        
        self.assertTrue(data, result)

    def test_set_urlencoded(self):
        data_prop = RequestDataProperty()
        req = webob.Request.blank("/")
        req.content_type = "application/x-www-form-urlencoded"
        data = {'test': 1}
        data_prop.fset(req, data)
        
        self.assertTrue(req.body, u"test=1")

    def test_get_urlencoded(self):
        data = {u"test": u"1"}
        data_prop = RequestDataProperty()
        req = webob.Request.blank("/")
        req.content_type = "application/x-www-form-urlencoded"
        req.body = "test=1"
        req.charset = "utf-8"
        result = data_prop.fget(req)
        
        self.assertTrue(data, result)


class TestResponseDataProperty(unittest.TestCase):
    def test_set_json(self):
        data_prop = ResponseDataProperty()
        req = webob.Request.blank("/")
        req.accept = "application/json"


        data = {'test': 1}
        resp = webob.Response()
        resp.request = req

        data_prop.fset(resp, data)
        
        self.assertTrue(resp.body, json.dumps(data))

    def test_get_json(self):
        data_prop = ResponseDataProperty()
        data = {'test': 1}

        resp = webob.Response()
        resp.content_type = "application/json"

        resp.body = json.dumps(data)
        result = data_prop.fget(resp)
        
        self.assertTrue(data, result)

    def test_set_urlencoded(self):
        data_prop = ResponseDataProperty()
        req = webob.Request.blank("/")
        req.accept = "application/x-www-form-urlencoded"


        data = {'test': 1}
        resp = webob.Response()
        resp.request = req

        data_prop.fset(resp, data)
        expect = u"test=1"
        self.assertTrue(resp.body, expect)

    def test_get_urlencoded(self):
        data_prop = ResponseDataProperty()
        data = {'test': 1}

        resp = webob.Response()
        resp.content_type = "application/x-www-form-urlencoded"

        resp.body = "test=1"
        resp.charset = "utf-8"
        result = data_prop.fget(resp)
        
        self.assertTrue(data, result)
        

class TestRequest(unittest.TestCase):

    def test_data_set(self):
        doc = {'test': 'simple'}

        req = Request.blank("/")
        req.content_type = "application/json"
        req.data = doc

        result = req.body
        expect = json.dumps(doc)

        self.assertEqual(expect, result)


    def test_data_get(self):
        doc = {'test': 'simple'}

        req = Request.blank("/")
        req.content_type = "application/json"
        req.body = json.dumps(doc)

        result = req.data
        expect = doc

        self.assertEqual(expect, result)

class TestResponse(unittest.TestCase):

    def test_data_set(self):


        doc = {'test': 'simple'}

        req = Request.blank("/")
        req.accept = "application/json"

        resp = Response(request=req)
        resp.data = doc

        result = resp.body
        expect = json.dumps(doc)

        self.assertEqual(expect, result)


    def test_data_get(self):
        doc = {'test': 'simple'}

        resp = Response()
        resp.content_type = "application/json"
        resp.body = json.dumps(doc)

        result = resp.data
        expect = doc

        self.assertEqual(expect, result)

    def test_data_set_request_norequest_on_ct(self):
        "No Request and Default Content Type"

        doc = {'test': 'simple'}

        # With out a content type, Response defaults
        # to text/html
        resp = Response()

        def setit():
            resp.data = doc
        
        self.assertRaises(exc.HTTPNotAcceptable, setit)


    def test_data_set_request_notacceptable(self):
        "Request without an acceptable content-type"
        doc = {'test': 'simple'}
        
        req = Request.blank("/")
        req.accept = "text/plain"

        resp = Response(request=req)

        def setit():
            resp.data = doc
        
        self.assertRaises(exc.HTTPNotAcceptable, setit)
        
    def test_data_set_norequest_unknownct(self):
        "No Request with an unknown content-type"
        doc = {'test': 'simple'}

        resp = Response(content_type='text/plain')

        def setit():
            resp.data = doc
        
        self.assertRaises(exc.HTTPNotAcceptable, setit)
        
    def test_data_get_unknown_ct(self):
        doc = {'test': 'simple'}

        resp = Response()
        resp.content_type = "text/plain"

        resp.body = json.dumps(doc)

        def getit():
            result = resp.data

        self.assertRaises(UnknownFormat, getit)


    def test_symetric(self):
        """Test that if data is set, it can then be retrieved"""
        doc = {'test': 'simple'}

        req = Request.blank("/")
        req.accept = "application/json"
        resp = Response(request=req)
        
        resp.data = doc
        result = resp.data

        self.assertEqual(doc, result)
