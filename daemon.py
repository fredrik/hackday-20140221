import signal
from time import time
from collections import Counter

import gevent

from status import StatusGreenlet


class BaseDaemon(object):
    VERSION = 'unknown'
    TYPE = 'unknown'

    def __init__(self):
        self._started_at = time()
        self._stats = Counter()

        gevent.signal(signal.SIGQUIT, self._shutdown)
        gevent.signal(signal.SIGINT, self._shutdown)

    def run(self):
        """Spawn status and worker greenlets."""

        # the main reason we're here.
        worker = gevent.spawn(self.work)

        # expose a status service over http.
        status = StatusGreenlet(self)
        status.start()

        # keep track of greenlets so that we can shut them down.
        self.greenlets = [status, worker]

        worker.join()

        # send deregistration to tower, with timeout.
        gevent.spawn(status.deregister).join(timeout=2)

        print 'exit.'

    def _shutdown(self):
        for greenlet in self.greenlets:
            if not greenlet.ready():
                greenlet.kill()

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
