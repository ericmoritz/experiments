from logstream.follow import Follow
import gevent
from gevent.queue import Queue
import logging
from webob import Request, Response, exc
from webob.dec import wsgify

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class LogStream(object):

    def __init__(self, fname):
        """
        Creates a new LogStream WSGI callable
        This also automatically spawns the Follow job

        :param fname: The filename to watch
        :var follow: The Follow instance
        :var job: The gevent job instance
        """

        # This creates a new Follow coroutine for the lifespan of the
        # LogStream WSGI application instance
        self.follow = Follow(fname)
        self.job = gevent.spawn(self.follow)

    # We use webob because frankly the interface is much nicer than raw-WSGI
    @wsgify
    def __call__(self, request):
        # LogStream WSGI app
        # -------------------
        #
        # Process request
        # ~~~~~~~~~~~~~~~~
        #
        #
        # Guard against non-GET methods.  The world won't come to an end if we
        # don't do this, but it's nice to let clients know what they're allowed
        # to do with your resource
        if request.method != "GET":
            return exc.HTTPMethodNotAllowed(allow=["GET"])
        #
        # Create a queue to use for this request
        queue = Queue()
        #
        # Create the WSGI response 
        # ~~~~~~~~~~~~~~~~~~~~~~~~~
        #
        # Subscribe this queue to the follow greenlet
        self.follow.queues.append(queue)
        #
        # Define a app_iter factory that will generate the lines that are
        # inserted into the queue by the follow job
        def make_app_iter():
            while True:
                line = queue.get()
                yield line
        #
        # Return the response with a new app_iter
        return Response(app_iter=make_app_iter())
