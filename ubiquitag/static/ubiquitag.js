/** Ubiquitag! **/
load = {};
ubiquitag_server = "http://dev.knoxpy.org:8000";

var targetDocument = document;
var targetWindow = window;

if(window.parent) { 
    var targetDocument = window.parent.document;
    var targetWindow = window.parent;
}

// dynamically load any javascript file.
load.getScript = function(filename) {
    var script = document.createElement('script')
    script.setAttribute("type","text/javascript")
    script.setAttribute("src", filename)
    if (typeof script!="undefined")
        document.getElementsByTagName("head")[0].appendChild(script)
}

load.tryReady = function(test, done) {
    // Continually polls to see if jQuery is loaded.
    if (!test()) { // if jQuery isn't loaded yet...
        setTimeout(function() { load.tryReady(test, done) }, 200); // set a timer to check again in 200 ms.
        
    } else {
      done();
    }
}

var tags = {};

function log(msg) {
    alert(msg);
}

function installjQueryPlugins() {
    jQuery.fn.addTagLink = function(pat) {
        tags[pat] = 1;

        function innerHighlight(node, pat) {
            var skip = 0;
            if (node.nodeType == 3) {
                var pos = node.data.toLowerCase().indexOf(pat);
                if (pos >= 0) {
                    var $atag = jQuery("<a>");
                    var $node = jQuery(node);

                    $atag.attr("href", ubiquitag_server + "/tag/" + pat.toLowerCase());
                    $atag.addClass("ubiquity-tag-link");
                    $atag.css("textDecoration", "none");
                    $atag.data("tag", pat);


                    var endbit = node.splitText(pos+pat.length);
    
                    $atag.html("*");

                    jQuery(node).after($atag);
                    skip = 1;
                }
            }
            else if (node.nodeType == 1 && node.childNodes && !/(script|style)/i.test(node.tagName)) {
                for (var i = 0; i < node.childNodes.length; ++i) {
                    i += innerHighlight(node.childNodes[i], pat);
                }
            }
            return skip;
        }
        return this.each(function() {
                innerHighlight(this, pat.toLowerCase());
            });
    };
    
    jQuery.fn.removeTagLink = function(tag) {
        var retval = this.find("a.ubiquity-tag-link").each(function() {
                var $this = jQuery(this);
                var $sibling = $this.prev();
                if(!tag) {
                    $this.remove();
                } else if($this.data("tag") == tag) {
                    $this.remove();
                }
                if($sibling.length && $sibling[0].replaceWholeText) {
                  $sibling[0].replaceWholeText($sibling[0].wholeText);
                }
            });
        if(tag) {
          delete tags[tag];
          }
    }
}

function installClickHandler() {
jQuery(targetDocument).find("body").mouseup(function() {
            var content = targetWindow.getSelection().toString();
            var tag = content.toLowerCase();
            if(tag != "") {
                if(tags[tag]) {
                    // Remove tag
                    var url = ubiquitag_server + "/remove?callback=?";
                    var data = {'url': targetWindow.location.toString(),
                                'tag': tag};
                    var callback = function(data) {
                        if(data.status == 'ok') {
                            var tag = data.result['tag'];
                            jQuery(targetDocument).find("body").removeTagLink(tag);
                        }
                    };
                    jQuery.getJSON(url, data, callback);

                } else {
                    // Add tag
                    var url = ubiquitag_server + "/store?callback=?";
                    var data = {'url': targetWindow.location.toString(),
                                'tag': tag,
                                'title': targetDocument.title };
                    var callback = function(data) {
                        if(data.status == 'ok') {
                            var tag = data.result.tag;
                            jQuery(targetDocument).find("body").addTagLink(tag);
                        }
                    };
                    jQuery.getJSON(url, data, callback);
                }
            }
    });
}

function loadTags() {
    jQuery.getJSON(ubiquitag_server + "/details?callback=?",
                   {'url': targetWindow.location.toString()},
                   function(data) {
                       if(data.status == 'ok') {
                           jQuery(targetDocument).contents().find("body").removeTagLink();
                           var result = data.result;
                           var tags = result.tags;
                           jQuery.each(tags, function(i) {
                                   var tag = this;
                                   jQuery(targetDocument).contents().find("body").addTagLink(tag);
                               });
                       }
                   });
}

function startUbiquitag() {
    installjQueryPlugins();
    installClickHandler();
    loadTags();
}

function main() {
    load.getScript("http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.js");
    load.tryReady(function() { return typeof jQuery != 'undefined' },
                  function() {
                      jQuery.noConflict();
                      startUbiquitag();
                  });
}

main();