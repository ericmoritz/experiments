The goal of this experiment is to produce a RESTful framework that allows any
resource to be templated using a template engine as well as expose the
underlining document using some kind of serialization method.  What format that
will be returned is solely determined by the client's Accept header.

Currently everything is designed in terms of `restish`, this dependency my be
removed and the only dependency will be `webob`

Goals
======

* Simplified Resource class
* Simplified REST based Responses
* Generic serialization of returned dictionaries into response entity body
* Automatic deserialization request entity bodies
* If the client accepts HTML/XHTML, allow templating
* Allow transformation of the document for HTML rendering
* The browser is a REST client


Simplifed Recource class
-------------------------
HTTP methods map to the generic verbs: read, write, delete, and append.  Let's
abstract the HTTP methods away to make REST super easy.

read(): dict
  This maps to GET

write(doc): restish.http.Response
  This maps to PUT
    
append(doc): restish.http.Response
  This maps to POST
    
delete(): restish.http.Response
  This maps to DELETE

Tada, there's our simple Resource class.   We no longer need to worry about 
what GET/POST/PUT/DELETE needs to do.


Simplifed Response values
--------------------------
HTTP has a standard response for CREATED, however there is no standard for
UPDATED, DELETED and APPEND.  Let's created standard responses for those.

http.updated(): restish.http.Response
    Returns a 200 OK with a Location header
    
http.appended(): restish.http.Response
   Returns a 200 OK with a Location header
    
http.deleted(): restish.http.Response
   Returns a 200 OK

Generic serialization of returned dictionaries
-----------------------------------------------
HTTP has a standard mechanism to determine what format the client wants the
data in.  It is called the `Accept` header.  Let's use the Accept header to 
serialize the value returned by read()


Automatic deserialization of request entity bodies
---------------------------------------------------
HTTP has a standard mechanism to determine the format of the request entity. It
is called, the `Content-Type` header.  Let's automatically deserialize request
entities so that write() and append() are given dictionaries instead of encoded
strings.

Content-Type also has a `charset` property. Let's use that to automatically
decode the request entity body into unicode so that our inputs are no longer
bytes.


If the client accepts HTML/XHTML, allow templating
---------------------------------------------------
If the client accepts HTML/XHTML, allow templating using the standard restish
templating mechanism.


The browser is a REST client
-----------------------------
Assuming the client is authorized, The browser should be able to
append data to a resource using a HTML form POST or write data using a
an AJAX PUT.
