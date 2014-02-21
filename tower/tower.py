"""
'Hello, this is air traffic control.''
"""

import json

from flask import Flask
from flask import request

from worker import Worker

app = Flask('control')


# global state.
# not sure I'm supposed to do this.
databank = {
    'workers': {},
}


# TODO:
# use Flask-RESTful http://flask-restful.readthedocs.org/en/latest/


@app.route('/')
def root():
    """System information."""
    worker_data = {
        w.id: w.as_dict() for w in databank['workers'].values()
    }
    return json.dumps(worker_data)


@app.route('/worker/<worker_id>')
def worker(worker_id):
    """Information about a particular worker."""
    if not worker_id in databank['workers']:
        return json.dumps({'ok': False, 'message': 'no such worker.'})

    worker = databank['workers'][worker_id]

    return json.dumps({worker_id: worker.as_dict()})


@app.route('/register', methods=['POST'])
def register():
    """Worker registration."""
    required_keys = set(('address', 'type'))
    try:
        post_data = json.loads(request.data)
        if not set(post_data.keys()).issubset(required_keys):
            raise Exception('missing required input.')
    except:
        return json.dumps({'ok': False})

    worker = Worker(**post_data)
    databank['workers'][worker.id] = worker

    return json.dumps({
        'ok': True,
        'worker_id': worker.id,
        'secret_key': worker.secret_key
    })


@app.route('/worker/<worker_id>/deregister', methods=['POST'])
def deregister(worker_id):
    required_keys = set(('secret_key',))
    try:
        post_data = json.loads(request.data)
    except:
        return json.dumps({'ok': False})

    if not set(post_data.keys()).issubset(required_keys):
        return json.dumps({'ok': False, 'message': 'missing require input.'})

    if not worker_id in databank['workers']:
        return json.dumps({'ok': False, 'message': 'no such worker.'})

    worker = databank['workers'][worker_id]

    if not post_data['secret_key'] == worker.secret_key:
        return json.dumps({'ok': False, 'message': 'bad secret key.'})

    del databank['workers'][worker_id]

    return json.dumps({'ok': True})


if __name__ == '__main__':
    app.run('', 6400, debug=True)
