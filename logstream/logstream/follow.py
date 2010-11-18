import re
import gevent
from gevent.queue import Queue
import logging

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class Follow(object):
    def __init__(self, fname):
        self.line = None
        self.queues = []
        self.fname = fname

    def __call__(self):
        log.info("Opening %s" % (self.fname, ))
        with file(self.fname) as fh:
            fh.seek(0,2)
            while True:
                l = fh.readline()
                if not l:
                    gevent.sleep(0.1)
                else:
                    self.line = l
                    for queue in self.queues:
                        log.debug(l)
                        queue.put(l)

def printer(queue):
    while True:
        print queue.get().strip()

if __name__ == "__main__":
    follow = Follow("/var/log/messages")
    f = gevent.spawn(follow)

    q = Queue()
    follow.queues.append(q)
    gevent.spawn(printer, q)

    q = Queue()
    follow.queues.append(q)
    gevent.spawn(printer, q)

    while True:
        gevent.sleep(0.01)
