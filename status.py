import random
import json
from time import time

import requests
import gevent
from gevent.wsgi import WSGIServer

from app import app


API_ADDRESS = 'http://localhost:6400'


class StatusGreenlet(gevent.Greenlet):
    """Expose `status_function` over HTTP."""

    PORT_RANGE = (9000, 9900)

    def __init__(self, observed):
        gevent.Greenlet.__init__(self)
        self.observed = observed

    def __str__(self):
        return '<StatusGreenlet>'

    def _status(self):
        """Returns a status dict."""
        return {
            'status': 'ok',
            'version': self.observed.VERSION,
            'type': self.observed.TYPE,
            'uptime': int(time() - self.observed._started_at),  # seconds
            'stats': self.observed._stats,
        }

    def _run(self):
        port = random.choice(xrange(*self.PORT_RANGE))
        address = 'http://localhost:{}/'.format(port)

        server = gevent.Greenlet.spawn(self.serve, port)
        register = gevent.Greenlet.spawn(self.register, address)

        print 'StatusGreenlet serving on {}/'.format(address)

        register.join()
        server.join()

    def serve(self, port):
        app._status = self._status
        http_server = WSGIServer(('', port), app)
        http_server.serve_forever()

    def register(self, address):
        """Register with control tower."""
        url = '{base}/register'.format(base=API_ADDRESS)
        data = {
            'address': address,
            'type': self.observed.TYPE,
        }
        headers = {'Content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(data), headers=headers)

        # store registration info.
        data = json.loads(response.text)
        self._secret_key = data.get('secret_key')
        self._worker_id = data.get('worker_id')

        print 'registered as worker', self._worker_id
        return True

    def deregister(self):
        """Deregister with control tower."""
        if not self._worker_id:
            print "can't deregister; not registered."
            return
        url = '{}/worker/{}/deregister'.format(API_ADDRESS, self._worker_id)
        data = {'secret_key': self._secret_key}
        headers = {'Content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(data), headers=headers)

        response.raise_for_status()
        print 'deregistered', self._worker_id
        return True
