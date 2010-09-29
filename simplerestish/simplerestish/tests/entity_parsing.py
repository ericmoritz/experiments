import unittest

from wsgientityparse import entity
from webob import Request


class TestRequest(unitest.TestCase):
    def test_content_type(self):
        req = Request.blank("/")
        
