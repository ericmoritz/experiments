LogStream
==========

This is a WSGI application that uses gevent to asynchronously stream a
file over HTTP.  It's intended purpose is to broadcast lines of log
files over HTTP to multiple clients.

Usage
------

Easy, create a new python module called mylogstream.py

  from logstream.app import LogStream

  application = LogStream("/var/log/apache2/access.log")

Then launch it using `gunicorn`_::

  gunicorn -k gevent mylogstream

.. _gunicorn: http://gunicorn.org/
