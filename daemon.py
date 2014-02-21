import logging

import gevent

logger = logging.getLogger('daemon')


class SomeDaemon(object):
    def __init__(self):
        logger.info('SomeDaemon starting.')

    def start(self):
        """Boot workers."""
        # one 'run' worker,
        # one status worker.
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
        while True:
            print 'all good.'
            gevent.sleep(2.5)

    def run(self):
        while True:
            print 'running'
            gevent.sleep(0.25)


def main():
    SomeDaemon().start()


if __name__ == '__main__':
    main()
