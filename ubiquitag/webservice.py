from flask import (Flask, url_for, render_template, request, json)
import pymongo
from functools import wraps
from time import time

app = Flask(__name__)
app.config.from_object("ubiquitag.default_settings")


con = pymongo.Connection(**app.config['MONGO_CONNECTION'])
db = getattr(con, app.config['MONGO_DATABASE'])
coll = getattr(db, app.config['MONGO_COLLECTION'])

@app.context_processor
def add_time():
    return {'time': time}

def jsonp_response(jsonp_arg="callback"):
    def decor(func):
        @wraps(func)
        def inner(*args, **kwargs):
            callback = request.args.get(jsonp_arg)
            result = func(*args, **kwargs)

            jsonstr = json.dumps(result)

            if callback:
                return "%s(%s)" % (callback, jsonstr)
            else:
                return jsonstr
        return inner
    return decor


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/demo")
def demo():
    return render_template("demo.html")

@app.route("/tag/<tag>")
def tag(tag):
    tag = tag.lower().strip()
    c = coll.find({'tags': tag})
    
    return render_template("tag.html",
                           cursor=c,
                           tag=tag)

@app.route("/details")
@jsonp_response()
def details():
    url = request.args.get('url')

    if url:
        doc = coll.find_one({'url': url})
        if(doc):
            del doc['_id']
            return {'status': 'ok',
                    'result': doc }
        else:
            return {'status': 'not found'}
    else:
        return {'status': 'param "url" required'}

@app.route("/remove")
@jsonp_response()
def remove():
    url = request.args.get('url')
    tag = request.args.get('tag')
    
    if(url and tag):
        coll.update({'url': url},
                    {'$pull': {'tags': tag}})
        return {'status': 'ok', 'result': {'tag': tag}}
    else:
        return {
            'status': 'URL args "url" and "tag" required'
            }

@app.route("/store")
@jsonp_response()
def store():
    url = request.args.get('url')
    tag = request.args.get('tag')
    title = request.args.get('title')

    if url and tag:
        tag = tag.lower().strip()
        url = url.lower().strip()

        # Check for the existance of a document
        count = coll.find({'url': url}).count()

        # If the document exists, append the tag
        # to the document's tags value if the tag
        # isn't already there
        if count > 0:
            coll.update({'url': url,
                         'tags': {"$ne": tag}},
                        {'$push': {'tags': tag},
                         '$set': {'title': title}})
        else:
            # otherwise insert a new document
            coll.insert({'url': url, 'title': title, 'tags': [tag]})

        return {
            'status': 'ok',
            'result': {'tag': tag}
            }
    else:
        return {
            'status': "expected params 'url' and 'tag'"
            }

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)
