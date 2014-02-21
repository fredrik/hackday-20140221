from time import time
from collections import Counter

import gevent
from gevent.wsgi import WSGIServer

from app import app


class SomeDaemon(object):
    VERSION = '0.1'

    def __init__(self):
        self._started_at = time()
        self._stats = Counter()

    def _status(self):
        """Returns a status dict."""
        return {
            'status': 'ok',
            'version': self.VERSION,
            'uptime': int(time() - self._started_at),  # seconds
            'stats': self._stats,
        }

    def run(self):
        """Boot workers."""
        worker = gevent.spawn(self.worker)
        status = gevent.spawn(self.status_worker)

        worker.join()
        print 'worker done:', worker.get()
        status.kill()
        print 'done.'

    def status_worker(self):
        app._status = self._status
        http_server = WSGIServer(('', 5000), app)
        http_server.serve_forever()

    def worker(self):
        while True:
            print 'work work'
            self._stats['units'] += 1
            gevent.sleep(0.25)
        return 32


def main():
    SomeDaemon().run()


if __name__ == '__main__':
    main()
