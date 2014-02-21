import logging

import gevent
from gevent.wsgi import WSGIServer

from app import app


logger = logging.getLogger('daemon')


class SomeDaemon(object):
    def __init__(self):
        logger.info('SomeDaemon starting.')

    def start(self):
        """Boot workers."""
        worker = gevent.spawn(self.run)
        status = gevent.spawn(self.status)

        while True:
            if worker.ready():
                print 'worker done.'
            if status.ready():
                print 'status done.'
            print 'zzz'
            gevent.sleep(2)

    def status(self):
        logger.info('status worker: starting.')
        http_server = WSGIServer(('', 5000), app)
        http_server.serve_forever()
        logger.info('status worker is done/dead.')

    def run(self):
        while True:
            print 'running'
            gevent.sleep(0.25)


def main():
    SomeDaemon().start()


if __name__ == '__main__':
    main()
