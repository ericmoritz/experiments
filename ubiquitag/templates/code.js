var _if = document.createElement('iframe');
document.body.appendChild(_if);
var _ifd = _if.contentDocument;
var _s = _ifd.createElement('script');
_s.src = 'http://dev.knoxpy.org:8000{{ url_for("static", filename="ubiquitag.js") }}?v={{ time() }}';
_ifd.body.appendChild(_s);
