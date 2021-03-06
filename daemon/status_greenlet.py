import random
import json
from time import time

import requests
import gevent
from gevent.wsgi import WSGIServer
from flask import Flask


TOWER = 'http://localhost:6400'


# HTTP API
##
"""
The simple HTTP server `app` is instantiated
at a random port in `StatusGreenlet.serve`.
"""
# TODO: look at class-based views.
# TODO: error handling lets us know what's wrong.
flaskapp = Flask('worker-status')


@flaskapp.route('/')
def status():
    try:
        status = flaskapp._status()
    except:
        return json.dumps({'status': 'fail'})

    return json.dumps(status)


# Greenlet
##

class StatusGreenlet(gevent.Greenlet):
    """
    Expose vital daemon characteristics and statistics,
    for some observed object. The observed object must
    set `_started_at`, and `_stats` is assumed to be
    interesting.

    self.observed is the object of our scrutiny.
    """

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
        """
        Override `gevent.Greenlet._run`.

        Spawns a HTTP server at a random port and
        sends off a registration to control tower.
        """
        port = random.choice(xrange(*self.PORT_RANGE))
        address = 'http://localhost:{}/'.format(port)

        server = gevent.Greenlet.spawn(self.serve, port)
        register = gevent.Greenlet.spawn(self.register, address)

        print 'StatusGreenlet serving on {}'.format(address)

        register.join()
        server.join()

    def serve(self, port):
        """
        Serve status over HTTP forever.
        """
        flaskapp._status = self._status
        http_server = WSGIServer(('', port), flaskapp)
        http_server.serve_forever()

    def register(self, address):
        """Register with control tower."""
        url = '{tower}/register'.format(tower=TOWER)
        data = {
            'address': address,
            'type': self.observed.TYPE,
        }
        headers = {'Content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(data), headers=headers)

        response.raise_for_status()

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
        url = '{tower}/worker/{id}/deregister'.format(
            tower=TOWER,
            id=self._worker_id
        )
        data = {'secret_key': self._secret_key}
        headers = {'Content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(data), headers=headers)

        response.raise_for_status()

        print 'deregistered', self._worker_id
        return True
