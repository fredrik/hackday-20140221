import signal
from time import time
from collections import Counter

import gevent

from status import StatusGreenlet


class Daemon(object):
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

        # wait for worker to be done.
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
