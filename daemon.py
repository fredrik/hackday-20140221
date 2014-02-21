import random
import signal
import json
from time import time
from collections import Counter

import requests
import gevent
from gevent.wsgi import WSGIServer

from app import app


API_ADDRESS = 'http://localhost:6400'


class StatusGreenlet(gevent.Greenlet):
    """Expose `status_function` over HTTP."""

    PORT_RANGE = (9000, 9900)

    def __init__(self, status_function):
        gevent.Greenlet.__init__(self)
        self.status_function = status_function

    def __str__(self):
        return '<StatusGreenlet>'

    def _run(self):
        port = random.choice(xrange(*self.PORT_RANGE))
        print 'StatusGreenlet running: http://0.0.0.0:{}/'.format(port)
        app._status = self.status_function
        http_server = WSGIServer(('', port), app)
        http_server.serve_forever()
        print 'StatusGreenlet done.'


class BaseDaemon(object):
    VERSION = 'unknown'
    TYPE = 'unknown'

    def __init__(self):
        self._started_at = time()
        self._stats = Counter()

        gevent.signal(signal.SIGQUIT, self._shutdown)
        gevent.signal(signal.SIGINT, self._shutdown)

    def _status(self):
        """Returns a status dict."""
        return {
            'status': 'ok',
            'version': self.VERSION,
            'type': self.TYPE,
            'uptime': int(time() - self._started_at),  # seconds
            'stats': self._stats,
        }

    def run(self):
        """Spawn."""

        status = StatusGreenlet(self._status)
        status.start()

        worker = gevent.spawn(self.work)

        registration = gevent.spawn(self.registration_greenlet)
        self._deregister = None

        self.lets = [status, registration, worker]

        worker.join()
        print 'worker done:', worker.get()

        # send deregistration to tower, with timeout.
        print 'dereg.'
        gevent.spawn(self.deregister).join(timeout=2)
        print 'dereg done.'

        print 'run exits.'

    def _shutdown(self):
        print 'reaping.'
        for let in self.lets:
            if not let.ready():
                print 'forcefully killing', let
                let.kill()
            else:
                print 'already ready:', let
        print 'done reaping.'

    def registration_greenlet(self):
        """Register with the API."""
        url = '{base}/register'.format(base=API_ADDRESS)
        data = {
            'address': '',
            'type': self.TYPE,
        }
        headers = {'Content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(data), headers=headers)

        # store registration info.
        data = json.loads(response.text)
        self._secret_key = data.get('secret_key')
        self._worker_id = data.get('worker_id')

        print 'registered as worker', self._worker_id

    def deregister(self):
        if not self._worker_id:
            print "can't deregister; not registered."
            return
        url = '{}/worker/{}/deregister'.format(API_ADDRESS, self._worker_id)
        data = {'secret_key': self._secret_key}
        headers = {'Content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(data), headers=headers)

        response.raise_for_status()
        return True

    def work(self):
        """To be implemented by sub-class."""
        raise NotImplementedError()


class BaconDaemon(BaseDaemon):
    VERSION = '0.1-dev'
    TYPE = 'bacon'

    def work(self):
        print 'frying bacon.'
        while True:
            gevent.sleep(5)
            print 'batch of bacon ready.'
            self._stats['bacon_strips'] += 1


if __name__ == '__main__':
    BaconDaemon().run()
