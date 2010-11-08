Comparison of Caching methods
==============================

This is an experiment to demonstrate how using HTTP/1.1 caching and a
caching proxy server fair exceeds the capabilities of caching inside
the application layer.


Hypothesis
-----------

External HTTP/1.1 caching will out perform caching within the
application layer

Methodology
------------

I created a new Ubuntu 10.10 256MB server on `rackspacecloud`_. I
configured the server by running the following commands::

    apt-get update
    apt-get install git varnish python-setuptools memcached apache2-utils
    git clone git://github.com/ericmoritz/experiments.git
    cd experiments/cachecompare
    python setup.py develop
    python cachecompare/tests/test.py &> /dev/null

.. _rackspacecloud: http://www.rackspacecloud.com/cloud_hosting_products/servers/pricing

The test.py script did the following for each test case.

#. Spawned a wsgiref HTTP server for the WSGI application implementing
   a cache technique.
#. Primed the cache by prefetching the URI being tested.  The results
   are stored at results/<test case>.html to confirm the WSGI
   application is functioning properly.
#. Ran Apache Bench configured to make 1000 requests in a single
   thread
#. Dumped the results of apache bench to restuls/<test case>.ab.txt


Results
--------

Mean requests per second
~~~~~~~~~~~~~~~~~~~~~~~~~

============== =============================
Case            Requests per second          
============== =============================
varnish                              5043.22
middleware                            741.43
control                               484.01
locmem                                403.02
memcache                              358.21
============== =============================
