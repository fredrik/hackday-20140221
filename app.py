import json
from flask import Flask

# the application
app = Flask(__name__)


@app.route('/')
def status():
    try:
        status = app._status()
    except Exception, e:
        print e.__class__, e
        return json.dumps({'status': 'fail'})

    return json.dumps(status)
