from time import time
from collections import Counter

import gevent
from gevent.wsgi import WSGIServer

from app import app


class BaseDaemon(object):
    VERSION = 'unknown'
    TYPE = 'unknown'

    def __init__(self):
        self._started_at = time()
        self._stats = Counter()

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
        """Boot worker."""
        worker = gevent.spawn(self.work)
        status = gevent.spawn(self.status_greenlet)

        worker.join()
        print 'worker done:', worker.get()
        status.kill()
        print 'done.'

    def status_greenlet(self):
        app._status = self._status
        http_server = WSGIServer(('', 5000), app)
        http_server.serve_forever()

    def worker(self):
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
