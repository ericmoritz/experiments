import unittest
from restish import resource
from restish.app import RestishApp
import simplerestish
from simplerestish import http
from webob import Request
import json


class Root(resource.Resource):
    @resource.child()
    def samples(self, request, segments):
        return SampleCollection("")


class SampleCollection(simplerestish.Entry):
    def _db(self, request):
        return request.environ['unittest.db']

    def read(self, request): # Read from the collection
        db = self._db(request)

        # We must return a dictionary, returning JSON lists are bad
        return {'entry_ids': db['samples'].keys()}

    def write(self, request, collection):
        db = self._db(request)
        db['samples'] = collection
        uri = "/samples"
        return http.updated(uri, [], '')

    def delete(self, request):
        db = self._db(request)
        db['samples'] = {}
        return http.deleted([], '')

    def append(self, request, doc):
        db = self._db(request)
        size = len(db['samples'].keys())
        new_key = "sample-%s" % (size+1)
        db['samples'][new_key] = doc
        uri = "/samples/%s" % (new_key, )
        return http.created(uri,  [], '')

    @resource.child("{entry_id}")
    def sample(self, request, segments, entry_id):
        return SampleEntry(entry_id)


class SampleEntry(simplerestish.Entry):
    def _db(self, request):
        return request.environ['unittest.db']

    def read(self, request):
        db = self._db(request)

        if self.entry_id in db['samples']:
            return db['samples'][self.entry_id]
        else:
            return None # Does not exist.

    def write(self, request, doc):
        db = self._db(request)
        uri = "/samples/%s" % (self.entry_id)
        if self.entry_id in db['samples']:
            # Update
            db['samples'][self.entry_id] = doc
            return http.updated(uri, [], '')
        else:
            # Create
            db['samples'][self.entry_id] = doc
            return http.created(uri, [], '')

    def delete(self, request):
        db = self._db(request)

        if self.entry_id in db['samples']:
            del db['samples'][self.entry_id]
            return http.deleted([], '')
        else:
            return http.not_found([], '')


class NothingResource(simplerestish.Entry):
    """This resource implements nothing"""
    pass

class DBMiddleware(object):
    def __init__(self, application):
        self.application = application
        self.db ={
            'samples': {
                'sample-1': {'name': 'Sample 1'}
                }
            }

    def __call__(self, environ, start_response):
        environ['unittest.db'] = self.db
        return self.application(environ, start_response)


class CollectionTestCase(unittest.TestCase):
    def setUp(self):
        app = RestishApp(Root())
        db_middleware = DBMiddleware(app)

        self.db = db_middleware.db
        self.app = db_middleware

    def test_read(self):
        req = Request.blank("/samples")

        resp = req.get_response(self.app)
        self.assertEqual(resp.status, "200 OK")

        expect = {'entry_ids': ['sample-1']}
        result = json.loads(resp.body)
        
        self.assertEqual(expect, result)

    def test_read_not_acceptable(self):
        req = Request.blank("/samples")
        req.accept = "text/plain"

        resp = req.get_response(self.app)
        self.assertEqual(resp.status, "406 Not Acceptable")

    def test_write(self):
        req = Request.blank("/samples")
        req.method = "PUT" # PUT replaces the entire collection
        req.body = json.dumps({'sample-3': {'name': 'Sample 3'}})
        req.content_type = "application/json"

        resp = req.get_response(self.app)
        self.assertEqual(resp.status, "200 OK")
        self.assertEqual(resp.headers['Location'], "/samples")

        # Write should have change the entire collection to the req.body

        result = self.db['samples']
        expect = {'sample-3': {'name': 'Sample 3'}}
        
        self.assertEqual(expect, result)

    def test_write_bad_content_type(self):
        req = Request.blank("/samples")
        req.method = "PUT" # PUT replaces the entire collection
        req.body = json.dumps({'sample-3': {'name': 'Sample 3'}})
        req.content_type = "text/plain"

        resp = req.get_response(self.app)
        self.assertEqual(resp.status, "415 Unsupported Media Type")


    def test_delete(self):
        req = Request.blank("/samples")
        req.method = "DELETE" # PUT replaces the entire collection

        resp = req.get_response(self.app)
        self.assertEqual(resp.status, "200 OK")

        # Write should have change the entire collection to the req.body
        expect = {}
        result = self.db['samples']
        self.assertEqual(expect, result)


    def test_append(self):
        req = Request.blank("/samples")
        req.method = "POST" # POST appends an entry onto the collection
        req.body = json.dumps({'name': 'Sample 2'})
        req.content_type = "application/json"

        resp = req.get_response(self.app)
        self.assertEqual(resp.status, "201 Created")
        self.assertEqual(resp.headers['Location'], "/samples/sample-2")

    def test_append_bad_content_type(self):
        req = Request.blank("/samples")
        req.method = "POST" # PUT replaces the entire collection
        req.body = json.dumps({'name': 'Sample 2'})
        req.content_type = "text/plain"

        resp = req.get_response(self.app)
        self.assertEqual(resp.status, "415 Unsupported Media Type")


class EntryTestCase(unittest.TestCase):
    def setUp(self):
        app = RestishApp(Root())
        db_middleware = DBMiddleware(app)

        self.db = db_middleware.db
        self.app = db_middleware

    def test_read(self):
        req = Request.blank("/samples/sample-1")

        resp = req.get_response(self.app)
        self.assertEqual(resp.status, "200 OK")

        expect = {'name': 'Sample 1'}
        result = json.loads(resp.body)
        
        self.assertEqual(expect, result)

    def test_write(self):
        # Test creation
        req = Request.blank("/samples/sample-2")
        req.method = "PUT"
        req.content_type = "application/json"
        req.body = json.dumps({'name': 'Sample 2'})

        resp = req.get_response(self.app)
        self.assertEqual(resp.status, "201 Created")
        self.assertEqual(resp.headers['Location'], '/samples/sample-2')
        
        expect = {'name' : 'Sample 2'}
        result = self.db['samples']['sample-2']
        self.assertEqual(expect, result)

        # Test update
        req = Request.blank("/samples/sample-2")
        req.method = "PUT"
        req.content_type = "application/json"
        req.body = json.dumps({'name': 'Sample 2.1'})

        resp = req.get_response(self.app)
        self.assertEqual(resp.status, "200 OK")
        self.assertEqual(resp.headers['Location'], '/samples/sample-2')

        expect = {'name' : 'Sample 2.1'}
        result = self.db['samples']['sample-2']
        self.assertEqual(expect, result)


    def test_delete(self):
        # Test delete
        req = Request.blank("/samples/sample-1")
        req.method = "DELETE"

        resp = req.get_response(self.app)
        self.assertEqual(resp.status, "200 OK")

        # Test repeated delete
        req = Request.blank("/samples/sample-1")
        req.method = "DELETE"
        resp = req.get_response(self.app)
        self.assertEqual(resp.status, "404 Not Found")


class TestNotImplemented(unittest.TestCase):
    def setUp(self):
        self.app = RestishApp(NothingResource(""))

    def test_not_implemented(self):
        for method in ["GET", "POST", "DELETE", "PUT"]:
            req = Request.blank("/")
            req.method = method
            resp = req.get_response(self.app)
            
            self.assertEqual(resp.status, "405 Method Not Allowed")

        
