import unittest
from datetime import datetime
from webobentity import Request, Response, UnknownFormat
from webob import exc
import json


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
